import ChargeProblem
from cg.IndependentSet import column_independent_set


class Solution:
    def __init__(self,instance:ChargeProblem,solution:list[column_independent_set]):
        self.instance = instance
        self.solution = solution

    def validate(self):
        pass


 
    