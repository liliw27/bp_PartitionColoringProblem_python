import sys
import os
# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.charge_problem import ChargeProblem
from cg.column_independent_set import ColumnIndependentSet
from cg.column_pool import ColumnPool
from cg.master.master_problem import MasterProblem
from cg.pricing.pricing_problem import PricingProblem
from cg.pricing.exact_pricing_solver import ExactPricingSolver
from cg.column_generation import ColumnGeneration
from model.a_graph import AuxiliaryGraph
from typing import Dict, Any
import time
from test_data.pcp_instance_generator import PCPInstanceGenerator
from test_data.pcp_instance_reader import PCPInstanceReader

try:
    import gurobipy as grb
    GUROBI_AVAILABLE = True
except ImportError:
    GUROBI_AVAILABLE = False

class CGSolver:
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
        
    def _create_charge_problem_from_instance(self, instance) -> ChargeProblem:
        """从实例数据创建ChargeProblem对象"""
        # 保存到临时文件
        temp_file = os.path.join(self.temp_dir, "temp_instance.json")
        self.generator.save_instance(instance, temp_file)

        # 加载为ChargeProblem
        charge_problem = self.reader.create_charge_problem(temp_file)
        return charge_problem
    
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
    
    def update_graph(self, a_graph: AuxiliaryGraph) -> None:
        self.pricing_problem.auxiliary_graph = a_graph
        self.pricing_solver.auxiliary_graph = a_graph
        
    def update_column_pool(self, column_pool: ColumnPool) -> None:
        self.column_pool = column_pool
        self.master_problem.column_pool = column_pool

if __name__ == "__main__":
    
    # 创建测试实例生成器和读取器
    generator = PCPInstanceGenerator(seed=42)
    reader = PCPInstanceReader()
    
    # 创建临时目录用于存储实例文件
    import os
    import tempfile
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 定义测试用例
        test_cases = [
            {"vertices": 8, "partitions": 3, "prob": 0.3, "name": "small_random"},
            {"vertices": 12, "partitions": 4, "prob": 0.2, "name": "medium_sparse"}, 
            {"vertices": 10, "partitions": 5, "prob": 0.5, "name": "medium_dense"},
        ]

        # 运行测试用例
        for case in test_cases:
            print(f"\n求解实例: {case['name']}")
            
            # 生成实例
            instance = generator.generate_random_instance(
                case["vertices"], case["partitions"], case["prob"], case["name"]
            )
            
            # 保存实例到临时文件
            temp_file = os.path.join(temp_dir, f"{case['name']}.json")
            generator.save_instance(instance, temp_file)
            
            # 读取实例并创建问题
            charge_problem = reader.create_charge_problem(temp_file)
            
            # 求解
            solver = CGSolver(charge_problem)
            result = solver.solve(time_limit=300)
            
            # 输出结果
            if result["status"] == "optimal":
                solution_info = solver.get_solution_info()
                print(f"求解成功:")
                print(f"- 使用颜色数: {solution_info['total_colors_used']}")
                print(f"- 目标值: {solution_info['objective_value']:.2f}")
                print(f"- 求解时间: {solution_info['solve_statistics']['solve_time']:.2f}秒")
            else:
                print(f"求解失败: {result['status']}")
                
    finally:
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)