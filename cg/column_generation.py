from cg.master.master_problem import Master
from cg.pricing.pricing_problem import PricingProblem
from cg.column_pool import ColumnPool
from ..model.charge_problem import ChargeProblem
from ..config import Config
import time
import math
class ColGen:
    def __init__(self,instance:ChargeProblem,master:Master,pricing_problems:list[PricingProblem],column_pool:ColumnPool):
        self.master = master
        self.pricing_problems = pricing_problems
        self.column_pool = column_pool
        self.upper_bound = float('inf')
        self.lower_bound = 0.0
        self.instance = instance
        self.masterSolveTime=0
        self.pricingSolveTime=0
        self.masterObjective=0.0
  

    def solve(self,time_limit:int):
        foundNewColumn = True
        while foundNewColumn:
            self.invokeMaster(time_limit)
            if math.ceil(self.masterObjective-self.instance.config.epsilon)>=self.upper_bound:
                break
            if abs(self.masterObjective - self.lower_bound) < self.instance.config.epsilon:
                break
            self.invokePricing(time_limit)
            if self.pricingObjective < self.lower_bound:
                self.lower_bound = self.pricingObjective
            if abs(self.pricingObjective - self.upper_bound) < self.instance.config.epsilon:
                break
    
    def invokeMaster(self,time_limit:int):
        self.master.solveMaster(time_limit)
        self.masterSolveTime += time.time() - self.masterSolveTime
        self.masterObjective = self.master.getObjective()