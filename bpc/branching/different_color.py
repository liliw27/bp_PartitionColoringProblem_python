from bpc.branching.branching_decision import BranchingDecision
from model.vertex import Vertex
from model.a_graph import AuxiliaryGraph
from cg.column_pool import ColumnPool
from typing import Tuple



class DifferentColor(BranchingDecision):
    def __init__(self, vertex_pair: Tuple[Vertex, Vertex]):
        self.vertex_pair = vertex_pair

    def a_graph_update(self,a_graph:AuxiliaryGraph):
        a_graph.different_color(self.vertex_pair[0], self.vertex_pair[1])

    def column_filter(self, column_pool: ColumnPool):
        for column in column_pool.columns:
            if column.is_artificial:
                continue
            if self.vertex_pair[0] in column.vertex_set and self.vertex_pair[1] in column.vertex_set:
                column_pool.removeColumn(column)
    