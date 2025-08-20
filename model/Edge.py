class Edge:
    def __init__(self, source, target, weight=1.0):
        self.source = source
        self.target = target
        self.weight = weight
        
        # Add each vertex to the other's adjacent vertices
        source.add_adjacent_vertex(target)
        target.add_adjacent_vertex(source)
    
    def get_source(self):
        """
        Gets the source vertex of the edge
        
        Returns:
            Vertex: The source vertex
        """
        return self.source
    
    def get_target(self):
        """
        Gets the target vertex of the edge
        
        Returns:
            Vertex: The target vertex
        """
        return self.target
    
    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return ((self.source == other.source and self.target == other.target) or
                (self.source == other.target and self.target == other.source))
    
    def __hash__(self):
        # Use a tuple of sorted vertex ids to ensure same hash regardless of order
        return hash(tuple(sorted([self.source.id, self.target.id])))
    
    def __str__(self):
        return f"Edge({self.source.id} -> {self.target.id}, weight={self.weight})"