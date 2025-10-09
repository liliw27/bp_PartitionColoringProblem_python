"""
分支定价算法主类
"""
import heapq
from typing import List, Optional, Dict, Any
from model.a_graph import AuxiliaryGraph
from bpc.branching.branching_decision import BranchingDecision
from bpc.bpc_node import BPCNode
from cg.column_generation import ColumnGeneration
from cg.pricing.pricing_problem import PricingProblem
from cg.pricing.exact_pricing_solver import ExactPricingSolver
from cg.master.master_problem import MasterProblem
from bpc.branch_creator import BranchCreator
from cg.column_independent_set import ColumnIndependentSet
from model.graph import Graph
from cg.column_pool import ColumnPool
import math
import gurobipy

class BranchAndPrice:
    """
    分支定价算法实现
    
    使用优先队列管理分支节点，按照目标值（下界）从小到大处理节点。
    这样可以优先处理最有希望的节点，提高算法效率。
    """
    
    def __init__(self, graph: Graph, time_limit: int):
        """
        初始化分支定价算法
        
        Args:
            graph: 原始图对象
            time_limit: 时间限制（秒）
        """
        self.graph = graph
        self.time_limit = time_limit
        
        # 使用最小堆作为优先队列，按objective_value排序
        self.node_queue: List[BPCNode] = []
        
        # 算法状态跟踪
        self.best_solution: Optional[Dict[str, Any]] = None
        self.best_objective: float = float('inf')  # 上界
        self.global_lower_bound: float = float('-inf')  # 全局下界
        self.optimal: bool = False
        
        # 统计信息
        self.nodes_processed: int = 0
        self.nodes_created: int = 0
        self.nodes_pruned: int = 0
        self.total_solve_time: float = 0.0
        
        

    def solve(self) -> Dict[str, Any]:
        """
        执行分支定价算法
        
        Returns:
            求解结果字典
        """
        import time
        start_time = time.time()
        time_end = start_time + self.time_limit
        
        print("开始分支定价算法...")
        print(f"时间限制: {self.time_limit}秒")
        
        # 生成并添加根节点
        root_node = self.generate_root_node()
        self.add_node(root_node)
        print(f"根节点已添加: ID={root_node.nodeid}")
        try:
            while not self.is_queue_empty():
                # 获取下一个要处理的节点
                current_node = self.get_next_node()
                self.nodes_processed += 1
                
                print(f"\n处理节点 {current_node.nodeid}: 下界={current_node.objective_value:.4f}")
                
                # 1. 检查是否可以剪枝，如果当前节点下界大于等于全局上界，则剪枝
                if self.is_prunable_node(current_node):
                    continue
                
                # 2. 求解当前节点的线性松弛问题（列生成）
                if not self.process_node(current_node, time_end):
                    self.add_node(current_node)
                    break  # 如果时间超限，则跳出循环
                    
                print(f"  列生成求解结果: 目标值={current_node.objective_value:.4f}")
                
                # 3. 再次检查剪枝条件（求解后目标值可能改变）
                if self.is_prunable_node(current_node):
                    continue
                    
                # 4. 检查是否不可行，如果解中存在人工列，则剪枝
                if self.is_infeasible_solution(current_node):
                    print("  剪枝: 解中存在人工列")
                    self.nodes_pruned += 1
                    continue
                    
                # 5. 检查解的整数性
                if self.is_integer_solution(current_node.solution):
                    # 如果是整数解，更新最优解
                    print("  找到整数解，更新最优解")
                    self.update_best_solution(current_node.objective_value, current_node.solution)
                    continue
                else:
                    # 如果不是整数解，进行分支
                    print("  解不是整数，开始分支...")
                    self.branch_node(current_node)
                
                # # 更新全局下界
                # active_nodes_bounds = [node.objective_value for node in self.node_queue]
                # if active_nodes_bounds:
                #     self.global_lower_bound = min(active_nodes_bounds)
                                    
                # 每处理一定数量的节点输出进度
                if self.nodes_processed % 10 == 0:
                    stats = self.get_statistics()
                    print(f"  进度: 已处理 {stats['nodes_processed']} 个节点, "
                          f"剩余 {stats['nodes_remaining']} 个, "
                          f"当前最优 {stats['best_objective']:.4f}")
            
            self.total_solve_time = time.time() - start_time
            
            # 更新全局下界
            self.update_global_lower_bound()
            
            # 输出最终结果
            stats = self.get_statistics()
            print(f"\n{'='*50}")
            print("分支定价算法完成!")
            print(f"{'='*50}")
            print(f"最优目标值: {stats['best_objective']:.6f}")
            print(f"全局下界: {stats['global_lower_bound']:.6f}")
            print(f"优化间隙: {stats['gap']:.4%}")
            print(f"处理节点数: {stats['nodes_processed']}")
            print(f"创建节点数: {stats['nodes_created']}")
            print(f"剪枝节点数: {stats['nodes_pruned']}")
            print(f"总求解时间: {stats['total_solve_time']:.2f}秒")
            
            return {
                "status": "optimal" if self.best_solution else "no_solution",
                "objective_value": self.best_objective,
                "solution": self.best_solution,
                "statistics": stats
            }
            
        except Exception as e:
            self.total_solve_time = time.time() - start_time
            print(f"求解过程中出现错误: {e}")
            return {
                "status": "error",
                "error": str(e),
                "statistics": self.get_statistics()
            }
    
    def branch_node(self, current_node: BPCNode) -> None:
        """
        对当前节点进行分支
        
        Args:
            current_node: 需要分支的节点
        """
        branch_creator = BranchCreator(
            current_node.solution, 
            current_node.column_pool, 
            current_node.a_graph
        )
        branches = branch_creator.create_branch()
        
        print(f"  创建了 {len(branches)} 个分支")
        for i, branch in enumerate(branches):
            # 复制当前节点的图和列池
            a_graph = current_node.a_graph.copy()
            branch.a_graph_update(a_graph)
            
            column_pool = current_node.column_pool.copy()
            branch.column_filter(column_pool)
            
            # 创建新的分支节点
            new_node = BPCNode(
                parent=current_node,
                a_graph=a_graph,
                column_pool=column_pool,
                objective_value=current_node.objective_value,
                solution=current_node.solution
            )
            self.add_node(new_node)
            print(f"    添加分支节点 {i+1}: ID={new_node.nodeid}")
    
    def process_node(self, current_node: BPCNode, time_end: float) -> bool:
        """
        处理当前节点：求解线性松弛问题
        
        Args:
            current_node: 当前节点
            time_end: 结束时间
            
        Returns:
            是否成功处理（False表示超时）
        """
        print("  开始列生成求解...")
        
        # 创建求解组件
        pricing_problem = PricingProblem(auxiliary_graph=current_node.a_graph, name="main_pricing", dualcosts=[])
        master_problem = MasterProblem(graph=self.graph, pricing_problem=pricing_problem, column_pool=current_node.column_pool, a_graph=current_node.a_graph)
        pricing_solver = ExactPricingSolver(current_node.a_graph,pricing_problem=pricing_problem)
        column_generation = ColumnGeneration(
            master_problem, 
            pricing_problem, 
            pricing_solver, 
            current_node.column_pool,
            self.best_objective, 
            self.global_lower_bound
        )
        
        try:
            current_node.solution, current_node.objective_value = column_generation.solve(time_end)
            return True
        except gurobipy.GurobiError as e:
            if e.errno == 10001:  # Gurobi timeout error code
                print("  列生成求解超时")
                self.nodes_pruned += 1
                return False
            else:
                raise e
    
    def is_prunable_node(self, current_node: BPCNode) -> bool:
        """
        检查节点是否可以剪枝
        
        Args:
            current_node: 当前节点
            
        Returns:
            是否可以剪枝
        """
        if math.ceil(current_node.objective_value) >= self.best_objective:
            print(f"  剪枝: {math.ceil(current_node.objective_value)} >= {self.best_objective:.4f}")
            self.nodes_pruned += 1
            return True
        return False
    
    def update_global_lower_bound(self) -> None:
        """
        更新全局下界
        """
        if len(self.node_queue) == 0:
            self.optimal = True
            self.global_lower_bound = self.best_objective
            print("所有节点已处理完毕，达到最优解")
        else:
            self.optimal = False
            active_nodes_bounds = [node.objective_value for node in self.node_queue]
            if active_nodes_bounds:
                self.global_lower_bound = min(active_nodes_bounds)
            print(f"算法终止，剩余 {len(self.node_queue)} 个未处理节点")
    
    def is_infeasible_solution(self, current_node: BPCNode) -> bool:
        """
        检查解是否不可行（包含人工列）
        
        Args:
            current_node: 当前节点
            
        Returns:
            解是否不可行
        """
        if not current_node.solution:
            return True
            
        return any(
            column_independent_set.is_artificial_column 
            for column_independent_set in current_node.solution.keys()
        )
    
    def generate_root_node(self) -> BPCNode:
        """
        生成根节点
        
        Returns:
            初始的根节点，包含原始图和空的列池
        """
        
        # 创建空的列池作为根节点的初始状态
        a_graph = self._create_auxiliary_graph()
        root_column_pool=self._add_artificial_columns(a_graph)
        return BPCNode(
            parent=None, 
            a_graph=a_graph, 
            column_pool=root_column_pool, 
            objective_value=float('-inf'),  # 根节点下界设为负无穷
            solution={}
        )
    
    def _create_auxiliary_graph(self) -> AuxiliaryGraph:
        """
        创建辅助图
        
        Returns:
            辅助图对象
        """
        # 创建顶点映射
        
        
        return AuxiliaryGraph(
            graph=self.graph,
            vertices_map=self.graph.vertex_map,
            auxiliary_edges=None,
            merged_vertices_map=None
        )
    
    def _add_artificial_columns(self, a_graph: AuxiliaryGraph) -> ColumnPool:
        """
        为每个分区添加人工列以确保主问题可行
        
        Args:
            a_graph: 辅助图
            
        Returns:
            包含人工列的列池
        """
        root_column_pool = ColumnPool()
        
        for partition in self.graph.partitions:
            # 为每个分区中的每个顶点创建单顶点人工列
            vertex=self.graph.vertex_map[partition.vertex_set[0]]
            
            artificial_column = ColumnIndependentSet(
                vertex_set={vertex},
                associated_pricing_problem="artificial",
                is_artificial=True,
                creator="artificial_initialization",
                value=1000.0  # 高代价确保只在必要时使用
            )
            root_column_pool.addColumn(artificial_column)
        
        return root_column_pool

    
    def is_integer_solution(self, solution: Dict[ColumnIndependentSet, Any]) -> bool:
        """
        检查解是否为整数解
        
        Args:
            solution: 待检查的解
            
        Returns:
            解是否为整数解
        """
        if not solution:
            return False
            
        tolerance = 1e-6
        
        # 检查所有变量值是否接近整数
        for column_independent_set, value in solution.items():
            if isinstance(value, (int, float)):
                # 检查是否接近0或1（二进制变量）
                if not (abs(value - 0) < tolerance or abs(value - 1) < tolerance):
                    print(f"    非整数变量: {column_independent_set.readable_name} = {value:.6f}")
                    return False
            
        return True
    
    def update_cg_solver(self, node: BPCNode) -> None:
        """
        更新列生成求解器（预留方法）
        
        Args:
            node: 当前节点
        """
        # TODO: 如果需要重用列生成求解器，在这里更新
        pass
    
    def add_node(self, node: BPCNode) -> None:
        """
        向优先队列添加节点
        
        Args:
            node: 要添加的分支节点
        """
        heapq.heappush(self.node_queue, node)
        self.nodes_created += 1
        
    def get_next_node(self) -> Optional[BPCNode]:
        """
        从优先队列中取出目标值最小的节点
        
        Returns:
            目标值最小的节点，如果队列为空则返回None
        """
        if self.node_queue:
            return heapq.heappop(self.node_queue)
        return None
        
    def is_queue_empty(self) -> bool:
        """
        检查队列是否为空
        
        Returns:
            队列是否为空
        """
        return len(self.node_queue) == 0
        
    def queue_size(self) -> int:
        """
        获取队列中节点数量
        
        Returns:
            队列中的节点数量
        """
        return len(self.node_queue)
    
    def prune_nodes(self) -> int:
        """
        剪枝：移除下界大于等于当前最优解的节点
        
        Returns:
            被剪枝的节点数量
        """
        if self.best_objective == float('inf'):
            return 0
            
        pruned_count = 0
        remaining_nodes = []
        
        # 重新构建队列，只保留有希望的节点
        while self.node_queue:
            node = heapq.heappop(self.node_queue)
            if node.objective_value < self.best_objective:
                remaining_nodes.append(node)
            else:
                pruned_count += 1
        
        # 重新建堆
        self.node_queue = remaining_nodes
        heapq.heapify(self.node_queue)
        
        self.nodes_pruned += pruned_count
        return pruned_count
    
    def update_best_solution(self, objective_value: float, solution: Dict[str, Any]) -> bool:
        """
        更新最优解
        
        Args:
            objective_value: 新的目标值
            solution: 新的解
            
        Returns:
            是否更新了最优解
        """
        if objective_value < self.best_objective:
            self.best_objective = objective_value
            self.best_solution = solution.copy()
            
            # 更新后进行剪枝
            pruned = self.prune_nodes()
            if pruned > 0:
                print(f"  更新最优解后剪枝了 {pruned} 个节点")
            
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取算法运行统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "nodes_processed": self.nodes_processed,
            "nodes_created": self.nodes_created,
            "nodes_pruned": self.nodes_pruned,
            "nodes_remaining": self.queue_size(),
            "best_objective": self.best_objective,
            "global_lower_bound": self.global_lower_bound,
            "gap": (self.best_objective - self.global_lower_bound) / max(abs(self.best_objective), 1e-6),
            "total_solve_time": self.total_solve_time
        }