from cg.pricing.pricing_problem import PricingProblem
from bidict import bidict
from cg.IndependentSet import column_independent_set
import gurobipy as gp

class MasterData:
    """
    Container which stores information coming from the master problem. It contains:
    a reference to the gurobi model
    a list of pricing problems
    a mapping of subtour inequalities to the constraints in the gurobi model

    This is a data object which is being managed by the Master problem. The same data object is passed to the cutHandlers. Therefore, the object can be used to pass information from the master problem to the classes which separate valid inequalities (and also in the opposite direction).
    being deprecated at this moment, try to use ColumnPool instead
    """
    def __init__(self,pricing_problems:list[PricingProblem],model:gp.Model,varMap:dict[PricingProblem,bidict[column_independent_set,gp.Var]]):
        self.pricing_problems = pricing_problems
        
        self.varMap = varMap
        self.inequalities=[]
        self.iteration=0