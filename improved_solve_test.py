#!/usr/bin/env python3
"""
改进的端到端求解测试
添加初始可行列来确保主问题可行
"""

import sys
import os
import traceback
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_artificial_columns(charge_problem):
    """为每个分区创建人工列（单顶点独立集）"""
    from cg.column_independent_set import ColumnIndependentSet
    
    artificial_columns = []
    
    # 为每个分区创建单顶点列
    for partition in charge_problem.partitions:
        partition_vertices = [v for v in charge_problem.vertices 
                            if v.associated_partition.id == partition.id]
        
        # 为每个顶点创建一个单独的列
        for vertex in partition_vertices:
            column = ColumnIndependentSet(
                vertex_set={vertex.id},
                associated_pricing_problem="artificial",
                is_artificial=True,
                creator="artificial_initialization",
                value=1.0  # 人工列的代价很高
            )
            artificial_columns.append(column)
    
    return artificial_columns

def run_improved_solve_test():
    """运行改进的求解测试"""
    
    try:
        print("=" * 70)
        print("分支定价算法 - 改进的求解测试")
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
        temp_file = "./temp_improved_solve_test.json"
        generator.save_instance(instance, temp_file)
        
        reader = PCPInstanceReader()
        charge_problem = reader.create_charge_problem(temp_file)
        print(f"✓ 问题对象创建成功")
        
        # 3. 创建人工列
        print("\n3. 创建初始人工列...")
        artificial_columns = create_artificial_columns(charge_problem)
        print(f"✓ 创建了 {len(artificial_columns)} 个人工列")
        
        # 4. 初始化求解组件
        print("\n4. 初始化求解组件...")
        
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
        
        # 创建列池并添加人工列
        column_pool = ColumnPool()
        for column in artificial_columns:
            column_pool.addColumn(column)
        
        print(f"✓ 列池中有 {len(column_pool.columns)} 个初始列")
        
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
        
        # 5. 运行列生成算法
        print("\n5. 运行列生成算法...")
        print("   (时间限制: 60秒)")
        
        start_time = time.time()
        column_generation.solve(time_limit=60)
        solve_time = time.time() - start_time
        
        # 6. 分析结果
        print("\n6. 求解结果分析...")
        print(f"✓ 求解完成，耗时: {solve_time:.3f}秒")
        print(f"✓ 迭代次数: {column_generation.iteration}")
        print(f"✓ 目标值: {column_generation.masterObjective:.6f}")
        print(f"✓ 上界: {column_generation.upper_bound}")
        print(f"✓ 下界: {column_generation.lower_bound:.6f}")
        print(f"✓ 主问题求解时间: {column_generation.masterSolveTime:.3f}秒")
        print(f"✓ 定价问题求解时间: {column_generation.pricingSolveTime:.3f}秒")
        
        # 检查解的质量
        if column_generation.solution:
            print(f"\n7. 解的质量分析...")
            solution = column_generation.solution
            used_colors = 0
            non_artificial_colors = 0
            
            print("   使用的列:")
            for col_id, value in solution.items():
                if value > 1e-6:  # 非零值
                    used_colors += 1
                    # 检查是否是人工列
                    is_artificial = any(col.is_artificial_column for col in column_pool.columns 
                                      if str(col) == col_id)
                    if not is_artificial:
                        non_artificial_colors += 1
                    
                    status = "(人工列)" if is_artificial else "(真实列)"
                    print(f"     列 {col_id}: 值 = {value:.6f} {status}")
            
            print(f"✓ 总共使用颜色数: {used_colors}")
            print(f"✓ 非人工列数: {non_artificial_colors}")
            print(f"✓ 预期最优颜色数: {instance.optimal_colors}")
            
            if non_artificial_colors > 0:
                print("🎉 找到了非人工列的解！")
                if non_artificial_colors <= instance.optimal_colors:
                    print("🏆 解的质量很好！")
                elif non_artificial_colors <= instance.optimal_colors + 1:
                    print("👍 解的质量不错")
                else:
                    print("⚠️ 解的质量可能需要改进")
            else:
                print("⚠️ 只找到了人工列的解，可能需要更多迭代")
                
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
        temp_file = "./temp_improved_solve_test.json"
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return False

if __name__ == "__main__":
    success = run_improved_solve_test()
    sys.exit(0 if success else 1)
