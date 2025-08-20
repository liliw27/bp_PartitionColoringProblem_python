class column_independent_set:
    """
    Class modeling an independent set in the column generation procedure.
    An independent set is a set of vertices where no two vertices are adjacent.
    Note that the fields in an independent set (except the value assigned to it by the master problem) are all final:
    an independent set should NOT be tempered with.
    """
    
    def __init__(self, columnid, vertex_set, associated_pricing_problem, is_artificial, creator):
        """
        Constructs a new independent set
        
        Args:
            vertex_set (set): Set of vertices in this independent set
            associated_pricing_problem: Pricing problem to which this independent set belongs
            is_artificial (bool): Is this an artificial independent set?
            creator (str): Who/What created this independent set?
        """
        self.vertex_set = vertex_set  # The set of vertices in this independent set
        self.value = 0.0  # The value of the independent set assigned to it by the last master problem solved
        self.is_artificial_column = is_artificial  # Indicates whether this is a real independent set or artificial
        self.creator = creator  # Textual description of the method which created this independent set
        self.associated_pricing_problem = associated_pricing_problem  # The pricing problem to which this independent set belongs
        self.iteration =0 # last iteration when the independent set was added to the master problem,used to manage the column pool
    
    def __eq__(self, other):
        """
        Compares two independent sets mutually.
        
        Args:
            other: Another independent set to compare with
            
        Returns:
            bool: True if the independent sets are equal, False otherwise
        """
        if not isinstance(other, column_independent_set):
            return False
        return (self.vertex_list == other.vertex_list and
                self.is_artificial_column == other.is_artificial_column and
                self.creator == other.creator and
                self.associated_pricing_problem == other.associated_pricing_problem)
    
    def __hash__(self):
        """
        Creates a hash code for the given independent set
        
        Returns:
            int: Hash code for the independent set
        """
        return hash((frozenset(self.vertex_list), self.is_artificial_column, self.creator, self.associated_pricing_problem))
    
    def __str__(self):
        """
        Gives a textual representation of an independent set
        
        Returns:
            str: String representation of the independent set
        """
        return f"IndependentSet(vertices={self.vertex_list}, creator={self.creator}, is_artificial={self.is_artificial_column}, value={self.value})"
