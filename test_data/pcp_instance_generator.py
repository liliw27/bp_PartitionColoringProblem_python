#!/usr/bin/env python3
"""
PCP (Partition Coloring Problem) 测试算例生成器

用于生成各种规模和类型的PCP测试实例，包括：
- 随机图
- 网格图
- 完全图
- 稀疏图等
"""

import random
import json
import os
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class PCPInstanceData:
    """PCP实例数据结构"""
    name: str
    num_vertices: int
    num_partitions: int
    vertices: List[Dict]  # [{"id": int, "partition_id": int, "data": any}]
    edges: List[Dict]     # [{"source": int, "target": int, "weight": float}]
    partitions: List[Dict] # [{"id": int, "vertex_ids": List[int]}]
    optimal_colors: int = None  # 最优着色数（如果已知）
    description: str = ""


class PCPInstanceGenerator:
    """PCP实例生成器"""
    
    def __init__(self, seed: int = 42):
        """初始化生成器
        
        Args:
            seed: 随机种子，确保结果可重现
        """
        self.seed = seed
        random.seed(seed)
    
    def generate_random_instance(self, 
                                num_vertices: int, 
                                num_partitions: int,
                                edge_probability: float = 0.3,
                                name: str = None) -> PCPInstanceData:
        """生成随机PCP实例
        
        Args:
            num_vertices: 顶点数量
            num_partitions: 分区数量
            edge_probability: 边的存在概率
            name: 实例名称
        """
        if name is None:
            name = f"random_{num_vertices}v_{num_partitions}p"
        
        # 生成顶点并随机分配到分区
        vertices = []
        partition_assignment = {}
        
        for i in range(num_vertices):
            partition_id = random.randint(0, num_partitions - 1)
            vertices.append({
                "id": i,
                "partition_id": partition_id,
                "data": f"vertex_{i}"
            })
            
            if partition_id not in partition_assignment:
                partition_assignment[partition_id] = []
            partition_assignment[partition_id].append(i)
        
        # 确保每个分区至少有一个顶点
        for p_id in range(num_partitions):
            if p_id not in partition_assignment:
                # 从其他分区移动一个顶点
                source_partition = random.choice(list(partition_assignment.keys()))
                vertex_id = partition_assignment[source_partition].pop()
                partition_assignment[p_id] = [vertex_id]
                vertices[vertex_id]["partition_id"] = p_id
        
        # 生成分区信息
        partitions = []
        for p_id in range(num_partitions):
            partitions.append({
                "id": p_id,
                "vertex_ids": partition_assignment.get(p_id, [])
            })
        
        # 生成随机边
        edges = []
        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                if random.random() < edge_probability:
                    edges.append({
                        "source": i,
                        "target": j,
                        "weight": 1.0
                    })
        
       
        
        return PCPInstanceData(
            name=name,
            num_vertices=num_vertices,
            num_partitions=num_partitions,
            vertices=vertices,
            edges=edges,
            partitions=partitions,
            description=f"Random PCP instance with {num_vertices} vertices, {num_partitions} partitions, edge_prob={edge_probability}"
        )
    
    def generate_grid_instance(self, 
                              rows: int, 
                              cols: int,
                              partition_size: int = 4,
                              name: str = None) -> PCPInstanceData:
        """生成网格图PCP实例
        
        Args:
            rows: 网格行数
            cols: 网格列数
            partition_size: 每个分区的大小
            name: 实例名称
        """
        if name is None:
            name = f"grid_{rows}x{cols}_ps{partition_size}"
        
        num_vertices = rows * cols
        num_partitions = (num_vertices + partition_size - 1) // partition_size
        
        # 生成网格顶点
        vertices = []
        for r in range(rows):
            for c in range(cols):
                vertex_id = r * cols + c
                partition_id = vertex_id // partition_size
                vertices.append({
                    "id": vertex_id,
                    "partition_id": partition_id,
                    "data": f"grid_{r}_{c}"
                })
        
        # 生成网格边（4连通）
        edges = []
        for r in range(rows):
            for c in range(cols):
                current_id = r * cols + c
                
                # 右边
                if c < cols - 1:
                    right_id = r * cols + (c + 1)
                    edges.append({
                        "source": current_id,
                        "target": right_id,
                        "weight": 1.0
                    })
                
                # 下边
                if r < rows - 1:
                    down_id = (r + 1) * cols + c
                    edges.append({
                        "source": current_id,
                        "target": down_id,
                        "weight": 1.0
                    })
        
        # 生成分区信息
        partitions = []
        for p_id in range(num_partitions):
            start_vertex = p_id * partition_size
            end_vertex = min((p_id + 1) * partition_size, num_vertices)
            vertex_ids = list(range(start_vertex, end_vertex))
            
            partitions.append({
                "id": p_id,
                "vertex_ids": vertex_ids
            })
        
       
        
        # 计算网格图的理论最优着色数
        optimal_colors = self._estimate_grid_coloring(rows, cols, partition_size)
        
        return PCPInstanceData(
            name=name,
            num_vertices=num_vertices,
            num_partitions=num_partitions,
            vertices=vertices,
            edges=edges,
            partitions=partitions,
            optimal_colors=optimal_colors,
            description=f"Grid PCP instance {rows}x{cols} with partition size {partition_size}"
        )
    
    def generate_complete_graph_instance(self,
                                       num_vertices: int,
                                       num_partitions: int,
                                       name: str = None) -> PCPInstanceData:
        """生成完全图PCP实例
        
        Args:
            num_vertices: 顶点数量
            num_partitions: 分区数量
            name: 实例名称
        """
        if name is None:
            name = f"complete_{num_vertices}v_{num_partitions}p"
        
        # 均匀分配顶点到分区
        vertices = []
        partition_assignment = {i: [] for i in range(num_partitions)}
        
        for i in range(num_vertices):
            partition_id = i % num_partitions
            vertices.append({
                "id": i,
                "partition_id": partition_id,
                "data": f"vertex_{i}"
            })
            partition_assignment[partition_id].append(i)
        
        # 生成完全图的所有边
        edges = []
        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                edges.append({
                    "source": i,
                    "target": j,
                    "weight": 1.0
                })
        
        # 生成分区信息
        partitions = []
        for p_id in range(num_partitions):
            partitions.append({
                "id": p_id,
                "vertex_ids": partition_assignment[p_id]
            })
        
        
        return PCPInstanceData(
            name=name,
            num_vertices=num_vertices,
            num_partitions=num_partitions,
            vertices=vertices,
            edges=edges,
            partitions=partitions,
            optimal_colors=num_partitions,  # 完全图的分区着色数等于分区数
            description=f"Complete graph PCP instance with {num_vertices} vertices, {num_partitions} partitions"
        )
    
    def generate_small_test_instance(self) -> PCPInstanceData:
        """生成小规模测试实例，便于调试"""
        return PCPInstanceData(
            name="small_test",
            num_vertices=6,
            num_partitions=3,
            vertices=[
                {"id": 0, "partition_id": 0, "data": "v0_p0"},
                {"id": 1, "partition_id": 0, "data": "v1_p0"},
                {"id": 2, "partition_id": 1, "data": "v2_p1"},
                {"id": 3, "partition_id": 1, "data": "v3_p1"},
                {"id": 4, "partition_id": 2, "data": "v4_p2"},
                {"id": 5, "partition_id": 2, "data": "v5_p2"}
            ],
            edges=[
                {"source": 0, "target": 2, "weight": 1.0},  # 分区0-1之间
                {"source": 1, "target": 3, "weight": 1.0},  # 分区0-1之间
                {"source": 2, "target": 4, "weight": 1.0},  # 分区1-2之间
                {"source": 0, "target": 4, "weight": 1.0},  # 分区0-2之间
            ],
            partitions=[
                {"id": 0, "vertex_ids": [0, 1]},
                {"id": 1, "vertex_ids": [2, 3]},
                {"id": 2, "vertex_ids": [4, 5]}
            ],
            optimal_colors=3,
            description="Small test instance for debugging - 6 vertices, 3 partitions, requires 3 colors"
        )
    
    def _estimate_grid_coloring(self, rows: int, cols: int, partition_size: int) -> int:
        """估算网格图的分区着色数"""
        # 这是一个简化的估算，实际情况可能更复杂
        num_partitions = (rows * cols + partition_size - 1) // partition_size
        
        # 网格图的分区着色数通常比分区数小
        # 这里给出一个保守估算
        if partition_size == 1:
            return 4  # 网格图的经典着色数
        else:
            # 分区越大，着色数相对越小
            return max(2, num_partitions // 2)
    
    def save_instance(self, instance: PCPInstanceData, file_path: str):
        """保存实例到JSON文件"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        instance_dict = {
            "name": instance.name,
            "num_vertices": instance.num_vertices,
            "num_partitions": instance.num_partitions,
            "vertices": instance.vertices,
            "edges": instance.edges,
            "partitions": instance.partitions,
            "optimal_colors": instance.optimal_colors,
            "description": instance.description
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(instance_dict, f, indent=2, ensure_ascii=False)
        
        print(f"实例已保存到: {file_path}")


def main():
    """生成一系列测试实例"""
    generator = PCPInstanceGenerator(seed=42)
    
    # 创建测试数据目录
    test_dir = "test_data/instances"
    os.makedirs(test_dir, exist_ok=True)
    
    # 生成各种类型的测试实例
    instances = [
        # 小规模调试实例
        generator.generate_small_test_instance(),
        
        # 随机实例
        generator.generate_random_instance(10, 3, 0.3, "random_small"),
        generator.generate_random_instance(20, 5, 0.4, "random_medium"),
        generator.generate_random_instance(50, 10, 0.2, "random_large_sparse"),
        generator.generate_random_instance(30, 8, 0.6, "random_dense"),
        
        # 网格实例
        generator.generate_grid_instance(3, 3, 3, "grid_3x3"),
        generator.generate_grid_instance(4, 4, 4, "grid_4x4"),
        generator.generate_grid_instance(5, 6, 5, "grid_5x6"),
        
        # 完全图实例
        generator.generate_complete_graph_instance(8, 4, "complete_small"),
        generator.generate_complete_graph_instance(12, 6, "complete_medium"),
    ]
    
    # 保存所有实例
    for instance in instances:
        file_path = os.path.join(test_dir, f"{instance.name}.json")
        generator.save_instance(instance, file_path)
    
    print(f"\n总共生成了 {len(instances)} 个测试实例")
    print("实例列表:")
    for instance in instances:
        print(f"  - {instance.name}: {instance.description}")


if __name__ == "__main__":
    main()
