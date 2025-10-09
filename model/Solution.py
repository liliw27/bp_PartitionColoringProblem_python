from model.charge_problem import ChargeProblem
from cg.column_independent_set import ColumnIndependentSet


class Solution:
    def __init__(self,instance:ChargeProblem,solution:list[ColumnIndependentSet]):
        self.instance = instance
        self.solution = solution

    def validate(self):
        pass


 
    