from PricingProblem import PricingProblem
from ...model import ChargeProblem
from ...bpc.branching.BranchingDecision import BranchingDecision
class PricingProblemSolver:
    solution=None

    def __init__(self,data_model:ChargeProblem, pricing_problem: PricingProblem):
        self.pricing_problem = pricing_problem

    def buildModel(self):
        #todo: build the model
        pass

    def solve(self):
        #todo: solve the model
        pass

    def setObjective(self,dualcosts:dict):
        pass

    def generateColumns(self,dualcosts:dict):
        self.setObjective(dualcosts)
        self.solve()
        columns=self.get_solution()
        return columns
    
    def branchPerformed(self,branchingDecision:BranchingDecision):
        pass

    def branchReversed(self,branchingDecision:BranchingDecision):
        pass
    
    def get_solution(self):
        return self.solution
    