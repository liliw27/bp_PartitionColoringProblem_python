from typing import Optional
from model.a_graph import AuxiliaryGraph
from cg.column_pool import ColumnPool
class BPCNode:
    _next_node_id = 1
    def __init__(self, parent: Optional['BPCNode'] = None, a_graph: AuxiliaryGraph = None,column_pool:ColumnPool = None,objective_value:float = float('-inf'),solution:dict[int,float] = {}):
        self.a_graph=a_graph
        
        # Generate unique node ID
        self.nodeid = BPCNode._next_node_id
        BPCNode._next_node_id += 1
        self.parent = parent
        self.column_pool=column_pool
        
        self.objective_value = objective_value
        self.solution = solution
        
    def __lt__(self, other):
        return self.objective_value < other.objective_value
        
    def __eq__(self, other):
        return self.objective_value == other.objective_value
        
    def __gt__(self, other):
        return self.objective_value > other.objective_value
        
        