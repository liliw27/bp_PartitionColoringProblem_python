from typing import List
from model.edge import Edge
from model.vertex import Vertex
from model.charger import Charger
from model.partition import Partition

class ChargeProblem:
    def __init__(self,edges:List[Edge],vertices:List[Vertex],chargers:List[Charger],partitions:List[Partition]) -> None:
        self.edges = edges
        self.vertices = vertices
        self.chargers = chargers
        self.partitions = partitions
