from cg.pricing.pricing_problem import PricingProblem
from cg.column_pool import ColumnPool
from bpc.branching.branching_decision import BranchingDecision
import gurobipy as grb
from cg.column_independent_set import ColumnIndependentSet
import time
from model.a_graph import AuxiliaryGraph
from model.graph import Graph

class MasterProblem:
    """
    主问题（Restricted Master Problem, RMP）模型封装。

    - 负责构建“每个分区至少被染色一次”的约束；
    - 维护列（独立集）到变量的映射，并将新列增广到模型中；
    - 调用 Gurobi 求解并返回解、对偶信息以及当前目标值。
    """
    def __init__(
        self,
        graph: Graph,
        pricing_problem: PricingProblem,
        column_pool: ColumnPool,
        a_graph: AuxiliaryGraph,
    ):
        self.graph = graph
        self.pricing_problem = pricing_problem
        self.column_pool = column_pool
        self.a_graph = a_graph
        self._rmp = grb.Model("master")
        # key: 定价问题实例 → value: {列对象 → Gurobi变量}
        self.varMap = {}  # 存储定价问题到变量映射的字典
        self.dual = []  # 对偶变量列表（与分区一一对应）
        self.each_partition_colored_once_constraint = dict()
        self.solution = None
        self.objective = 0.0
        self.buildModel()

    def buildModel(self):
        """初始化求解参数并构建基础约束。"""
        self._rmp.Params.LogToConsole = 0
        self._rmp.Params.DualReductions = 0
        self._build_constraints()
        # self._add_feasible_initial_columns(self.column_pool)

    def _add_feasible_initial_columns(self, column_pool: ColumnPool):
        """（可选）为模型添加一批初始可行列。"""
        for column in column_pool.columns:
            self.add_column_to_rmp(column)

    def add_column_to_rmp(self, column_independent_set: ColumnIndependentSet):
        """将表示“独立集”的列增广到 RMP 中并创建对应变量。"""
        name = f"column_{column_independent_set.columnid}"

        c = grb.Column()
        for vertex in column_independent_set.vertex_list:
            if vertex not in self.a_graph.merged_vertices_map:
                partition_id = vertex.associated_partition.id
                constr = self.each_partition_colored_once_constraint[partition_id]
                coeff = 1.0
                c.addTerms(coeff, constr)
            else:
                merged_vertices = self.a_graph.merged_vertices_map[vertex]
                for merged_vertex in merged_vertices:
                    partition_id = merged_vertex.associated_partition.id
                    constr = self.each_partition_colored_once_constraint[partition_id]
                    coeff = 1.0
                    c.addTerms(coeff, constr)

        var = self._rmp.addVar(
            lb=0.0,
            # ub=1.0,
            obj=column_independent_set.value,
            vtype=grb.GRB.CONTINUOUS,
            name=name,
            column=c,
        )

        # 确保定价问题的键存在
        if column_independent_set.associated_pricing_problem not in self.varMap:
            self.varMap[column_independent_set.associated_pricing_problem] = {}
        
        # 使用列的字符串表示作为键
        
        self.varMap[column_independent_set.associated_pricing_problem][column_independent_set] = var
        # self.column_pool.addColumn(column_independent_set)

    def _build_constraints(self):
        """构建每个分区至少/恰好一次被染色的基础约束骨架。"""
        partition_number = len(self.graph.partitions)
        # 构建每个partition被染色一次的约束
        for partition_id in range(partition_number):
            lhs = grb.quicksum([])
            rhs = 1
            name = f"each_partition_colored_once_constraint{partition_id}"
            c = self._rmp.addConstr(lhs >= rhs, name=name)
            self.each_partition_colored_once_constraint[partition_id] = c

    def solveMaster(self, time_end: int):
        """求解主问题并返回（解、对偶、目标值）。"""
        # 设置求解器参数
        self._rmp.Params.DualReductions = 0  # 禁用对偶约减

        # 提高求解精度
        self._rmp.Params.OptimalityTol = 1e-9
        self._rmp.Params.FeasibilityTol = 1e-9
        self._rmp.Params.BarConvTol = 1e-9

        # 强制使用数值稳定的求解方法
        self._rmp.Params.Method = 1  # 强制使用对偶单纯形法（更稳定）
        # # 或者
        # self.model.Params.Method = 2  # 内点法（更适合病态问题）

        # 设置时间限制
        time_limit = time_end - time.time()
        self._rmp.Params.TimeLimit = time_limit

        self._rmp.update()

        # 在优化前导出模型（调试/排错用）
        self._rmp.write("model_info/master.lp")

        try:
            self._rmp.setObjective(self._rmp.getObjective(), grb.GRB.MINIMIZE)
            self._rmp.optimize()
        except grb.GurobiError as e:
            # 将求解器异常直接抛出
            raise e

        # 根据求解状态处理结果
        if self._rmp.status == grb.GRB.OPTIMAL:
            # 获取解
            self.solution = {}
            for pricing_problem, var_dict in self.varMap.items():
                for col, var in var_dict.items():
                    if var.X > 1e-6:  # 只保存非零解
                        self.solution[col] = var.X
            # 获取对偶变量（假设约束顺序与添加顺序一致）
            self._get_dual_variables()

            return self.solution, self.dual, self._rmp.ObjVal
        elif self._rmp.status == grb.GRB.INFEASIBLE:
            raise grb.GurobiError(grb.GRB.INFEASIBLE, "Master problem is infeasible")
        elif self._rmp.status == grb.GRB.INF_OR_UNBD:
            raise grb.GurobiError(
                grb.GRB.INF_OR_UNBD, "Master problem is infeasible or unbounded"
            )
        elif self._rmp.status == grb.GRB.UNBOUNDED:
            raise grb.GurobiError(grb.GRB.UNBOUNDED, "Master problem is unbounded")
        elif self._rmp.status == grb.GRB.TIME_LIMIT:
            # 时间限制达到但未找到最优解
            if self._rmp.SolCount > 0:  # 有可行解
                self.solution = {}
                for pricing_problem, var_dict in self.varMap.items():
                    for col_id, var in var_dict.items():
                        if var.X > 1e-6:  # 只保存非零解
                            self.solution[col_id] = var.X
                self._get_dual_variables()
                return self.solution, self.dual, self._rmp.ObjVal
            else:
                raise grb.GurobiError(
                    grb.GRB.TIME_LIMIT, "Time limit reached without solution"
                )
        else:
            # 其他未处理状态
            status_name = self._rmp.status
            raise RuntimeError(f"Master problem solve failed with status {status_name}")

    def _get_dual_variables(self):
        """提取每个分区对应的对偶变量值（影子价格）。"""
        self.dual = []
        for partition_id in range(len(self.graph.partitions)):
            self.dual.append(
                self.each_partition_colored_once_constraint[partition_id].Pi
            )
