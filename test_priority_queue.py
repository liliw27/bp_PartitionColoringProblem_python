#!/usr/bin/env python3
"""
测试分支定价算法中的优先队列功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_priority_queue():
    """测试优先队列的基本功能"""
    
    print("=" * 50)
    print("分支定价优先队列测试")
    print("=" * 50)
    
    from bpc.branch_and_price import BranchAndPrice
    from bpc.bpc_node import BPCNode
    from model.a_graph import AuxiliaryGraph
    from model.graph import Graph
    
    # 创建一个简单的图用于测试
    graph = Graph([], [], [])
    aux_graph = AuxiliaryGraph(graph, {}, None, None)
    
    # 创建分支定价算法实例
    bp = BranchAndPrice(aux_graph)
    
    print("\n1. 测试空队列:")
    print(f"   队列是否为空: {bp.is_queue_empty()}")
    print(f"   队列大小: {bp.queue_size()}")
    print(f"   获取下一个节点: {bp.get_next_node()}")
    
    print("\n2. 添加节点到队列:")
    
    # 创建几个测试节点，目标值不同
    nodes = [
        BPCNode(objective_value=5.5, solution={"test": "node1"}),
        BPCNode(objective_value=2.1, solution={"test": "node2"}),
        BPCNode(objective_value=8.3, solution={"test": "node3"}),
        BPCNode(objective_value=1.0, solution={"test": "node4"}),
        BPCNode(objective_value=4.7, solution={"test": "node5"}),
    ]
    
    for i, node in enumerate(nodes):
        bp.add_node(node)
        print(f"   添加节点{i+1}: 目标值={node.objective_value}, 队列大小={bp.queue_size()}")
    
    print(f"\n   最终队列大小: {bp.queue_size()}")
    print(f"   队列是否为空: {bp.is_queue_empty()}")
    
    print("\n3. 按优先级弹出节点:")
    
    expected_order = [1.0, 2.1, 4.7, 5.5, 8.3]  # 预期的弹出顺序
    actual_order = []
    
    while not bp.is_queue_empty():
        node = bp.get_next_node()
        actual_order.append(node.objective_value)
        print(f"   弹出节点: ID={node.nodeid}, 目标值={node.objective_value}, "
              f"解={node.solution}, 剩余队列大小={bp.queue_size()}")
    
    print(f"\n4. 验证排序正确性:")
    print(f"   预期顺序: {expected_order}")
    print(f"   实际顺序: {actual_order}")
    print(f"   排序正确: {expected_order == actual_order}")
    
    print(f"\n   最终队列大小: {bp.queue_size()}")
    print(f"   队列是否为空: {bp.is_queue_empty()}")
    
    print("\n" + "=" * 50)
    print("测试完成!")
    
    if expected_order == actual_order:
        print("✅ 优先队列功能正常！")
        return True
    else:
        print("❌ 优先队列排序有误！")
        return False

if __name__ == "__main__":
    success = test_priority_queue()
    sys.exit(0 if success else 1)
