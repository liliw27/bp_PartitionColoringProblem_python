from IndependentSet import column_independent_set
from cg.pricing.pricing_problem import PricingProblem
from bidict import bidict
import gurobipy as gp

class ColumnPool:
    def __init__(self,varMap:dict[PricingProblem,bidict[column_independent_set,gp.Var]]):#todo: check if the varMap is correct
        self.varMap = varMap

    def addColumn(self,column:column_independent_set,pricingProblem:PricingProblem,variable:gp.Var):  
        self.varMap[pricingProblem][column] = variable
    
    def removeColumn(self,column:column_independent_set,pricingProblem:PricingProblem):
        self.varMap[pricingProblem].pop(column)
    
    def getColumns(self,pricingProblem:PricingProblem)->set[column_independent_set]:
        return self.varMap[pricingProblem].keys()
    
    def getVariable(self,pricingProblem:PricingProblem,column:column_independent_set):
        return self.varMap[pricingProblem][column]
    
    def getColumnByValue(self,pricingProblem:PricingProblem,value:float):#todo: check if this is correct
        return self.varMap[pricingProblem].inverse[value]
    
    def getNrColumns(self,pricingProblem:PricingProblem):
        return len(self.varMap[pricingProblem])
    

    
    
    
