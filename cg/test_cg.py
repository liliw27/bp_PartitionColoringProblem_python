#!/usr/bin/env python3
"""
CG模块测试文件
主要测试 column_generation.py 的功能
"""
import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cg.column_generation import ColumnGeneration
from cg.column_independent_set import ColumnIndependentSet
from cg.column_pool import ColumnPool
from cg.master.master_problem import MasterProblem
from cg.pricing.pricing_problem import PricingProblem
from cg.pricing.exact_pricing_solver import ExactPricingSolver
from model.charge_problem import ChargeProblem
from bidict import bidict


class TestColumnGeneration(unittest.TestCase):
    """测试 ColumnGeneration 类的核心功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建模拟对象
        self.mock_instance = Mock(spec=ChargeProblem)
        self.mock_instance.config = Mock()
        self.mock_instance.config.epsilon = 1e-6
        
        self.mock_master = Mock(spec=MasterProblem)
        self.mock_pricing_problem = Mock(spec=PricingProblem)
        self.mock_pricing_solver = Mock(spec=ExactPricingSolver)
        self.mock_column_pool = Mock(spec=ColumnPool)
        
        # 设置 column_pool.columns 返回值
        self.mock_column_pool.columns = []
        
        # 创建 ColumnGeneration 实例
        self.cg = ColumnGeneration(
            instance=self.mock_instance,
            master=self.mock_master,
            pricing_problem=self.mock_pricing_problem,
            pricing_solver=self.mock_pricing_solver,
            column_pool=self.mock_column_pool
        )
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.cg.master, self.mock_master)
        self.assertEqual(self.cg.pricing_problem, self.mock_pricing_problem)
        self.assertEqual(self.cg.pricing_solver, self.mock_pricing_solver)
        self.assertEqual(self.cg.column_pool, self.mock_column_pool)
        self.assertEqual(self.cg.instance, self.mock_instance)
        
        self.assertEqual(self.cg.upper_bound, float("inf"))
        self.assertEqual(self.cg.lower_bound, 0.0)
        self.assertEqual(self.cg.masterSolveTime, 0)
        self.assertEqual(self.cg.pricingSolveTime, 0)
        self.assertEqual(self.cg.masterObjective, 0.0)
        self.assertEqual(self.cg.iteration, 0)
        self.assertIsNone(self.cg.solution)
        self.assertEqual(self.cg.new_columns, [])
        self.assertEqual(self.cg.dual, [])
    
    def test_check_termination_upper_bound(self):
        """测试终止条件 - 上界检查"""
        self.cg.masterObjective = 100.0
        self.cg.upper_bound = 99.0
        
        result = self.cg.check_termination()
        self.assertTrue(result)
    
    def test_check_termination_convergence(self):
        """测试终止条件 - 收敛检查"""
        self.cg.masterObjective = 100.0
        self.cg.lower_bound = 100.0 - 1e-7  # 小于 epsilon
        
        result = self.cg.check_termination()
        self.assertTrue(result)
    
    def test_check_termination_continue(self):
        """测试终止条件 - 继续迭代"""
        self.cg.masterObjective = 100.0
        self.cg.upper_bound = 200.0
        self.cg.lower_bound = 50.0
        
        result = self.cg.check_termination()
        self.assertIsNone(result)  # 不满足终止条件，返回 None
    
    def test_invoke_master(self):
        """测试调用主问题求解"""
        # 准备测试数据
        test_columns = [
            ColumnIndependentSet(
                vertex_set={1, 2},
                associated_pricing_problem="test",
                is_artificial=False,
                creator="test"
            )
        ]
        test_solution = {"col1": 0.5}
        test_duals = [1.0, 2.0, 3.0]
        test_obj_val = 10.5
        time_limit = 600
        
        # 设置 mock 返回值
        self.mock_master.solveMaster.return_value = (test_solution, test_duals, test_obj_val)
        
        # 记录开始时间
        start_time = time.time()
        
        # 调用方法
        self.cg.invokeMaster(test_columns, time_limit)
        
        # 验证结果
        self.mock_master.add_column_to_rmp.assert_called_once_with(test_columns[0])
        self.mock_master.solveMaster.assert_called_once_with(time_limit)
        
        self.assertEqual(self.cg.masterObjective, test_obj_val)
        self.assertEqual(self.cg.dual, test_duals)
        
        # 验证时间统计
        self.assertGreater(self.cg.masterSolveTime, 0)
    
    def test_invoke_pricing(self):
        """测试调用定价问题求解"""
        # 准备测试数据
        time_limit = 30
        test_dual = [1.0, 2.0, 3.0]
        test_new_columns = [
            ColumnIndependentSet(
                vertex_set={3, 4},
                associated_pricing_problem="test",
                is_artificial=False,
                creator="pricing"
            )
        ]
        
        # 设置 mock 返回值
        self.mock_pricing_solver.generate_columns.return_value = test_new_columns
        
        # 记录开始时间
        start_time = time.time()
        
        # 调用方法
        result = self.cg.invokePricing(time_limit, test_dual)
        
        # 验证结果
        self.mock_pricing_problem.update_pricing_problem.assert_called_once_with(test_dual)
        self.mock_pricing_solver.generate_columns.assert_called_once_with(time_limit)
        
        self.assertEqual(result, test_new_columns)
        
        # 验证时间统计
        self.assertGreater(self.cg.pricingSolveTime, 0)
    
    def test_solve_no_new_columns(self):
        """测试求解 - 没有新列生成的情况"""
        time_limit = 60
        
        # 设置 mock 返回值 - 主问题
        self.mock_master.solveMaster.return_value = ({}, [1.0, 2.0], 10.0)
        
        # 设置 mock 返回值 - 定价问题返回空列表
        self.mock_pricing_solver.generate_columns.return_value = []
        
        # 调用求解
        self.cg.solve(time_limit)
        
        # 验证至少调用了一次主问题和定价问题
        self.mock_master.solveMaster.assert_called()
        self.mock_pricing_solver.generate_columns.assert_called()
        
        # 验证迭代次数
        self.assertEqual(self.cg.iteration, 1)
    
    def test_solve_with_new_columns(self):
        """测试求解 - 有新列生成的情况"""
        time_limit = 60
        
        # 设置主问题返回值
        self.mock_master.solveMaster.return_value = ({}, [1.0, 2.0], 10.0)
        
        # 设置定价问题返回值 - 第一次有新列，第二次没有
        new_column = ColumnIndependentSet(
            vertex_set={1, 2},
            associated_pricing_problem="test",
            is_artificial=False,
            creator="pricing"
        )
        self.mock_pricing_solver.generate_columns.side_effect = [[new_column], []]
        
        # 调用求解
        self.cg.solve(time_limit)
        
        # 验证调用次数
        self.assertEqual(self.mock_master.solveMaster.call_count, 2)
        self.assertEqual(self.mock_pricing_solver.generate_columns.call_count, 2)
        
        # 验证迭代次数
        self.assertEqual(self.cg.iteration, 2)
    
    def test_solve_with_termination(self):
        """测试求解 - 满足终止条件"""
        time_limit = 60
        
        # 设置主问题返回值 - 目标值达到上界
        self.cg.upper_bound = 10.0
        self.mock_master.solveMaster.return_value = ({}, [1.0, 2.0], 11.0)
        
        # 调用求解
        self.cg.solve(time_limit)
        
        # 验证只调用了一次主问题，没有调用定价问题
        self.assertEqual(self.mock_master.solveMaster.call_count, 1)
        self.assertEqual(self.mock_pricing_solver.generate_columns.call_count, 0)
        
        # 验证迭代次数
        self.assertEqual(self.cg.iteration, 1)
    
    def test_solve_timing_tracking(self):
        """测试求解过程中的时间统计"""
        time_limit = 60
        
        # 设置 mock 返回值
        self.mock_master.solveMaster.return_value = ({}, [1.0, 2.0], 10.0)
        self.mock_pricing_solver.generate_columns.return_value = []
        
        # 调用求解
        initial_master_time = self.cg.masterSolveTime
        initial_pricing_time = self.cg.pricingSolveTime
        
        self.cg.solve(time_limit)
        
        # 验证时间有增加
        self.assertGreater(self.cg.masterSolveTime, initial_master_time)
        self.assertGreater(self.cg.pricingSolveTime, initial_pricing_time)


class TestColumnIndependentSet(unittest.TestCase):
    """测试 ColumnIndependentSet 类"""
    
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
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.column.vertex_set, self.vertex_set)
        self.assertEqual(self.column.associated_pricing_problem, self.pricing_problem)
        self.assertEqual(self.column.is_artificial_column, False)
        self.assertEqual(self.column.creator, "test")
        self.assertEqual(self.column.value, 5.0)
        self.assertEqual(self.column.iteration, 0)
    
    def test_equality(self):
        """测试相等性比较"""
        column2 = ColumnIndependentSet(
            vertex_set=self.vertex_set,
            associated_pricing_problem=self.pricing_problem,
            is_artificial=False,
            creator="test"
        )
        self.assertEqual(self.column, column2)
        
        # 测试不相等
        column3 = ColumnIndependentSet(
            vertex_set={4, 5, 6},
            associated_pricing_problem=self.pricing_problem,
            is_artificial=False,
            creator="test"
        )
        self.assertNotEqual(self.column, column3)
    
    def test_hash(self):
        """测试哈希功能"""
        column2 = ColumnIndependentSet(
            vertex_set=self.vertex_set,
            associated_pricing_problem=self.pricing_problem,
            is_artificial=False,
            creator="test"
        )
        self.assertEqual(hash(self.column), hash(column2))
    
    def test_str(self):
        """测试字符串表示"""
        str_repr = str(self.column)
        self.assertIn("IndependentSet", str_repr)
        self.assertIn("test", str_repr)
        self.assertIn("5.0", str_repr)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_column_generation_integration(self):
        """测试列生成算法的集成流程"""
        # 这里可以添加更复杂的集成测试
        # 例如使用真实的小规模数据进行端到端测试
        pass


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_suite.addTest(unittest.makeSuite(TestColumnGeneration))
    test_suite.addTest(unittest.makeSuite(TestColumnIndependentSet))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("CG模块测试 - 专注于 column_generation.py")
    print("=" * 70)
    
    result = run_tests()
    
    print("\n" + "=" * 70)
    print(f"测试完成!")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n成功率: {success_rate:.1f}%")
    print("=" * 70)