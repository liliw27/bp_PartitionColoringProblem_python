from typing import List
from model.edge import Edge
from model.vertex import Vertex

class AuxiliaryGraph:
    def __init__(self,edges:List[Edge],vertices:List[Vertex]):
        self.edges=edges
        self.get_auxiliary_edges()
        self.vertices=vertices
        self.weight_v=[]
    
        
    def _get_auxiliary_edges(self):
        for i in range(len(self.vertices)):
            for j in range(i+1,len(self.vertices)):
                if self.vertices[i].associated_partition.id == self.vertices[j].associated_partition.id:
                    self.edges.append(Edge(self.vertices[i],self.vertices[j]))
    
    def update_weightf(self,dual:List[float]):
        for vertex in self.vertices:
            self.weight_v[vertex.id]=dual[vertex.associated_partition.id]