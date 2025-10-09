from typing import List, Dict, Any, Optional
from model.edge import Edge
from model.vertex import Vertex
from model.partition import Partition
from model.graph import Graph


class ChargeProblem:
    """
    充电问题/分区着色问题 (Partition Coloring Problem, PCP) 的数据模型
    
    这个类封装了PCP问题的所有数据，包括：
    - 图结构（顶点和边）
    - 分区信息
    - 问题配置参数
    """
    
    def __init__(self, 
                 edges: List[Edge], 
                 vertices: List[Vertex], 
                 partitions: List[Partition]) -> None:
        """
        初始化充电问题实例
        
        Args:
            edges: 边列表
            vertices: 顶点列表
            partitions: 分区列表
            config: 配置参数，如果不提供则使用默认配置
        """
        self.edges = edges
        self.vertices = vertices
        self.partitions = partitions  # 这里保持原名以兼容现有代码
        # self.partition = partitions   # 添加这个属性以保持一致性
        
        
        # 实例元数据
        self.name: str = "unnamed_instance"
        self.description: str = ""
        self.optimal_colors: Optional[int] = None
        
        # 构建辅助数据结构
        self._build_lookup_tables()
        self.graph = Graph(edges, vertices, partitions,self.vertex_map)
    def _build_lookup_tables(self):
        """构建查找表以提高访问效率"""
        # 顶点ID到顶点对象的映射
        self.vertex_map: Dict[int, Vertex] = {v.id: v for v in self.vertices}
        
        # 分区ID到分区对象的映射
        self.partition_map: Dict[int, Partition] = {p.id: p for p in self.partitions}
        
        # 边的查找表（用于快速判断两顶点是否相邻）
        self.edge_set = set()
        for edge in self.edges:
            self.edge_set.add((min(edge.source.id, edge.target.id), 
                             max(edge.source.id, edge.target.id)))
    
    def get_vertex_by_id(self, vertex_id: int) -> Optional[Vertex]:
        """根据ID获取顶点"""
        return self.vertex_map.get(vertex_id)
    
    def get_partition_by_id(self, partition_id: int) -> Optional[Partition]:
        """根据ID获取分区"""
        return self.partition_map.get(partition_id)
    
    def is_adjacent(self, vertex1_id: int, vertex2_id: int) -> bool:
        """判断两个顶点是否相邻"""
        edge_key = (min(vertex1_id, vertex2_id), max(vertex1_id, vertex2_id))
        return edge_key in self.edge_set
    
    def get_partition_vertices(self, partition_id: int) -> List[Vertex]:
        """获取指定分区的所有顶点"""
        partition = self.get_partition_by_id(partition_id)
        if partition is None:
            return []
        
        return [self.vertex_map[vid] for vid in partition.vertex_set 
                if vid in self.vertex_map]
    
    def get_inter_partition_edges(self) -> List[Edge]:
        """获取分区间的边（连接不同分区顶点的边）"""
        inter_edges = []
        for edge in self.edges:
            if edge.source.associated_partition.id != edge.target.associated_partition.id:
                inter_edges.append(edge)
        return inter_edges
    
    def get_intra_partition_edges(self) -> List[Edge]:
        """获取分区内的边（连接同一分区顶点的边）"""
        intra_edges = []
        for edge in self.edges:
            if edge.source.associated_partition.id == edge.target.associated_partition.id:
                intra_edges.append(edge)
        return intra_edges
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取问题实例的统计信息"""
        num_vertices = len(self.vertices)
        num_edges = len(self.edges)
        num_partitions = len(self.partitions)
        
        # 计算边密度
        max_edges = num_vertices * (num_vertices - 1) // 2
        edge_density = num_edges / max_edges if max_edges > 0 else 0
        
        # 计算分区间边数
        inter_edges = self.get_inter_partition_edges()
        num_inter_edges = len(inter_edges)
        
        # 计算分区内边数
        intra_edges = self.get_intra_partition_edges()
        num_intra_edges = len(intra_edges)
        
        # 计算平均分区大小
        avg_partition_size = num_vertices / num_partitions if num_partitions > 0 else 0
        
        return {
            "name": self.name,
            "description": self.description,
            "num_vertices": num_vertices,
            "num_edges": num_edges,
            "num_partitions": num_partitions,
            "edge_density": round(edge_density, 4),
            "num_inter_partition_edges": num_inter_edges,
            "num_intra_partition_edges": num_intra_edges,
            "avg_partition_size": round(avg_partition_size, 2),
            "optimal_colors": self.optimal_colors
        }
    
    def validate(self) -> List[str]:
        """验证数据的完整性和一致性
        
        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []
        
        # 检查基本数据
        if not self.vertices:
            errors.append("顶点列表为空")
        if not self.partitions:
            errors.append("分区列表为空")
        
        # 检查顶点ID的唯一性
        vertex_ids = [v.id for v in self.vertices]
        if len(vertex_ids) != len(set(vertex_ids)):
            errors.append("存在重复的顶点ID")
        
        # 检查分区ID的唯一性
        partition_ids = [p.id for p in self.partitions]
        if len(partition_ids) != len(set(partition_ids)):
            errors.append("存在重复的分区ID")
        
        # 检查顶点分区分配
        all_partition_vertices = set()
        for partition in self.partitions:
            for vid in partition.vertex_set:
                if vid in all_partition_vertices:
                    errors.append(f"顶点 {vid} 被分配到多个分区")
                all_partition_vertices.add(vid)
        
        # 检查所有顶点都被分配到分区
        vertex_ids_set = set(vertex_ids)
        unassigned = vertex_ids_set - all_partition_vertices
        if unassigned:
            errors.append(f"顶点 {unassigned} 未被分配到任何分区")
        
        return errors
    
    def __str__(self) -> str:
        """字符串表示"""
        stats = self.get_statistics()
        return (f"ChargeProblem(name='{self.name}', "
                f"vertices={stats['num_vertices']}, "
                f"edges={stats['num_edges']}, "
                f"partitions={stats['num_partitions']})")
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()
