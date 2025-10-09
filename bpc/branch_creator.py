from typing import Tuple
from cg.column_pool import ColumnPool
from bpc.branching.branching_decision import BranchingDecision
from bpc.branching.imposed_vertex import ImposedVertex
from bpc.branching.forbid_vertex import ForbidVertex
from model.vertex import Vertex
from model.a_graph import AuxiliaryGraph
from bpc.branching.same_color import SameColor
from bpc.branching.different_color import DifferentColor

class BranchCreator:
    def __init__(self, solution:dict[int,float],column_pool:ColumnPool,a_graph:AuxiliaryGraph):
        self.solution = solution
        self.column_pool = column_pool
        self.checked_vertex=None
        self.a_graph=a_graph
    def create_branch(self)->Tuple[BranchingDecision,BranchingDecision]:
        if self.check_branch_rule1():
            return self.create_branch_rule1(self.checked_vertex)
        elif self.check_branch_rule2():
            return self.create_branch_rule2()
        else:
            return None
    
    def check_branch_rule1(self)->bool:
        for k,v in self.solution.items():
            column_id=k
            value=v
            valued_column_num_for_each_vertices={}
            column=self.column_pool.get_column_by_id(column_id)
            if value>0:
                for vertex_id in column.vertex_set:
                    if vertex_id not in valued_column_num_for_each_vertices:
                        valued_column_num_for_each_vertices[vertex_id]=0
                    valued_column_num_for_each_vertices[vertex_id]+=1
        if not valued_column_num_for_each_vertices:
            return False
            
        max_vertex = max(valued_column_num_for_each_vertices.items(), key=lambda x: x[1])
        
        if max_vertex[1] > 1:
            self.checked_vertex=max_vertex[0]
            return True
        return False
    
    def create_branch_rule1(self,checked_vertex:Vertex)->Tuple[BranchingDecision,BranchingDecision]:
        return ImposedVertex(checked_vertex,self.a_graph),ForbidVertex(checked_vertex,self.a_graph)
    
    def check_branch_rule2(self)->bool:
        max_fraction=0
        for vertex_v in self.a_graph.vertices_map.values():
            for vertex_u in self.a_graph.vertices_map.values():
                if vertex_v.associated_partition.id == vertex_u.associated_partition.id:
                    continue
                gamma=0
                for column_id in self.solution.keys():
                    if vertex_v in column_id.vertex_set and vertex_u in column_id.vertex_set:
                        gamma+=self.solution[column_id]
                if gamma>max_fraction:
                    max_fraction=gamma
                    checked_vertex_v=vertex_v
                    checked_vertex_u=vertex_u
        if max_fraction>0:
            self.checked_vertex_v=checked_vertex_v
            self.checked_vertex_u=checked_vertex_u
            return True        
        return False
    
    def create_branch_rule2(self)->Tuple[BranchingDecision,BranchingDecision]:
        return SameColor(self.a_graph,self.checked_vertex_v,self.checked_vertex_u),DifferentColor(self.a_graph,self.checked_vertex_v,self.checked_vertex_u)