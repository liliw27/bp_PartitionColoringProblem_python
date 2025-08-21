from typing import Set

from model.partition import Partition


class Vertex:
    def __init__(self, id, data,adjacent_vertices:Set,associated_partition:Partition):
        self.id = id
        self.data = data
        self.adjacent_vertices = adjacent_vertices
        self.associated_partition=associated_partition
    
    def add_adjacent_vertex(self, vertex):
        self.adjacent_vertices.add(vertex)
    
    def remove_adjacent_vertex(self, vertex):
        self.adjacent_vertices.discard(vertex)
    
    def is_adjacent_to(self, vertex):
        return vertex in self.adjacent_vertices
    
    def __eq__(self, other):
        if not isinstance(other, Vertex):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def __str__(self):
        return f"Vertex(id={self.id}, data={self.data})"
