import pyomo.environ as pyo
import random as rd
import pandas as pd

def buildFakePsi(O, S):
    psi = {}
    for i in O:
        psi[i] = {}
        for k in S:
            if i == 'OR1' and (k == 'CARDIOLOGIA' or k == 'CIRURGIA CARDÍACA' or k == 'CIRURGIA VASCULAR'):
                psi[i][k] = 1
            elif i == 'OR11' and (k == 'CIRURGIA DE CABEÇA E PESCOÇO' or k == 'NEUROCIRURGIA'):
                psi[i][k] = 1
            else:
                psi[i][k] = rd.choices([0, 1], [0.3, 0.7])[0]
    return psi

def buildFakeLambda(S, B):
    lambda_ = {}
    for k in S:
        lambda_[k] = {}
        for j in B:
            lambda_[k][j] = rd.choices([0, 1], [0.2, 0.8])[0]
    return lambda_

def buildFakeAnesthetists(B):
    A = {}
    for j in B:
        A[j] = rd.randint(10, 15)
    return A

def getParameters():
    O = ['OR1', 'OR2', 'OR3', 'OR4', 'OR5', 'OR6', 'OR7', 'OR8', 'OR9', 'OR10', 'OR11', 'OR12', 'OR13']
    B = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10']
    S = ['CARDIOLOGIA', 'CIRURGIA CARDÍACA', 'CIRURGIA DE CABEÇA E PESCOÇO', 'CIRURGIA DO TRAUMA',
                        'CIRURGIA PEDIÁTRICA', 'CIRURGIA PLÁSTICA', 'CIRURGIA TORÁCICA', 'CIRURGIA VASCULAR', 
                        'DERMATOLOGIA', 'GASTROCIRURGIA', 'GASTROCLINICA', 'GINECOLOGIA', 'HEMATOLOGIA', 'NEUROCIRURGIA']

    # Demand
    D = {'CARDIOLOGIA': 10, 'CIRURGIA CARDÍACA': 6, 'CIRURGIA DE CABEÇA E PESCOÇO': 10, 'CIRURGIA DO TRAUMA': 10,
                        'CIRURGIA PEDIÁTRICA': 3, 'CIRURGIA PLÁSTICA': 6, 'CIRURGIA TORÁCICA': 8, 'CIRURGIA VASCULAR': 5, 
                        'DERMATOLOGIA': 3, 'GASTROCIRURGIA': 5, 'GASTROCLINICA': 5, 'GINECOLOGIA': 3, 'HEMATOLOGIA': 5, 'NEUROCIRURGIA': 10}

    # Revenue
    P = {'CARDIOLOGIA': 3000, 'CIRURGIA CARDÍACA': 3000, 'CIRURGIA DE CABEÇA E PESCOÇO': 2000, 'CIRURGIA DO TRAUMA': 1200,
                        'CIRURGIA PEDIÁTRICA': 1300, 'CIRURGIA PLÁSTICA': 2000, 'CIRURGIA TORÁCICA': 1700, 'CIRURGIA VASCULAR': 1600,
                        'DERMATOLOGIA': 900, 'GASTROCIRURGIA': 1100, 'GASTROCLINICA': 1000, 'GINECOLOGIA': 800, 'HEMATOLOGIA': 950, 'NEUROCIRURGIA': 3000}

    # Cost
    C = {'OR1': {'CARDIOLOGIA': 800, 'CIRURGIA CARDÍACA': 750, 'CIRURGIA DE CABEÇA E PESCOÇO': 500, 'CIRURGIA DO TRAUMA': 420,
                    'CIRURGIA PEDIÁTRICA': 330, 'CIRURGIA PLÁSTICA': 280, 'CIRURGIA TORÁCICA': 370, 'CIRURGIA VASCULAR': 460,
                    'DERMATOLOGIA': 190, 'GASTROCIRURGIA': 210, 'GASTROCLINICA': 200, 'GINECOLOGIA': 180, 'HEMATOLOGIA': 195, 'NEUROCIRURGIA': 700},
    'OR2': {'CARDIOLOGIA': 600, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120,
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160,
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 550},
    'OR3': {'CARDIOLOGIA': 500, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120,
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160,
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 550},
    'OR4': {'CARgit iDIOLOGIA': 500, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120,
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160,
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 550},
    'OR5': {'CARDIOLOGIA': 500, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120,
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160,
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 550},
    'OR6': {'CARDIOLOGIA': 500, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120,
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160, 
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 550},
    'OR7': {'CARDIOLOGIA': 500, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120, 
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160,
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 550},
    'OR8': {'CARDIOLOGIA': 500, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120, 
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160,
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 550},
    'OR9': {'CARDIOLOGIA': 700, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120,
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160,
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 550},
    'OR10': {'CARDIOLOGIA': 500, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120, 
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160,
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 550},
    'OR11': {'CARDIOLOGIA': 500, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120,
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160,
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 550},
    'OR12': {'CARDIOLOGIA': 500, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120,
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160,
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 550},
    'OR13': {'CARDIOLOGIA': 500, 'CIRURGIA CARDÍACA': 550, 'CIRURGIA DE CABEÇA E PESCOÇO': 200, 'CIRURGIA DO TRAUMA': 120, 
                    'CIRURGIA PEDIÁTRICA': 130, 'CIRURGIA PLÁSTICA': 180, 'CIRURGIA TORÁCICA': 170, 'CIRURGIA VASCULAR': 160,
                    'DERMATOLOGIA': 90, 'GASTROCIRURGIA': 110, 'GASTROCLINICA': 100, 'GINECOLOGIA': 80, 'HEMATOLOGIA': 95, 'NEUROCIRURGIA': 400}}

    psi = buildFakePsi(O, S)
    lambda_ = buildFakeLambda(S, B)
    A = buildFakeAnesthetists(B)
    return O, B, S, D, P, C, psi, lambda_, A

def createModel(O, B, S, D, P, C, psi, lambda_, A):
    m = pyo.ConcreteModel()

    m.x = pyo.Var(O, B, S, domain=pyo.Binary)

    m.obj = pyo.Objective(expr=sum(sum(sum(P[k] * m.x[i, j, k] for k in S) for j in B) for i in O), sense=pyo.maximize)

    # Each specialty needs to be allocated to, at least, D_k blocks
    m.SpecialtyDemand = pyo.ConstraintList()
    for k in S:
        m.SpecialtyDemand.add(sum(m.x[i, j, k] for i in O for j in B) >= D[k])

    # Each block of each room needs to be allocated to, at most, one specialty
    m.BlockSpecialty = pyo.ConstraintList()
    for i in O:
        for j in B:
            m.BlockSpecialty.add(sum(m.x[i, j, k] for k in S) <= 1)

    # fixing variables according to psi (if psi[i][k] == 0, then x[i][j][k] == 0)
    m.Infrastructure = pyo.ConstraintList()
    for i in O:
        for k in S:
            if psi[i][k] == 0:
                for j in B:
                    m.Infrastructure.add(m.x[i, j, k] == 0)

    # fixing variables according to lambda (if lambda[k][j] == 0, then x[i][j][k] == 0)
    m.Team_Availability = pyo.ConstraintList()
    for k in S:
        for j in B:
            if lambda_[k][j] == 0:
                for i in O:
                    m.Team_Availability.add(m.x[i, j, k] == 0)

    # For each block j, the number of anesthetists available is enough to cover the number of blocks allocated to each specialty
    m.Anesthetists = pyo.ConstraintList()
    for j in B:
        m.Anesthetists.add(sum(m.x[i, j, k] for i in O for k in S) <= A[j])

    # Objective function, where we want to maximize the profit by multiplying the variable by the REvenue P_k subtracted by the cost C_ik
    return m, m.x

def saveResults(m, x, O, B, S):
    m.write('hc.lp')

    # put the result from pyomo in a dataframe
    df = pd.DataFrame(columns=['Room', 'Block', 'Specialty'])
    for i in O:
        for j in B:
            for k in S:
                if x[i, j, k].value > 0:
                    df = df.append({'Room': i, 'Block': j, 'Specialty': k}, ignore_index=True)

    for column in df.columns:
        df[column] = df[column].apply(lambda x: x[0] if len(x) > 0 else '')

    print(df)

    df.to_csv('hc_output.csv')

    count = {}
    for i in O:
        for j in B:
            for k in S:
                if x[i, j, k].x > 0:
                    count[k] = count.get(k, 0) + 1

    df_count = pd.DataFrame(count.items(), columns=['Specialty', 'Number of Blocks'])
    df_count.to_csv('hc_output_count.csv')
    print(df_count)

def main():
    rd.seed(123)
    O, B, S, D, P, C, psi, lambda_, A = getParameters()
    vars, model = createModel(O, B, S, D, P, C, psi, lambda_, A)
    # optimize pyomo model
    solver = pyo.SolverFactory('gurobi')
    solver.solve(model)

    saveResults(model, vars, O, B, S)

if __name__ == '__main__':
    main()