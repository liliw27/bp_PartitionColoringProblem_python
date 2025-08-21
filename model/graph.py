from typing import List
from model.edge import Edge
from model.vertex import Vertex
from model.partition import Partition


class graph:
    def __init__(self,edges:List[Edge],vertices:List[Vertex],partitions:List[Partition]):
        self.edges=edges
        self.vertices=vertices
        self.partitions=partitions
        
        
        
        
        