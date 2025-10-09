from bpc.branching.branching_decision import BranchingDecision
from model.vertex import Vertex
from model.a_graph import AuxiliaryGraph
from cg.column_pool import ColumnPool

class ForbidVertex(BranchingDecision):
    def __init__(self, vertex: Vertex):
        self.vertex = vertex
        
        
    def a_graph_update(self,a_graph:AuxiliaryGraph):
        a_graph.remove_vertex(self.vertex)
    
    def column_filter(self,column_pool:ColumnPool):
        for column in column_pool.columns:
            if column.is_artificial:
                continue
            if self.vertex in column.vertex_set:
                column_pool.removeColumn(column)
    def __str__(self):
        return f"ForbidVertex(vertex={self.vertex})"

    def __repr__(self):
        return f"ForbidVertex(vertex={self.vertex})"