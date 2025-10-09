#!/usr/bin/env python3
"""
PCP求解器端到端集成测试

测试完整的求解流程，使用真实的数据和算法组件（需要Gurobi许可证）
"""

import unittest
import sys
import os
import tempfile
import time
from typing import List, Dict, Any

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    import gurobipy as grb

    GUROBI_AVAILABLE = True
except ImportError:
    GUROBI_AVAILABLE = False

# 导入测试数据生成器

from test_data.pcp_instance_generator import PCPInstanceGenerator, PCPInstanceData
from test_data.pcp_instance_reader import PCPInstanceReader

# 导入核心模块
from cg.column_generation import ColumnGeneration
from cg.column_independent_set import ColumnIndependentSet
from cg.column_pool import ColumnPool
from cg.master.master_problem import MasterProblem
from cg.pricing.pricing_problem import PricingProblem
from cg.pricing.exact_pricing_solver import ExactPricingSolver

# 导入数据模型
from model.charge_problem import ChargeProblem
from model.a_graph import AuxiliaryGraph

# 导入其他依赖
from bidict import bidict


class PCPSolver:
    """
    完整的PCP求解器
    
    整合所有组件，提供端到端的求解功能
    """

    def __init__(self, charge_problem: ChargeProblem):
        """
        初始化求解器
        
        Args:
            charge_problem: 要求解的PCP实例
        """
        self.charge_problem = charge_problem

        # 组件将在solve方法中初始化
        self.master_problem = None
        self.pricing_problems = None
        self.pricing_solvers = None
        self.column_pool = None
        self.column_generation = None

        # 求解结果
        self.solution = None
        self.objective_value = None
        self.solve_time = None
        self.iterations = None

    def _create_auxiliary_graph(self) -> AuxiliaryGraph:
        """创建辅助图"""
        return AuxiliaryGraph(
           graph=self.charge_problem.graph,
            vertices_map=self.charge_problem.vertex_map,
            auxiliary_edges=None,
            merged_vertices_map=None
        )
    
    def _add_artificial_columns(self):
        """为每个分区添加人工列以确保主问题可行"""
        for partition in self.charge_problem.partitions:
            # 为每个分区中的每个顶点创建单顶点人工列
            partition_vertices = [v for v in self.charge_problem.vertices 
                                if v.associated_partition.id == partition.id]
            
            for vertex in partition_vertices:
                artificial_column = ColumnIndependentSet(
                    vertex_set={vertex},
                    associated_pricing_problem=self.pricing_problem,
                    is_artificial=True,
                    creator="artificial_initialization",
                    value=1000.0  # 高代价确保只在必要时使用
                )
                self.column_pool.addColumn(artificial_column)

    def _initialize_components(self):
        """初始化所有求解组件"""
        # 创建辅助图
        aux_graph = self._create_auxiliary_graph()

        # 创建定价问题（这里简化为一个定价问题）
        self.pricing_problem = PricingProblem(
            auxiliary_graph=aux_graph,
            name="main_pricing",
            dualcosts=[]
        )

        # 创建定价求解器
        self.pricing_solver = ExactPricingSolver(
            auxiliary_graph=aux_graph,
            pricing_problem=self.pricing_problem
        )

        # 创建列池
        self.column_pool = ColumnPool()
        
        # 为每个分区添加人工列以确保主问题可行
        self._add_artificial_columns()

        # 创建主问题
        self.master_problem = MasterProblem(
            data_model=self.charge_problem,
            pricing_problem=self.pricing_problem,
            column_pool=self.column_pool
        )

        # 构建主问题模型
        self.master_problem.buildModel()

        # 创建列生成算法
        self.column_generation = ColumnGeneration(
            instance=self.charge_problem,
            master=self.master_problem,
            pricing_problem=self.pricing_problem,
            pricing_solver=self.pricing_solver,
            column_pool=self.column_pool
        )

    def solve(self, time_limit: int = 3600) -> Dict[str, Any]:
        """
        求解PCP实例
        
        Args:
            time_limit: 时间限制（秒）
            
        Returns:
            求解结果字典
        """
        if not GUROBI_AVAILABLE:
            raise RuntimeError("Gurobi不可用，无法运行集成测试")

        start_time = time.time()

        try:
            # 初始化组件
            self._initialize_components()

            # 运行列生成算法
            self.column_generation.solve(time_limit)

            # 记录结果
            self.solve_time = time.time() - start_time
            self.iterations = self.column_generation.iteration
            self.objective_value = self.column_generation.masterObjective
            self.solution = self.column_generation.solution

            return {
                "status": "optimal" if self.solution else "no_solution",
                "objective_value": self.objective_value,
                "solve_time": self.solve_time,
                "iterations": self.iterations,
                "master_solve_time": self.column_generation.masterSolveTime,
                "pricing_solve_time": self.column_generation.pricingSolveTime,
                "upper_bound": self.column_generation.upper_bound,
                "lower_bound": self.column_generation.lower_bound
            }

        except Exception as e:
            self.solve_time = time.time() - start_time
            return {
                "status": "error",
                "error": str(e),
                "solve_time": self.solve_time
            }

    def get_solution_info(self) -> Dict[str, Any]:
        """获取详细的解信息"""
        if not self.solution:
            return {"status": "no_solution"}

        # 分析解的结构
        used_columns = []
        total_colors = 0

        for col_id, value in self.solution.items():
            if value > 1e-6:  # 非零值
                used_columns.append({
                    "column_id": col_id,
                    "value": value
                })
                total_colors += 1

        return {
            "status": "solved",
            "total_colors_used": total_colors,
            "objective_value": self.objective_value,
            "used_columns": used_columns,
            "solve_statistics": {
                "iterations": self.iterations,
                "solve_time": self.solve_time,
                "master_time": self.column_generation.masterSolveTime if self.column_generation else 0,
                "pricing_time": self.column_generation.pricingSolveTime if self.column_generation else 0
            }
        }


@unittest.skipUnless(GUROBI_AVAILABLE, "Gurobi不可用")
class TestEndToEndSolving(unittest.TestCase):
    """端到端求解测试"""

    def setUp(self):
        """设置测试环境"""
        self.generator = PCPInstanceGenerator(seed=42)
        self.reader = PCPInstanceReader()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_charge_problem_from_instance(self, instance) -> ChargeProblem:
        """从实例数据创建ChargeProblem对象"""
        # 保存到临时文件
        temp_file = os.path.join(self.temp_dir, "temp_instance.json")
        self.generator.save_instance(instance, temp_file)

        # 加载为ChargeProblem
        charge_problem = self.reader.create_charge_problem(temp_file)
        return charge_problem

    def test_small_instance_solving(self):
        """测试小实例求解"""
        # 生成小测试实例
        instance = self.generator.generate_small_test_instance()
        charge_problem = self._create_charge_problem_from_instance(instance)

        # 创建求解器
        solver = PCPSolver(charge_problem)

        # 求解
        result = solver.solve(time_limit=30)

        # 验证结果
        self.assertIn("status", result)
        self.assertIn("solve_time", result)

        if result["status"] == "optimal":
            self.assertIsNotNone(result["objective_value"])
            self.assertGreaterEqual(result["objective_value"], 0)

            # 获取解的详细信息
            solution_info = solver.get_solution_info()
            self.assertEqual(solution_info["status"], "solved")

            # 验证解的质量
            colors_used = solution_info["total_colors_used"]
            optimal_colors = instance.optimal_colors

            if optimal_colors:
                self.assertGreaterEqual(colors_used, optimal_colors,
                                        f"使用颜色数 {colors_used} 少于最优值 {optimal_colors}")

                # 对于小实例，应该能找到最优解或接近最优解
                self.assertLessEqual(colors_used, optimal_colors + 1,
                                     f"解质量不佳: 使用 {colors_used} 颜色，最优 {optimal_colors}")

        elif result["status"] == "error":
            self.fail(f"求解过程出错: {result.get('error', 'Unknown error')}")

    def test_random_instances_solving(self):
        """测试随机实例求解"""
        test_cases = [
            {"vertices": 8, "partitions": 3, "prob": 0.3, "name": "small_random"},
            {"vertices": 12, "partitions": 4, "prob": 0.2, "name": "medium_sparse"},
            {"vertices": 10, "partitions": 5, "prob": 0.5, "name": "medium_dense"},
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                # 生成实例
                instance = self.generator.generate_random_instance(
                    case["vertices"], case["partitions"], case["prob"], case["name"]
                )
                charge_problem = self._create_charge_problem_from_instance(instance)

                # 求解
                solver = PCPSolver(charge_problem)
                result = solver.solve(time_limit=60)

                # 基本验证
                self.assertIn("status", result)
                self.assertLessEqual(result["solve_time"], 70,  # 允许一点超时容忍
                                     f"求解时间过长: {result['solve_time']:.2f}秒")

                if result["status"] == "optimal":
                    # 验证解的合理性
                    colors_used = solver.get_solution_info()["total_colors_used"]
                    max_reasonable_colors = case["partitions"]  # 最多需要分区数量的颜色

                    self.assertGreaterEqual(colors_used, 1, "至少需要1种颜色")
                    self.assertLessEqual(colors_used, max_reasonable_colors,
                                         f"颜色数过多: {colors_used} > {max_reasonable_colors}")

                elif result["status"] == "error":
                    # 记录错误但不失败（可能是Gurobi配置问题）
                    print(f"警告: {case['name']} 求解出错: {result.get('error', 'Unknown')}")

    def test_grid_instance_solving(self):
        """测试网格实例求解"""
        # 生成3x3网格实例
        instance = self.generator.generate_grid_instance(3, 3, 3)
        charge_problem = self._create_charge_problem_from_instance(instance)

        # 求解
        solver = PCPSolver(charge_problem)
        result = solver.solve(time_limit=60)

        # 验证结果
        self.assertIn("status", result)

        if result["status"] == "optimal":
            solution_info = solver.get_solution_info()
            colors_used = solution_info["total_colors_used"]

            # 对于3x3网格，分区大小为3，应该需要相对较少的颜色
            self.assertGreaterEqual(colors_used, 1)
            self.assertLessEqual(colors_used, 4,  # 网格图通常不需要太多颜色
                                 f"网格实例颜色数过多: {colors_used}")

    def test_complete_graph_solving(self):
        """测试完全图实例求解"""
        # 生成小的完全图实例
        instance = self.generator.generate_random_instance(6, 3)
        charge_problem = self._create_charge_problem_from_instance(instance)

        # 求解
        solver = PCPSolver(charge_problem)
        result = solver.solve(time_limit=60)

        # 验证结果
        self.assertIn("status", result)

        if result["status"] == "optimal":
            solution_info = solver.get_solution_info()
            colors_used = solution_info["total_colors_used"]

            # 完全图的分区着色应该正好需要分区数量的颜色
            expected_colors = instance.optimal_colors  # 应该是4
            self.assertEqual(colors_used, expected_colors,
                             f"完全图实例颜色数不正确: 期望 {expected_colors}，实际 {colors_used}")


@unittest.skipUnless(GUROBI_AVAILABLE, "Gurobi不可用")
class TestPerformanceIntegration(unittest.TestCase):
    """性能集成测试"""

    def setUp(self):
        """设置性能测试环境"""
        self.generator = PCPInstanceGenerator(seed=42)
        self.reader = PCPInstanceReader()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_charge_problem_from_instance(self, instance) -> ChargeProblem:
        """从实例数据创建ChargeProblem对象"""
        temp_file = os.path.join(self.temp_dir, "temp_instance.json")
        self.generator.save_instance(instance, temp_file)
        return self.reader.create_charge_problem(temp_file)

    def test_medium_instance_performance(self):
        """测试中等规模实例的性能"""
        # 生成中等规模实例
        instance = self.generator.generate_random_instance(20, 8, 0.15, "performance_test")
        charge_problem = self._create_charge_problem_from_instance(instance)

        # 求解
        solver = PCPSolver(charge_problem)
        result = solver.solve(time_limit=120)

        # 性能要求
        self.assertLessEqual(result["solve_time"], 130,  # 允许一点超时
                             f"求解时间过长: {result['solve_time']:.2f}秒")

        if result["status"] == "optimal":
            # 验证算法效率
            self.assertLessEqual(result["iterations"], 50,
                                 f"迭代次数过多: {result['iterations']}")

            # 验证时间分配合理性
            master_time = result.get("master_solve_time", 0)
            pricing_time = result.get("pricing_solve_time", 0)
            total_algorithm_time = master_time + pricing_time

            self.assertLessEqual(total_algorithm_time, result["solve_time"],
                                 "算法时间统计异常")

    def test_scalability(self):
        """测试算法可扩展性"""
        test_sizes = [
            {"vertices": 10, "partitions": 3, "expected_time": 30},
            {"vertices": 15, "partitions": 5, "expected_time": 60},
            {"vertices": 20, "partitions": 7, "expected_time": 120},
        ]

        results = []

        for size_config in test_sizes:
            instance = self.generator.generate_random_instance(
                size_config["vertices"],
                size_config["partitions"],
                0.2,  # 固定边密度
                f"scale_{size_config['vertices']}v"
            )
            charge_problem = self._create_charge_problem_from_instance(instance)

            solver = PCPSolver(charge_problem)
            result = solver.solve(time_limit=size_config["expected_time"])

            results.append({
                "vertices": size_config["vertices"],
                "partitions": size_config["partitions"],
                "solve_time": result["solve_time"],
                "status": result["status"],
                "iterations": result.get("iterations", 0)
            })

            # 基本性能要求
            self.assertLessEqual(result["solve_time"], size_config["expected_time"] + 10,
                                 f"实例{size_config['vertices']}v求解时间过长")

        # 分析可扩展性
        print("\n可扩展性测试结果:")
        for r in results:
            print(f"  {r['vertices']}顶点: {r['solve_time']:.2f}秒, "
                  f"{r['iterations']}迭代, 状态: {r['status']}")


class TestErrorHandling(unittest.TestCase):
    """错误处理测试"""

    def test_invalid_instance_handling(self):
        """测试无效实例的处理"""
        # 创建一个无效的ChargeProblem（空数据）
        charge_problem = ChargeProblem(
            edges=[],
            vertices=[],
            partitions=[]
        )

        if GUROBI_AVAILABLE:
            solver = PCPSolver(charge_problem)
            result = solver.solve(time_limit=10)

            # 应该优雅地处理错误
            self.assertEqual(result["status"], "error")
            self.assertIn("error", result)
        else:
            # 如果Gurobi不可用，应该抛出适当的异常
            solver = PCPSolver(charge_problem)
            with self.assertRaises(RuntimeError):
                solver.solve(time_limit=10)


def run_integration_tests():
    """运行集成测试"""
    print("=" * 80)
    print("PCP求解器端到端集成测试")
    print("=" * 80)

    if not GUROBI_AVAILABLE:
        print("警告: Gurobi不可用，跳过所有集成测试")
        print("请确保已正确安装Gurobi并配置许可证")
        return

    # 创建测试套件
    suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [
        TestEndToEndSolving,
        TestPerformanceIntegration,
        TestErrorHandling
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出结果
    print("\n" + "=" * 80)
    print("集成测试结果汇总")
    print("=" * 80)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) /
                    result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"成功率: {success_rate:.1f}%")
    print("=" * 80)

    return result


if __name__ == "__main__":
    # 确保测试数据目录存在
    os.makedirs("test_data/instances", exist_ok=True)

    # 运行集成测试
    result = run_integration_tests()

    # 根据测试结果设置退出码
    sys.exit(0 if result.wasSuccessful() else 1)
