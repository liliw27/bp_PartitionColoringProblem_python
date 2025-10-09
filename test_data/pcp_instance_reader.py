#!/usr/bin/env python3
"""
PCP实例读取器

从JSON文件读取PCP实例数据并转换为ChargeProblem对象
"""

import json
import os
from typing import List, Dict, Any
from model.charge_problem import ChargeProblem
from model.vertex import Vertex
from model.edge import Edge
from model.partition import Partition




class PCPInstanceReader:
    """PCP实例读取器"""
    
    def __init__(self):
        """初始化读取器"""
        pass
    
    def load_from_json(self, file_path: str) -> Dict[str, Any]:
        """从JSON文件加载原始数据
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            原始实例数据字典
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"实例文件不存在: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"JSON文件格式错误: {e}")
    
    def create_charge_problem(self, file_path: str) -> ChargeProblem:
        """从JSON文件创建ChargeProblem对象
        
        Args:
            file_path: JSON实例文件路径
            
        Returns:
            ChargeProblem对象
        """
        # 加载原始数据
        data = self.load_from_json(file_path)
        
        # 创建分区对象
        partitions = {}
        for p_data in data["partitions"]:
            partition = Partition(
                id=p_data["id"],
                vertex_set=set(p_data["vertex_ids"])
            )
            partitions[p_data["id"]] = partition
        
        # 创建顶点对象
        vertices = {}
        for v_data in data["vertices"]:
            partition = partitions[v_data["partition_id"]]
            vertex = Vertex(
                # id=v_data["id"],
                associated_partition=partition
            )
            vertices[v_data["id"]] = vertex
        
        # 创建边对象并更新邻接关系
        edges = []
        for e_data in data["edges"]:
            source = vertices[e_data["source"]]
            target = vertices[e_data["target"]]
            
            edge = Edge(
                source=source,
                target=target,
                weight=e_data.get("weight", 1.0)
            )
            edges.append(edge)
            
            # 更新邻接关系
            source.add_adjacent_vertex(target)
            target.add_adjacent_vertex(source)
        
        # 创建ChargeProblem对象
        charge_problem = ChargeProblem(
            edges=edges,
            vertices=list(vertices.values()),
            partitions=list(partitions.values())
        )
        
        # 添加实例元数据
        charge_problem.name = data.get("name", "unknown")
        charge_problem.description = data.get("description", "")
        charge_problem.optimal_colors = data.get("optimal_colors", None)

        
        return charge_problem
    
    def validate_instance(self, charge_problem: ChargeProblem) -> List[str]:
        """验证实例的有效性
        
        Args:
            charge_problem: 要验证的ChargeProblem对象
            
        Returns:
            验证错误列表，空列表表示验证通过
        """
        errors = []
        
        # 检查基本数据完整性
        if not charge_problem.vertices:
            errors.append("顶点列表为空")
        
        if not charge_problem.partitions:
            errors.append("分区列表为空")
        
        # 检查顶点分区分配
        vertex_ids = {v.id for v in charge_problem.vertices}
        partition_vertex_ids = set()
        
        for partition in charge_problem.partitions:
            for v_id in partition.vertex_set:
                if v_id not in vertex_ids:
                    errors.append(f"分区 {partition.id} 包含不存在的顶点 {v_id}")
                
                if v_id in partition_vertex_ids:
                    errors.append(f"顶点 {v_id} 被分配到多个分区")
                
                partition_vertex_ids.add(v_id)
        
        # 检查是否所有顶点都被分配到分区
        unassigned_vertices = vertex_ids - partition_vertex_ids
        if unassigned_vertices:
            errors.append(f"顶点 {unassigned_vertices} 未被分配到任何分区")
        
        # 检查边的有效性
        for edge in charge_problem.edges:
            if edge.source.id not in vertex_ids:
                errors.append(f"边包含不存在的源顶点 {edge.source.id}")
            if edge.target.id not in vertex_ids:
                errors.append(f"边包含不存在的目标顶点 {edge.target.id}")
        
        # 检查邻接关系的一致性
        for edge in charge_problem.edges:
            if not edge.source.is_adjacent_to(edge.target):
                errors.append(f"边 ({edge.source.id}, {edge.target.id}) 的邻接关系不一致")
            if not edge.target.is_adjacent_to(edge.source):
                errors.append(f"边 ({edge.target.id}, {edge.source.id}) 的邻接关系不一致")
        
        return errors
    
    def get_instance_info(self, file_path: str) -> Dict[str, Any]:
        """获取实例的基本信息
        
        Args:
            file_path: JSON实例文件路径
            
        Returns:
            实例信息字典
        """
        data = self.load_from_json(file_path)
        
        # 计算统计信息
        num_edges = len(data["edges"])
        avg_partition_size = data["num_vertices"] / data["num_partitions"]
        
        # 计算边密度
        max_edges = data["num_vertices"] * (data["num_vertices"] - 1) // 2
        edge_density = num_edges / max_edges if max_edges > 0 else 0
        
        # 计算分区间边数
        inter_partition_edges = 0
        vertex_to_partition = {v["id"]: v["partition_id"] for v in data["vertices"]}
        
        for edge in data["edges"]:
            if vertex_to_partition[edge["source"]] != vertex_to_partition[edge["target"]]:
                inter_partition_edges += 1
        
        return {
            "name": data.get("name", "unknown"),
            "description": data.get("description", ""),
            "num_vertices": data["num_vertices"],
            "num_partitions": data["num_partitions"],
            "num_edges": num_edges,
            "num_inter_partition_edges": inter_partition_edges,
            "edge_density": edge_density,
            "avg_partition_size": avg_partition_size,
            "optimal_colors": data.get("optimal_colors", None)
        }
    
    def list_available_instances(self, instances_dir: str) -> List[str]:
        """列出可用的实例文件
        
        Args:
            instances_dir: 实例文件目录
            
        Returns:
            实例文件名列表
        """
        if not os.path.exists(instances_dir):
            return []
        
        instances = []
        for file_name in os.listdir(instances_dir):
            if file_name.endswith('.json'):
                instances.append(file_name)
        
        return sorted(instances)


def main():
    """演示实例读取功能"""
    reader = PCPInstanceReader()
    
    # 假设有一个测试实例
    test_file = "test_data/instances/small_test.json"
    
    if os.path.exists(test_file):
        print("=== 加载测试实例 ===")
        
        # 获取实例信息
        info = reader.get_instance_info(test_file)
        print("实例信息:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print("\n=== 创建ChargeProblem对象 ===")
        
        # 创建ChargeProblem对象
        charge_problem = reader.create_charge_problem(test_file)
        print(f"创建的ChargeProblem:")
        print(f"  名称: {charge_problem.name}")
        print(f"  顶点数: {len(charge_problem.vertices)}")
        print(f"  边数: {len(charge_problem.edges)}")
        print(f"  分区数: {len(charge_problem.partitions)}")
        
        print("\n=== 验证实例 ===")
        
        # 验证实例
        errors = reader.validate_instance(charge_problem)
        if errors:
            print("验证错误:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("实例验证通过!")
    
    else:
        print(f"测试实例文件不存在: {test_file}")
        print("请先运行 pcp_instance_generator.py 生成测试实例")
    
    # 列出可用实例
    instances_dir = "test_data/instances"
    available_instances = reader.list_available_instances(instances_dir)
    
    print(f"\n=== 可用实例 ({len(available_instances)}) ===")
    for instance in available_instances:
        print(f"  - {instance}")


if __name__ == "__main__":
    main()
