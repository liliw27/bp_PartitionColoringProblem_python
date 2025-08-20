from cg.pricing.PricingProblem import PricingProblem
from cg.ColumnPool import ColumnPool
from ...model import ChargeProblem
from ...bpc.branching.BranchingDecision import BranchingDecision
import gurobipy as grb
from bidict import bidict
from cg.column_independent_set import column_independent_set


class Master:
    def __init__(
        self,
        data_model: ChargeProblem,
        pricing_problems: list[PricingProblem],
        column_pool: ColumnPool,
    ):
        self.data_model = data_model
        self.pricing_problems = pricing_problems
        self.column_pool = column_pool
        self.model = grb.Model("master")
        self.varMap = dict[PricingProblem, bidict[column_independent_set, grb.Var]]
        self.dualcosts = dict[str, list[float]]
        self.each_partition_colored_once_constraint = dict()
        self.solution = None
        self.objective = 0.0

    def buildModel(self):
        self._rmp.Params.LogToConsole = 0
        self._rmp.Params.DualReductions = 0
        self._build_constraints()
        self._add_feasible_initial_columns(self.column_pool)

    def _add_feasible_initial_columns(self, column_pool: ColumnPool):
        for column in column_pool:
            self._add_column_to_rmp(column)

    def _add_column_to_rmp(self, column_independent_set: column_independent_set):
        """
        Adds a column that represents `independent set` to RMP.
        It does so by creating variable and adding to Gurobi problem/model.

        :param column: independent set
        """
        name = f"column_{column_independent_set.columnid}"

        c = grb.Column()
        for vertex in column_independent_set.vertex_set:
            partition_id = vertex.associated_partition.id
            constr = self.each_partition_colored_once_constraint[partition_id]
            coeff = 1.0
            c.addTerms(coeff, constr)

        var = self._rmp.addVar(
            lb=0.0,
            # ub=1.0,
            obj=1,
            vtype=grb.GRB.CONTINUOUS,
            name=name,
            column=c,
        )

        self.varMap[column_independent_set.associated_pricing_problem][
            column_independent_set
        ] = var

    def _build_constraints(self):
        partition_number = len(self.data_model.partition)
        # 构建每个partition被染色一次的约束
        for partition_id in range(partition_number):
            lhs = grb.quicksum([])
            rhs = 1
            name = f"each_partition_colored_once_constraint{partition_id}"
            c = self.model.addConstr(lhs >= rhs, name=name)
            self.each_partition_colored_once_constraint[partition_id] = c

    def solveMaster(self, time_limit: int):
        pass

    def addVariable(
        self, pricingProblem: PricingProblem, column: column_independent_set
    ):
        pass

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

    def updateDualCosts(
        self, pricingProblem: PricingProblem, dualcosts: dict[str, float]
    ):
        pass

    def getSolution(self):
        pass
