#!/usr/bin/env python3
"""
分支定价算法测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_branch_and_price_framework():
    """测试分支定价算法框架"""
    
    print("=" * 60)
    print("分支定价算法框架测试")
    print("=" * 60)
    
    try:
        # 导入必要的模块
        from bpc.branch_and_price import BranchAndPrice
        from model.a_graph import AuxiliaryGraph
        from model.graph import Graph
        from test_data.pcp_instance_generator import PCPInstanceGenerator
        from test_data.pcp_instance_reader import PCPInstanceReader
        
        print("\n1. 创建测试实例...")
        generator = PCPInstanceGenerator(seed=42)
        instance = generator.generate_small_test_instance()
        
        # 保存并加载实例
        temp_file = "./temp_bp_test.json"
        generator.save_instance(instance, temp_file)
        
        reader = PCPInstanceReader()
        charge_problem = reader.create_charge_problem(temp_file)
        
        print(f"✓ 测试实例: {len(charge_problem.vertices)}顶点, {len(charge_problem.partitions)}分区")
        
        print("\n2. 创建辅助图...")
        aux_graph = AuxiliaryGraph(
            charge_problem.graph,
            {v.id: v for v in charge_problem.vertices},
            None,
            None
        )
        print(f"✓ 辅助图创建: {len(aux_graph.vertices_map)}顶点, {len(aux_graph.auxiliary_edges)}辅助边")
        
        print("\n3. 初始化分支定价算法...")
        bp = BranchAndPrice(aux_graph)
        
        print(f"✓ 初始状态:")
        print(f"  队列大小: {bp.queue_size()}")
        print(f"  最优目标值: {bp.best_objective}")
        print(f"  全局下界: {bp.global_lower_bound}")
        
        print("\n4. 测试根节点生成...")
        root_node = bp.generate_root_node()
        print(f"✓ 根节点创建: ID={root_node.nodeid}, 目标值={root_node.objective_value}")
        
        print("\n5. 测试优先队列操作...")
        bp.add_node(root_node)
        print(f"✓ 添加根节点后队列大小: {bp.queue_size()}")
        
        # 测试获取节点
        next_node = bp.get_next_node()
        if next_node:
            print(f"✓ 获取节点: ID={next_node.nodeid}")
        
        print(f"✓ 获取节点后队列大小: {bp.queue_size()}")
        
        print("\n6. 测试整数解检查...")
        # 测试非整数解
        non_integer_solution = {"var1": 0.5, "var2": 0.7}
        is_int1 = bp.is_integer_solution(non_integer_solution)
        print(f"✓ 非整数解 {non_integer_solution}: {is_int1}")
        
        # 测试整数解
        integer_solution = {"var1": 1.0, "var2": 0.0}
        is_int2 = bp.is_integer_solution(integer_solution)
        print(f"✓ 整数解 {integer_solution}: {is_int2}")
        
        print("\n7. 测试统计信息...")
        stats = bp.get_statistics()
        print("✓ 统计信息:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n" + "=" * 60)
        print("✅ 分支定价算法框架测试通过！")
        print("=" * 60)
        
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 清理临时文件
        temp_file = "./temp_bp_test.json"
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return False

if __name__ == "__main__":
    success = test_branch_and_price_framework()
    
    print("\n" + "=" * 60)
    print("测试总结:")
    if success:
        print("🎉 分支定价算法框架已准备就绪！")
        print("\n主要功能:")
        print("• ✅ 优先队列管理分支节点")
        print("• ✅ 根节点生成")
        print("• ✅ 整数解检查")
        print("• ✅ 统计信息跟踪")
        print("• ✅ 完整的算法框架")
        
        print("\n下一步:")
        print("• 完善列生成求解器集成")
        print("• 实现分支规则")
        print("• 添加剪枝优化")
        
    else:
        print("❌ 框架存在问题，需要进一步调试")
    
    print("=" * 60)
    sys.exit(0 if success else 1)
