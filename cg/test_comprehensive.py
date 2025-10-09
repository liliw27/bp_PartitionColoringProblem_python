#!/usr/bin/env python3
"""
PCP求解器的全面测试套件

包含以下测试模块：
1. 单元测试：测试各个组件的独立功能
2. 集成测试：测试组件间的协作
3. 端到端测试：测试完整的求解流程
4. 性能测试：测试算法性能
5. 边界情况测试：测试极端情况的处理
"""

import unittest
import sys
import os
import time
import tempfile
from unittest.mock import Mock, MagicMock, patch
from typing import List, Dict, Any

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

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
from model.vertex import Vertex
from model.edge import Edge
from model.partition import Partition
# from model.charger import Charger  # 已移除
from model.a_graph import AuxiliaryGraph
from config import Config

# 导入其他依赖
from bidict import bidict


class TestDataModel(unittest.TestCase):
    """测试数据模型类"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建基本的测试数据
        self.partitions = [
            Partition(0, {0, 1}),
            Partition(1, {2, 3}),
            Partition(2, {4, 5})
        ]
        
        self.vertices = [
            Vertex(0, "v0", set(), self.partitions[0]),
            Vertex(1, "v1", set(), self.partitions[0]),
            Vertex(2, "v2", set(), self.partitions[1]),
            Vertex(3, "v3", set(), self.partitions[1]),
            Vertex(4, "v4", set(), self.partitions[2]),
            Vertex(5, "v5", set(), self.partitions[2])
        ]
        
        self.edges = [
            Edge(self.vertices[0], self.vertices[2], 1.0),  # 分区间边
            Edge(self.vertices[1], self.vertices[3], 1.0),  # 分区间边
            Edge(self.vertices[2], self.vertices[4], 1.0),  # 分区间边
        ]
        
        # 更新邻接关系
        for edge in self.edges:
            edge.source.add_adjacent_vertex(edge.target)
            edge.target.add_adjacent_vertex(edge.source)
        
        self.charge_problem = ChargeProblem(
            edges=self.edges,
            vertices=self.vertices,
            partitions=self.partitions
        )
    
    def test_charge_problem_initialization(self):
        """测试ChargeProblem初始化"""
        self.assertEqual(len(self.charge_problem.vertices), 6)
        self.assertEqual(len(self.charge_problem.edges), 3)
        self.assertEqual(len(self.charge_problem.partitions), 3)
# self.assertEqual(len(self.charge_problem.chargers), 3)  # 已移除chargers
        
        # 测试查找表构建
        self.assertIsNotNone(self.charge_problem.vertex_map)
        self.assertIsNotNone(self.charge_problem.partition_map)
# self.assertIsNotNone(self.charge_problem.charger_map)  # 已移除chargers
    
    def test_charge_problem_statistics(self):
        """测试统计信息计算"""
        stats = self.charge_problem.get_statistics()
        
        self.assertEqual(stats["num_vertices"], 6)
        self.assertEqual(stats["num_edges"], 3)
        self.assertEqual(stats["num_partitions"], 3)
        self.assertEqual(stats["num_inter_partition_edges"], 3)  # 所有边都是分区间边
        self.assertEqual(stats["num_intra_partition_edges"], 0)
        self.assertEqual(stats["avg_partition_size"], 2.0)
    
    def test_charge_problem_validation(self):
        """测试数据验证"""
        errors = self.charge_problem.validate()
        self.assertEqual(len(errors), 0, f"验证失败: {errors}")
    
    def test_vertex_operations(self):
        """测试顶点相关操作"""
        vertex = self.charge_problem.get_vertex_by_id(0)
        self.assertIsNotNone(vertex)
        self.assertEqual(vertex.id, 0)
        
        # 测试邻接关系
        self.assertTrue(self.charge_problem.is_adjacent(0, 2))
        self.assertFalse(self.charge_problem.is_adjacent(0, 1))
    
    def test_partition_operations(self):
        """测试分区相关操作"""
        partition_vertices = self.charge_problem.get_partition_vertices(0)
        self.assertEqual(len(partition_vertices), 2)
        self.assertEqual({v.id for v in partition_vertices}, {0, 1})


class TestColumnIndependentSet(unittest.TestCase):
    """测试独立集列类"""
    
    def setUp(self):
        """设置测试数据"""
        self.vertex_set = {1, 2, 3}
        self.pricing_problem = "test_pricing_problem"
        self.column = ColumnIndependentSet(
            vertex_set=self.vertex_set,
            associated_pricing_problem=self.pricing_problem,
            is_artificial=False,
            creator="test",
            value=5.0
        )
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.column.vertex_set, self.vertex_set)
        self.assertEqual(self.column.associated_pricing_problem, self.pricing_problem)
        self.assertEqual(self.column.is_artificial_column, False)
        self.assertEqual(self.column.creator, "test")
        self.assertEqual(self.column.value, 5.0)
    
    def test_equality_and_hash(self):
        """测试相等性和哈希"""
        column2 = ColumnIndependentSet(
            vertex_set=self.vertex_set,
            associated_pricing_problem=self.pricing_problem,
            is_artificial=False,
            creator="test"
        )
        
        self.assertEqual(self.column, column2)
        self.assertEqual(hash(self.column), hash(column2))
        
        # 测试不相等情况
        column3 = ColumnIndependentSet(
            vertex_set={4, 5, 6},
            associated_pricing_problem=self.pricing_problem,
            is_artificial=False,
            creator="test"
        )
        self.assertNotEqual(self.column, column3)


class TestColumnPool(unittest.TestCase):
    """测试列池类"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建模拟对象
        self.pricing_problem = Mock()
        self.pricing_problem.name = "test_pricing"
        
        self.column1 = ColumnIndependentSet(
            vertex_set={1, 2},
            associated_pricing_problem=self.pricing_problem,
            is_artificial=False,
            creator="test1"
        )
        
        self.column2 = ColumnIndependentSet(
            vertex_set={3, 4},
            associated_pricing_problem=self.pricing_problem,
            is_artificial=False,
            creator="test2"
        )
        
        # 初始化简化的列池
        self.column_pool = ColumnPool()
        self.column_pool.addColumn(self.column1)
    
    def test_column_operations(self):
        """测试列操作"""
        # 测试获取列数
        initial_count = len(self.column_pool.columns)
        self.assertEqual(initial_count, 1)
        
        # 测试添加列
        self.column_pool.addColumn(self.column2)
        
        new_count = len(self.column_pool.columns)
        self.assertEqual(new_count, 2)
        
        # 测试列是否存在
        self.assertIn(self.column1, self.column_pool.columns)
        self.assertIn(self.column2, self.column_pool.columns)
        
        # 测试移除列
        self.column_pool.removeColumn(self.column1)
        final_count = len(self.column_pool.columns)
        self.assertEqual(final_count, 1)
        self.assertNotIn(self.column1, self.column_pool.columns)


class TestColumnGenerationMocked(unittest.TestCase):
    """测试列生成算法（使用模拟对象）"""
    
    def setUp(self):
        """设置模拟环境"""
        # 创建模拟对象
        self.mock_instance = Mock(spec=ChargeProblem)
        self.mock_instance.config = Mock()
        self.mock_instance.config.epsilon = 1e-6
        
        self.mock_master = Mock(spec=MasterProblem)
        self.mock_pricing_problem = Mock(spec=PricingProblem)
        self.mock_pricing_solver = Mock(spec=ExactPricingSolver)
        self.mock_column_pool = Mock(spec=ColumnPool)
        
        # 设置默认返回值
        self.mock_column_pool.columns = []
        
        # 创建列生成算法实例
        self.cg = ColumnGeneration(
            instance=self.mock_instance,
            master=self.mock_master,
            pricing_problem=self.mock_pricing_problem,
            pricing_solver=self.mock_pricing_solver,
            column_pool=self.mock_column_pool
        )
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.cg.instance, self.mock_instance)
        self.assertEqual(self.cg.master, self.mock_master)
        self.assertEqual(self.cg.upper_bound, float("inf"))
        self.assertEqual(self.cg.lower_bound, 0.0)
        self.assertEqual(self.cg.iteration, 0)
    
    def test_termination_conditions(self):
        """测试终止条件"""
        # 测试上界终止
        self.cg.masterObjective = 100.0
        self.cg.upper_bound = 99.0
        self.assertTrue(self.cg.check_termination())
        
        # 测试收敛终止
        self.cg.masterObjective = 100.0
        self.cg.upper_bound = 200.0
        self.cg.lower_bound = 100.0 - 1e-7
        self.assertTrue(self.cg.check_termination())
        
        # 测试继续条件
        self.cg.masterObjective = 100.0
        self.cg.upper_bound = 200.0
        self.cg.lower_bound = 50.0
        self.assertIsNone(self.cg.check_termination())
    
    def test_solve_workflow(self):
        """测试求解流程"""
        # 设置模拟返回值
        self.mock_master.solveMaster.return_value = ({}, [1.0, 2.0], 10.0)
        
        # 第一次定价返回新列，第二次返回空列表
        new_column = ColumnIndependentSet(
            vertex_set={1, 2},
            associated_pricing_problem=self.mock_pricing_problem,
            is_artificial=False,
            creator="pricing"
        )
        self.mock_pricing_solver.generate_columns.side_effect = [[new_column], []]
        
        # 运行求解
        self.cg.solve(time_limit=60)
        
        # 验证调用
        self.assertEqual(self.mock_master.solveMaster.call_count, 2)
        self.assertEqual(self.mock_pricing_solver.generate_columns.call_count, 2)
        self.assertEqual(self.cg.iteration, 2)


class TestInstanceGeneration(unittest.TestCase):
    """测试实例生成和读取"""
    
    def setUp(self):
        """设置测试环境"""
        self.generator = PCPInstanceGenerator(seed=42)
        self.reader = PCPInstanceReader()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理临时文件"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_small_instance_generation(self):
        """测试小实例生成"""
        instance = self.generator.generate_small_test_instance()
        
        self.assertEqual(instance.name, "small_test")
        self.assertEqual(instance.num_vertices, 6)
        self.assertEqual(instance.num_partitions, 3)
        self.assertEqual(len(instance.edges), 4)
        self.assertEqual(instance.optimal_colors, 3)
    
    def test_random_instance_generation(self):
        """测试随机实例生成"""
        instance = self.generator.generate_random_instance(10, 3, 0.3)
        
        self.assertEqual(instance.num_vertices, 10)
        self.assertEqual(instance.num_partitions, 3)
        self.assertGreaterEqual(len(instance.edges), 0)
        
        # 验证分区覆盖所有顶点
        all_vertex_ids = {v["id"] for v in instance.vertices}
        partition_vertex_ids = set()
        for p in instance.partitions:
            partition_vertex_ids.update(p["vertex_ids"])
        
        self.assertEqual(all_vertex_ids, partition_vertex_ids)
    
    def test_grid_instance_generation(self):
        """测试网格实例生成"""
        instance = self.generator.generate_grid_instance(3, 3, 3)
        
        self.assertEqual(instance.num_vertices, 9)
        self.assertEqual(instance.num_partitions, 3)
        
        # 验证网格连接性（应该有12条边：6条水平+6条垂直）
        expected_edges = 2 * 3 * 2  # 2个方向 * 3行/列 * 2条边/行/列
        self.assertEqual(len(instance.edges), expected_edges)
    
    def test_instance_save_load(self):
        """测试实例保存和加载"""
        # 生成实例
        instance = self.generator.generate_small_test_instance()
        
        # 保存到文件
        file_path = os.path.join(self.temp_dir, "test_instance.json")
        self.generator.save_instance(instance, file_path)
        
        # 从文件加载
        charge_problem = self.reader.create_charge_problem(file_path)
        
        # 验证加载结果
        self.assertEqual(len(charge_problem.vertices), 6)
        self.assertEqual(len(charge_problem.partitions), 3)
        self.assertEqual(len(charge_problem.edges), 4)
        
        # 验证数据完整性
        errors = charge_problem.validate()
        self.assertEqual(len(errors), 0, f"验证失败: {errors}")


class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def setUp(self):
        """设置性能测试环境"""
        self.generator = PCPInstanceGenerator(seed=42)
    
    def test_medium_instance_creation_time(self):
        """测试中等规模实例创建时间"""
        start_time = time.time()
        
        instance = self.generator.generate_random_instance(100, 20, 0.1)
        
        creation_time = time.time() - start_time
        
        # 应该在1秒内完成
        self.assertLess(creation_time, 1.0, 
                       f"实例创建时间过长: {creation_time:.3f}秒")
        
        # 验证实例基本属性
        self.assertEqual(instance.num_vertices, 100)
        self.assertEqual(instance.num_partitions, 20)
    
    def test_charge_problem_operations_performance(self):
        """测试ChargeProblem操作性能"""
        # 创建较大的实例
        instance = self.generator.generate_random_instance(200, 40, 0.05)
        
        # 通过临时文件创建ChargeProblem
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            self.generator.save_instance(instance, f.name)
            
            reader = PCPInstanceReader()
            
            start_time = time.time()
            charge_problem = reader.create_charge_problem(f.name)
            creation_time = time.time() - start_time
            
            # 测试统计信息计算时间
            start_time = time.time()
            stats = charge_problem.get_statistics()
            stats_time = time.time() - start_time
            
            # 清理临时文件
            os.unlink(f.name)
        
        # 性能断言
        self.assertLess(creation_time, 2.0, 
                       f"ChargeProblem创建时间过长: {creation_time:.3f}秒")
        self.assertLess(stats_time, 0.1, 
                       f"统计信息计算时间过长: {stats_time:.3f}秒")


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def setUp(self):
        """设置边界测试环境"""
        self.generator = PCPInstanceGenerator(seed=42)
        self.reader = PCPInstanceReader()
    
    def test_single_vertex_instance(self):
        """测试单顶点实例"""
        # 创建最小实例
        instance = self.generator.generate_random_instance(1, 1, 0.0)
        
        self.assertEqual(instance.num_vertices, 1)
        self.assertEqual(instance.num_partitions, 1)
        self.assertEqual(len(instance.edges), 0)
    
    def test_empty_edge_instance(self):
        """测试无边实例"""
        instance = self.generator.generate_random_instance(10, 5, 0.0)
        
        self.assertEqual(len(instance.edges), 0)
        
        # 验证可以正常创建ChargeProblem
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            self.generator.save_instance(instance, f.name)
            charge_problem = self.reader.create_charge_problem(f.name)
            os.unlink(f.name)
        
        errors = charge_problem.validate()
        self.assertEqual(len(errors), 0)
    
    def test_complete_graph_instance(self):
        """测试完全图实例"""
        instance = self.generator.generate_complete_graph_instance(6, 3)
        
        expected_edges = 6 * 5 // 2  # C(6,2) = 15
        self.assertEqual(len(instance.edges), expected_edges)
        self.assertEqual(instance.optimal_colors, 3)


def create_test_suite():
    """创建完整的测试套件"""
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    test_classes = [
        TestDataModel,
        TestColumnIndependentSet,
        TestColumnPool,
        TestColumnGenerationMocked,
        TestInstanceGeneration,
        TestPerformance,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite


def run_tests(verbosity=2):
    """运行所有测试"""
    print("=" * 80)
    print("PCP求解器全面测试套件")
    print("=" * 80)
    
    # 创建测试套件
    suite = create_test_suite()
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # 输出结果统计
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print(f"\n失败的测试 ({len(result.failures)}):")
        for i, (test, trace) in enumerate(result.failures, 1):
            print(f"{i}. {test}")
            print(f"   {trace.split('AssertionError:')[-1].strip() if 'AssertionError:' in trace else 'Unknown failure'}")
    
    if result.errors:
        print(f"\n错误的测试 ({len(result.errors)}):")
        for i, (test, trace) in enumerate(result.errors, 1):
            print(f"{i}. {test}")
            print(f"   {trace.split('Error:')[-1].strip() if 'Error:' in trace else 'Unknown error'}")
    
    # 计算成功率
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / 
                   result.testsRun * 100) if result.testsRun > 0 else 0
    
    print(f"\n成功率: {success_rate:.1f}%")
    print("=" * 80)
    
    return result


if __name__ == "__main__":
    # 确保测试数据目录存在
    os.makedirs("test_data/instances", exist_ok=True)
    
    # 生成测试实例（如果不存在）
    if not os.path.exists("test_data/instances/small_test.json"):
        print("生成测试实例...")
        generator = PCPInstanceGenerator()
        small_instance = generator.generate_small_test_instance()
        generator.save_instance(small_instance, "test_data/instances/small_test.json")
        print("测试实例生成完成\n")
    
    # 运行测试
    result = run_tests()
    
    # 根据测试结果设置退出码
    sys.exit(0 if result.wasSuccessful() else 1)
