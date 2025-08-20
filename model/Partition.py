from typing import Set


class Partition:
    def __init__(self, id: int, vetex_set: Set):
        """Initialize a Partition object

        Args:
            vetex_set: Set of vertices in the partition
        """
        self.id = id
        self.vetex_set = vetex_set
