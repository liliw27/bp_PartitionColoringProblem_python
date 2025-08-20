from typing import List
from model.Edge import Edge
from model.Vertex import Vertex
from model.Charger import Charger
from model.Partition import Partition

class ChargeProblem:
    def __init__(self,edges:List[Edge],vertices:List[Vertex],chargers:List[Charger],partitions:List[Partition]) -> None:
        self.edges = edges
        self.vertices = vertices
        self.chargers = chargers
        self.partitions = partitions
