#!/usr/bin/env python3
"""
简单的调试测试脚本
用于验证基本功能是否正常工作
"""

import sys
import os
import traceback

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("=" * 60)
    print("开始基本功能测试...")
    print("=" * 60)
    
    # 1. 测试导入
    print("\n1. 测试模块导入...")
    from test_data.pcp_instance_generator import PCPInstanceGenerator
    from test_data.pcp_instance_reader import PCPInstanceReader
    print("✓ 测试数据模块导入成功")
    
    from cg.column_generation import ColumnGeneration
    from cg.column_independent_set import ColumnIndependentSet
    from cg.column_pool import ColumnPool
    print("✓ 列生成模块导入成功")
    
    from model.charge_problem import ChargeProblem
    from model.vertex import Vertex
    from model.edge import Edge
    from model.partition import Partition
    print("✓ 数据模型导入成功")
    
    # 2. 测试实例生成
    print("\n2. 测试实例生成...")
    generator = PCPInstanceGenerator(seed=42)
    instance = generator.generate_small_test_instance()
    print(f"✓ 生成小测试实例: {instance.num_vertices}顶点, {instance.num_partitions}分区")
    
    # 3. 测试实例保存和加载
    print("\n3. 测试实例保存和加载...")
    temp_file = "./temp_test_instance.json"
    generator.save_instance(instance, temp_file)
    print(f"✓ 实例保存到 {temp_file}")
    
    reader = PCPInstanceReader()
    charge_problem = reader.create_charge_problem(temp_file)
    print(f"✓ 实例加载成功: {len(charge_problem.vertices)}顶点, {len(charge_problem.partitions)}分区")
    
    # 4. 测试数据验证
    print("\n4. 测试数据验证...")
    errors = charge_problem.validate()
    if errors:
        print(f"⚠️ 数据验证发现问题: {errors}")
    else:
        print("✓ 数据验证通过")
    
    # 5. 测试统计信息
    print("\n5. 测试统计信息...")
    stats = charge_problem.get_statistics()
    print(f"✓ 统计信息: {stats}")
    
    # 6. 尝试创建求解组件（不实际求解）
    print("\n6. 测试求解组件创建...")
    
    from model.a_graph import AuxiliaryGraph
    from cg.master.master_problem import MasterProblem
    from cg.pricing.pricing_problem import PricingProblem
    from cg.pricing.exact_pricing_solver import ExactPricingSolver
    
    # 创建辅助图
    aux_graph = AuxiliaryGraph(
       graph=self.charge_problem.graph,
            vertices_map=self.charge_problem.vertex_map,
            auxiliary_edges=None,
            merged_vertices_map=None
    )
    print("✓ 辅助图创建成功")
    
    # 创建定价问题
    pricing_problem = PricingProblem(
        auxiliary_graph=aux_graph,
        name="test_pricing",
        dualcosts=[]
    )
    print("✓ 定价问题创建成功")
    
    # 创建列池
    column_pool = ColumnPool()
    print("✓ 列池创建成功")
    
    # 创建主问题
    master_problem = MasterProblem(
        data_model=charge_problem,
        pricing_problem=pricing_problem,
        column_pool=column_pool
    )
    print("✓ 主问题创建成功")
    
    # 尝试构建主问题模型
    print("\n7. 测试主问题模型构建...")
    try:
        master_problem.buildModel()
        print("✓ 主问题模型构建成功")
    except Exception as e:
        print(f"⚠️ 主问题模型构建失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("基本功能测试完成！")
    print("=" * 60)
    
    # 清理临时文件
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"✓ 清理临时文件: {temp_file}")

except Exception as e:
    print(f"\n❌ 测试过程中出现错误: {e}")
    print("\n详细错误信息:")
    traceback.print_exc()
    
    # 清理临时文件
    temp_file = "./temp_test_instance.json"
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"✓ 清理临时文件: {temp_file}")
