from typing import Set


class Partition:
    def __init__(self, id: int, vertex_set: Set):
        """Initialize a Partition object

        Args:
            vertex_set: Set of vertices in the partition
        """
        self.id = id
        self.vertex_set = vertex_set
