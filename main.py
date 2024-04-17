import sys

def solveModel(solver, model, instanceFolder):
    if solver == 'gurobi':
        if model == 'M1':
            import gurobipy as gp
            import pandas as pd
            import os
            from hc_model_gurobi import createModel, saveResults

            # TODO

if __name__ == '__main__':
    solver = sys.argv[1:][0]
    model = sys.argv[1:][1]
    instanceFolder = sys.argv[1:][2]
    solveModel(solver, model, instanceFolder)