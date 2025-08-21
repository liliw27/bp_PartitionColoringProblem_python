from ...model import ChargeProblem
from ...bpc.branching.branching_decision import BranchingDecision
from typing import List

"""
This module contains the PricingProblem class which represents a pricing problem in column generation.
The pricing problem is responsible for generating new columns (independent sets) with negative reduced cost.
It maintains the dual costs from the master problem and handles branching decisions.
"""

class pricing_problem:
    def __init__(self, data_model: ChargeProblem, name : str,dualcosts:dict):
        self.data_model = data_model
        self.name = name
        self.dualcosts = dualcosts
    
    # def initPricingProblem(self,dualcosts):
    #     self.dualcosts = dualcosts

    def branchingDecisionPerformed(self,branchingDecision:BranchingDecision):
        pass
    
    def update_dual(self,dual:List[float]):
        self.dualcosts=dual

    def __str__(self):
        return f"PricingProblem(name={self.name})"

    def __repr__(self):
        return f"PricingProblem(name={self.name})"
