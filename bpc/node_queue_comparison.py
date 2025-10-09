"""
分支定价算法中不同队列策略的比较
"""
import heapq
from collections import deque
from typing import List
from bpc.bpc_node import BPCNode

class QueueStrategy:
    """队列策略基类"""
    def add_node(self, node: BPCNode):
        raise NotImplementedError
    
    def get_next_node(self) -> BPCNode:
        raise NotImplementedError
    
    def is_empty(self) -> bool:
        raise NotImplementedError

class FIFOQueue(QueueStrategy):
    """先进先出队列（广度优先）"""
    def __init__(self):
        self.queue = deque()
    
    def add_node(self, node: BPCNode):
        self.queue.append(node)
    
    def get_next_node(self) -> BPCNode:
        return self.queue.popleft() if self.queue else None
    
    def is_empty(self) -> bool:
        return len(self.queue) == 0

class LIFOQueue(QueueStrategy):
    """后进先出队列（深度优先）"""
    def __init__(self):
        self.stack = []
    
    def add_node(self, node: BPCNode):
        self.stack.append(node)
    
    def get_next_node(self) -> BPCNode:
        return self.stack.pop() if self.stack else None
    
    def is_empty(self) -> bool:
        return len(self.stack) == 0

class PriorityQueue(QueueStrategy):
    """优先队列（最佳优先）"""
    def __init__(self):
        self.heap = []
    
    def add_node(self, node: BPCNode):
        heapq.heappush(self.heap, node)
    
    def get_next_node(self) -> BPCNode:
        return heapq.heappop(self.heap) if self.heap else None
    
    def is_empty(self) -> bool:
        return len(self.heap) == 0

# 使用示例
def demonstrate_strategies():
    """演示不同队列策略的效果"""
    
    # 创建测试节点
    test_nodes = [
        BPCNode(objective_value=10.5),
        BPCNode(objective_value=3.2),
        BPCNode(objective_value=8.1),
        BPCNode(objective_value=2.8),
        BPCNode(objective_value=15.0),
    ]
    
    strategies = {
        "FIFO (广度优先)": FIFOQueue(),
        "LIFO (深度优先)": LIFOQueue(),
        "优先队列 (最佳优先)": PriorityQueue(),
    }
    
    print("=" * 60)
    print("不同队列策略处理顺序对比")
    print("=" * 60)
    print("输入节点目标值:", [node.objective_value for node in test_nodes])
    print()
    
    for name, strategy in strategies.items():
        # 添加所有节点
        for node in test_nodes:
            strategy.add_node(node)
        
        # 按策略顺序处理
        processing_order = []
        while not strategy.is_empty():
            node = strategy.get_next_node()
            processing_order.append(node.objective_value)
        
        print(f"{name:20}: {processing_order}")
    
    print("\n分析:")
    print("• FIFO: 按添加顺序处理，公平但可能低效")
    print("• LIFO: 深度优先，内存友好但可能错过好解")
    print("• 优先队列: 优先处理有希望的节点，通常最高效 ⭐")

if __name__ == "__main__":
    demonstrate_strategies()
