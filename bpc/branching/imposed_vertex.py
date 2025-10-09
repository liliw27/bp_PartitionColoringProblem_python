"""
分支定价算法中的强制顶点分支决策
"""
from model.vertex import Vertex
from bpc.branching.branching_decision import BranchingDecision
from model.a_graph import AuxiliaryGraph
from cg.column_pool import ColumnPool


class ImposedVertex(BranchingDecision):
    """
    强制顶点分支决策类
    
    当选择某个顶点时，该分区中的其他顶点将被禁用，
    确保该分区只使用这一个顶点的颜色。
    """
    
    def __init__(self, vertex: Vertex):
        """
        初始化强制顶点分支决策
        
        Args:
            vertex: 被强制选择的顶点
            a_graph: 辅助图对象
        """
        self.vertex = vertex
        
    
    def a_graph_update(self,a_graph:AuxiliaryGraph):
        """更新辅助图：移除同分区中的其他顶点"""
        a_graph.remove_other_vertices_in_partition(self.vertex)
    
    def column_filter(self, column_pool: ColumnPool):
        """
        过滤列池：移除包含同分区中其他顶点的列
        
        Args:
            column_pool: 需要过滤的列池
        """
        columns_to_remove = []
        
        for column in column_pool.columns:
            if column.is_artificial:
                continue
            # 检查列中是否包含同分区的其他顶点
            for v in self.a_graph.partitions[self.vertex.associated_partition.id].vertex_set:
                if v != self.vertex and v in column.vertex_set:
                    columns_to_remove.append(column)
                    break
        
        # 移除不符合条件的列
        for column in columns_to_remove:
            column_pool.removeColumn(column)
    
    def __str__(self):
        """返回字符串表示"""
        return f"ImposedVertex(vertex={self.vertex})"

    def __repr__(self):
        """返回详细的字符串表示"""
        return f"ImposedVertex(vertex={self.vertex.id}, partition={self.vertex.associated_partition.id})"