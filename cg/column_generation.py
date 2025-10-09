from cg.master.master_problem import MasterProblem
from cg.pricing.pricing_problem import PricingProblem
from cg.pricing.exact_pricing_solver import ExactPricingSolver
from cg.column_pool import ColumnPool
from config import config

import time
import math
from typing import List
from cg.column_independent_set import ColumnIndependentSet


class ColumnGeneration:
    def __init__(
        self,
        master: MasterProblem,
        pricing_problem: PricingProblem,
        pricing_solver: ExactPricingSolver,
        column_pool: ColumnPool,
        upper_bound: float,
        lower_bound: float
    ):
        self.master = master
        self.pricing_problem = pricing_problem
        self.pricing_solver = pricing_solver
        self.column_pool = column_pool
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.lower_bound = 0.0
        self.masterSolveTime = 0
        self.dual: List[float] = []
        self.pricingSolveTime = 0
        self.masterObjective = 0.0
        self.iteration = 0
        self.solution = None
        self.new_columns = []
    def solve(self, time_end: int):
        foundNewColumn = True
        self.new_columns = self.column_pool.columns
        while foundNewColumn:
            self.iteration += 1
            self.invokeMaster(self.new_columns,time_end)
            if self.check_termination():
                break
            
            new_columns = self.invokePricing(time_end, self.dual)
            self.new_columns = new_columns
            for column in new_columns:
                self.column_pool.addColumn(column)
            foundNewColumn = len(new_columns) > 0
        self.solution = self.master.solution
        return self.solution,self.masterObjective
    
    def check_termination(self):
        if (
                math.ceil(self.masterObjective - config.epsilon)
                >= self.upper_bound
            ):
                return True
            
        if (
                abs(self.masterObjective - self.lower_bound)
                < config.epsilon
            ):
                return True
            
    def invokeMaster(self,new_columns:List[ColumnIndependentSet], time_end: int):
        c_time = time.time()
        for column in new_columns:
            self.master.add_column_to_rmp(column)
            
        solution, duals, obj_val = self.master.solveMaster(time_end)
        self.masterSolveTime += time.time() - c_time
        self.masterObjective = obj_val
        self.dual = duals
    
    def invokePricing(self, time_end: int, dual: List[float]):
        
        c_time = time.time()
        self.pricing_problem.update_pricing_problem(dual)
        new_columns = self.pricing_solver.generate_columns(time_end)
        self.pricingSolveTime += time.time() - c_time
        return new_columns