#!/usr/bin/env python3
"""
简单的端到端求解测试
验证算法能否找到正确的解
"""

import sys
import os
import traceback
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_simple_solve_test():
    """运行简单的求解测试"""
    
    try:
        print("=" * 70)
        print("分支定价算法 - 简单求解测试")
        print("=" * 70)
        
        # 导入必要模块
        from test_data.pcp_instance_generator import PCPInstanceGenerator
        from test_data.pcp_instance_reader import PCPInstanceReader
        from cg.column_generation import ColumnGeneration
        from cg.column_pool import ColumnPool
        from cg.master.master_problem import MasterProblem
        from cg.pricing.pricing_problem import PricingProblem
        from cg.pricing.exact_pricing_solver import ExactPricingSolver
        from model.a_graph import AuxiliaryGraph
        
        # 1. 生成测试实例
        print("\n1. 生成测试实例...")
        generator = PCPInstanceGenerator(seed=42)
        instance = generator.generate_small_test_instance()
        print(f"✓ 生成实例: {instance.num_vertices}顶点, {instance.num_partitions}分区")
        print(f"  预期需要颜色数: {instance.optimal_colors}")
        
        # 2. 创建ChargeProblem对象
        print("\n2. 创建问题对象...")
        temp_file = "./temp_solve_test.json"
        generator.save_instance(instance, temp_file)
        
        reader = PCPInstanceReader()
        charge_problem = reader.create_charge_problem(temp_file)
        print(f"✓ 问题对象创建成功")
        
        # 3. 初始化求解组件
        print("\n3. 初始化求解组件...")
        
        # 创建辅助图
        aux_graph = AuxiliaryGraph(
            graph=charge_problem.graph,
            vertices_map=charge_problem.vertex_map,
            auxiliary_edges=None,
            merged_vertices_map=None
        )
        
        # 创建定价问题
        pricing_problem = PricingProblem(
            auxiliary_graph=aux_graph,
            name="main_pricing",
            dualcosts=[]
        )
        
        # 创建定价求解器
        pricing_solver = ExactPricingSolver(
            auxiliary_graph=aux_graph,
            pricing_problem=pricing_problem
        )
        
        # 创建列池
        column_pool = ColumnPool()
        
        # 创建主问题
        master_problem = MasterProblem(
            data_model=charge_problem,
            pricing_problem=pricing_problem,
            column_pool=column_pool
        )
        
        # 构建主问题模型
        master_problem.buildModel()
        
        # 创建列生成算法
        column_generation = ColumnGeneration(
            instance=charge_problem,
            master=master_problem,
            pricing_problem=pricing_problem,
            pricing_solver=pricing_solver,
            column_pool=column_pool
        )
        
        print("✓ 所有组件初始化成功")
        
        # 4. 运行列生成算法
        print("\n4. 运行列生成算法...")
        print("   (时间限制: 60秒)")
        
        start_time = time.time()
        column_generation.solve(time_limit=60)
        solve_time = time.time() - start_time
        
        # 5. 分析结果
        print("\n5. 求解结果分析...")
        print(f"✓ 求解完成，耗时: {solve_time:.3f}秒")
        print(f"✓ 迭代次数: {column_generation.iteration}")
        print(f"✓ 目标值: {column_generation.masterObjective:.6f}")
        print(f"✓ 上界: {column_generation.upper_bound}")
        print(f"✓ 下界: {column_generation.lower_bound:.6f}")
        print(f"✓ 主问题求解时间: {column_generation.masterSolveTime:.3f}秒")
        print(f"✓ 定价问题求解时间: {column_generation.pricingSolveTime:.3f}秒")
        
        # 检查解的质量
        if column_generation.solution:
            print(f"\n6. 解的质量分析...")
            solution = column_generation.solution
            used_colors = 0
            
            print("   使用的列:")
            for col_id, value in solution.items():
                if value > 1e-6:  # 非零值
                    used_colors += 1
                    print(f"     列 {col_id}: 值 = {value:.6f}")
            
            print(f"✓ 总共使用颜色数: {used_colors}")
            print(f"✓ 预期最优颜色数: {instance.optimal_colors}")
            
            if used_colors <= instance.optimal_colors:
                print("🎉 找到了最优解！")
            elif used_colors <= instance.optimal_colors + 1:
                print("👍 找到了接近最优的解")
            else:
                print("⚠️ 解的质量可能不够好")
                
        else:
            print("⚠️ 没有找到可行解")
        
        print("\n" + "=" * 70)
        print("测试完成！")
        print("=" * 70)
        
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return True
        
    except Exception as e:
        print(f"\n❌ 求解过程中出现错误: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()
        
        # 清理临时文件
        temp_file = "./temp_solve_test.json"
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return False

if __name__ == "__main__":
    success = run_simple_solve_test()
    sys.exit(0 if success else 1)
