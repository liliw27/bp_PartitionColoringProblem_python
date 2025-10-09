from cg.pricing.pricing_problem import PricingProblem
from cg.column_pool import ColumnPool
from model import charge_problem
from bpc.branching.branching_decision import BranchingDecision
import gurobipy as grb
from bidict import bidict
from cg.column_independent_set import ColumnIndependentSet
import time
from model.a_graph import AuxiliaryGraph
from model.graph import Graph

class MasterProblem:
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
        self.varMap = {}  # 存储定价问题到变量映射的字典
        self.dual = []  # 对偶变量列表
        self.each_partition_colored_once_constraint = dict()
        self.solution = None
        self.objective = 0.0

    def buildModel(self):
        self._rmp.Params.LogToConsole = 0
        self._rmp.Params.DualReductions = 0
        self._build_constraints()
        # self._add_feasible_initial_columns(self.column_pool)

    def _add_feasible_initial_columns(self, column_pool: ColumnPool):
        for column in column_pool.columns:
            self.add_column_to_rmp(column)

    def add_column_to_rmp(self, column_independent_set: ColumnIndependentSet):
        """
        Adds a column that represents `independent set` to RMP.
        It does so by creating variable and adding to Gurobi problem/model.

        :param column: independent set
        """
        name = f"column_{column_independent_set.columnid}"

        c = grb.Column()
        for vertex in column_independent_set.vertex_set:
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
        partition_number = len(self.graph.partitions)
        # 构建每个partition被染色一次的约束
        for partition_id in range(partition_number):
            lhs = grb.quicksum([])
            rhs = 1
            name = f"each_partition_colored_once_constraint{partition_id}"
            c = self._rmp.addConstr(lhs >= rhs, name=name)
            self.each_partition_colored_once_constraint[partition_id] = c

    def solveMaster(self, time_end: int):
        """
        求解主问题并返回结果
        :return:
        """
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

        # 在优化前导出模型（调试用）
        self._rmp.write("model_info/master.lp")

        try:
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

            # # 验证结果（调试用）
            # print("============================= test ======================================")
            # self._verify_solution()  # 验证主问题解
            # print("============================= test ======================================")
            # self._verify_duals()  # 验证对偶变量
            # self._verify_column_rc(duals=duals)  # 验证列 reduced cost

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
        self.dual = []
        for partition_id in range(len(self.graph.partitions)):
            self.dual.append(
                self.each_partition_colored_once_constraint[partition_id].Pi
            )

    def branchPerformed(self, branchingDecision: BranchingDecision):
        self.updateModel(branchingDecision)

    def branchReversed(
        self, branchingDecision: BranchingDecision
    ):  # todo: check if this is correct
        pass

    def updateModel(self, branchingDecision: BranchingDecision):
        pass

    def reverseModel(self, branchingDecision: BranchingDecision):
        pass


    def getSolution(self):
        pass
