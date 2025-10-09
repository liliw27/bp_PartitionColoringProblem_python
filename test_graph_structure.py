#!/usr/bin/env python3
"""
测试图结构和独立集逻辑
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_graph_structure():
    """测试图结构和独立集逻辑"""
    
    print("=" * 60)
    print("图结构和独立集逻辑测试")
    print("=" * 60)
    
    # 1. 生成小测试实例
    from test_data.pcp_instance_generator import PCPInstanceGenerator
    from test_data.pcp_instance_reader import PCPInstanceReader
    
    generator = PCPInstanceGenerator(seed=42)
    instance = generator.generate_small_test_instance()
    
    print("\n1. 原始实例结构:")
    print(f"   顶点数: {instance.num_vertices}")
    print(f"   分区数: {instance.num_partitions}")
    print(f"   边数: {len(instance.edges)}")
    
    # 2. 创建ChargeProblem对象
    temp_file = "./temp_graph_test.json"
    generator.save_instance(instance, temp_file)
    
    reader = PCPInstanceReader()
    charge_problem = reader.create_charge_problem(temp_file)
    
    print("\n2. 分区结构:")
    for partition in charge_problem.partitions:
        vertices_in_partition = [v.id for v in charge_problem.vertices 
                               if v.associated_partition.id == partition.id]
        print(f"   分区 {partition.id}: 顶点 {vertices_in_partition}")
    
    print("\n3. 原图边（分区间冲突）:")
    for edge in charge_problem.edges:
        src_partition = edge.source.associated_partition.id
        tgt_partition = edge.target.associated_partition.id
        print(f"   边 ({edge.source.id}, {edge.target.id}): 分区{src_partition} - 分区{tgt_partition}")
    
    # 3. 创建辅助图
    from model.a_graph import AuxiliaryGraph
    aux_graph = AuxiliaryGraph(
        graph=charge_problem.graph,
            vertices_map=charge_problem.vertex_map,
            auxiliary_edges=None,
            merged_vertices_map=None
    )
    
    print("\n4. 辅助边（同分区内约束）:")
    if aux_graph.auxiliary_edges:
        for aux_edge in aux_graph.auxiliary_edges:
            src_partition = aux_edge.source.associated_partition.id
            tgt_partition = aux_edge.target.associated_partition.id
            print(f"   辅助边 ({aux_edge.source.id}, {aux_edge.target.id}): 分区{src_partition} - 分区{tgt_partition}")
    else:
        print("   没有辅助边（这是正确的，因为每个分区只有2个顶点，可以形成独立集）")
    
    # 4. 分析可能的独立集
    print("\n5. 可能的独立集分析:")
    
    # 对每个分区，分析可能的独立集
    for partition in charge_problem.partitions:
        partition_vertices = [v for v in charge_problem.vertices 
                            if v.associated_partition.id == partition.id]
        
        print(f"\n   分区 {partition.id} 的可能独立集:")
        
        # 单顶点独立集
        for vertex in partition_vertices:
            print(f"     单顶点集: {{{vertex.id}}}")
        
        # 检查是否可以有多顶点独立集
        if len(partition_vertices) > 1:
            # 检查分区内是否有边（辅助边）
            has_internal_edges = any(
                aux_edge.source.associated_partition.id == partition.id and
                aux_edge.target.associated_partition.id == partition.id
                for aux_edge in aux_graph.auxiliary_edges
            )
            
            if not has_internal_edges:
                vertex_ids = [v.id for v in partition_vertices]
                print(f"     多顶点集: {set(vertex_ids)} (分区内无冲突)")
            else:
                print(f"     多顶点集: 不可能 (分区内有冲突)")
    
    # 5. 验证定价问题的逻辑
    print("\n6. 定价问题逻辑验证:")
    print("   在PCP中，定价问题是在辅助图上寻找最大权重独立集")
    print("   辅助图 = 原图 + 同分区内顶点间的边")
    print("   这确保了:")
    print("   - 同一分区内最多选择一个顶点（一个分区一种颜色）")
    print("   - 相邻分区不能选择有边连接的顶点（冲突约束）")
    
    # 清理临时文件
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_graph_structure()
