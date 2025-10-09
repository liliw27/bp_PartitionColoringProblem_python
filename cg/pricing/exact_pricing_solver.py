from cg.column_independent_set import ColumnIndependentSet
from cg.pricing.pricing_problem import PricingProblem
from bpc.branching.branching_decision import BranchingDecision
import gurobipy as grb
from typing import Dict
from model.a_graph import AuxiliaryGraph
import time

class ExactPricingSolver:
    solution = None

    def __init__(
        self, auxiliary_graph: AuxiliaryGraph, pricing_problem: PricingProblem
    ):
        self.pricing_problem = pricing_problem
        self.auxiliary_graph = auxiliary_graph
        self.model = grb.Model("sub")
        self.vars: Dict[int, grb.Var] = {}
        self.cons = {}
        self.pool_sol_num = 5
        self.build_model()
        self.dual = pricing_problem.dualcosts

    def build_model(self):
        # 决策变量
        for v in self.auxiliary_graph.vertices:
            self.vars[v.id] = self.model.addVar(vtype=grb.GRB.BINARY, name=f"x_{v.id}")

        # 约束条件
        for edge in self.auxiliary_graph.auxiliary_edges:
            u = edge.source
            v = edge.target
            self.cons[(u.id, v.id)] = self.model.addConstr(
                self.vars[u.id] + self.vars[v.id] <= 1, name=f"cons_({u.id},{v.id})"
            )

        # 目标函数
        obj_expr = grb.LinExpr()

        obj_expr += sum(
            self.auxiliary_graph.weight_v[v.id] * self.vars[v.id]
            for v in self.auxiliary_graph.vertices
        )

        self.model.setObjective(1 - obj_expr, grb.GRB.MINIMIZE)

    def solve(self,time_end:int):
        # 设置 model 参数：使用解池存储多个可行解
        self.model.setParam("PoolSearchMode", 2)  # 系统搜索多个解
        self.model.setParam("PoolSolutions", self.pool_sol_num)  # 最大存储解数量

        # 设置求解器参数
        self.model.setParam("OutputFlag", 0)  # 关闭求解器输出
        time_limit = time_end - time.time()
        self.model.setParam("TimeLimit", time_limit)  # 30秒时间限制

        self.model.update()
        # 求解
        self.model.optimize()

    def set_objective(self):
        obj_expr = grb.LinExpr()
        obj_expr += sum(
            self.auxiliary_graph.weight_v[v.id] * self.vars[v.id]
            for v in self.auxiliary_graph.vertices
        )
        self.model.setObjective(obj_expr, grb.GRB.MAXIMIZE)

    def generate_columns(self,time_end:int):
        # 设置目标函数
        self.set_objective()

        # 构建和求解子问题
        self.solve(time_end)

        # 处理解池中的解，获取reduced cost < 0的多个可行列
        columns = []

        # 检查是否有解
        if self.model.status != grb.GRB.OPTIMAL and self.model.SolCount == 0:
            return columns

        # 获取解池中的解数量
        solution_num = self.model.SolCount

        # 遍历解池中所有解
        for i in range(solution_num):
            # 设置当前解的索引
            self.model.setParam(grb.GRB.Param.SolutionNumber, i)

            # 获取当前解的目标值
            obj_val = self.model.PoolObjVal

            # 只考虑减少成本为负的解
            if obj_val < 1.0+1e-6:  # 考虑数值误差
                continue

            # 提取稳定集（值为1的节点）
            stable_set = set()
            for v, var in self.vars.items():
                if abs(var.Xn - 1.0) < 1e-6:  # 检查是否为1
                    stable_set.add(self.auxiliary_graph.vertices_map[v])

            # 创建列对象
            new_column = ColumnIndependentSet(
                vertex_set=stable_set,
                value=1,
                associated_pricing_problem=self.pricing_problem,
                is_artificial=False,
                creator="Exact Pricing Solver",
            )

            columns.append(new_column)

            # 手动计算 reduced cost
            self._update_dual()
            manual_rc = self._calculate_reduced_cost(new_column)

            # print(f"**** Column={new_column.stable_set}, calculate reduced cost={manual_rc} ****")

            # 验证 reduced cost 一致性
            if abs((1.0-obj_val) - manual_rc) > 1e-5:
                raise RuntimeError(
                    f"Reduced cost 不一致: "
                    f"子问题报告={obj_val:.6f}, "
                    f"手动计算={manual_rc:.6f}, "
                    f"差异={abs(obj_val - manual_rc):.6f}"
                )
        return columns
    def _update_dual(self):
        self.dual = self.pricing_problem.dualcosts
    def _calculate_reduced_cost(self, column: ColumnIndependentSet) -> float:
        """
        手动计算 reduced cost
        :param column:
        :return:
        """
        dual_contrib = 0
        for v in column.vertex_set:
            vertex=self.auxiliary_graph.vertices[v]
            dual_contrib += self.dual[vertex.associated_partition.id]
        rc = 1.0 - dual_contrib

        # 根据数学模型计算 reduced cost
        return rc

    def branchPerformed(self, branchingDecision: BranchingDecision):
        pass

    def branchReversed(self, branchingDecision: BranchingDecision):
        pass

    def get_solution(self):
        return self.solution
