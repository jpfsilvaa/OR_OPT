import gurobipy as gp
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

def buildFakeTeams(B, S):
    H = {}
    for j in B:
        H[j] = {}
        for k in S:
            H[j][k] = rd.randint(1, 3)
    return H

def getParameters():
    # Operating Rooms (real)
    O = ['OR1', 'OR2', 'OR3', 'OR4', 'OR5', 'OR6', 'OR7', 'OR8', 'OR9', 'OR10', 'OR11', 'OR12', 'OR13']

    # Blocks (one week -- the real planning is for a month)
    B = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10'] 

    # Specialties (real)
    S = ['CARDIOLOGIA', 'CIRURGIA CARDÍACA', 'CIRURGIA DE CABEÇA E PESCOÇO', 'CIRURGIA DO TRAUMA',
                        'CIRURGIA PEDIÁTRICA', 'CIRURGIA PLÁSTICA', 'CIRURGIA TORÁCICA', 'CIRURGIA VASCULAR',
                         'GASTROCIRURGIA', 'GASTROCLINICA', 'GINECOLOGIA', 'NEUROCIRURGIA', 'OBSTETRÍCIA',
                         'OFTALMOLOGIA', 'ORTOPEDIA', 'ORTOPEDIA TRAUMA', 'OTORRINOLARINGOLOGIA', 'PROCTOLOGIA', 'UROLOGIA']

    # Demand (artificial)
    D = {'CARDIOLOGIA': 7, 'CIRURGIA CARDÍACA': 5, 'CIRURGIA DE CABEÇA E PESCOÇO': 7, 'CIRURGIA DO TRAUMA': 7,
                        'CIRURGIA PEDIÁTRICA': 3, 'CIRURGIA PLÁSTICA': 7, 'CIRURGIA TORÁCICA': 6, 'CIRURGIA VASCULAR': 5, 
                        'GASTROCIRURGIA': 5, 'GASTROCLINICA': 6, 'GINECOLOGIA': 5,  'NEUROCIRURGIA': 8, 'OBSTETRÍCIA': 6,
                        'OFTALMOLOGIA': 10, 'ORTOPEDIA': 10, 'ORTOPEDIA TRAUMA': 8, 'OTORRINOLARINGOLOGIA': 9, 'PROCTOLOGIA': 2, 'UROLOGIA': 4}

    # # Revenue (artificial)
    # P = {'CARDIOLOGIA': 3000, 'CIRURGIA CARDÍACA': 3000, 'CIRURGIA DE CABEÇA E PESCOÇO': 2000, 'CIRURGIA DO TRAUMA': 1200,
    #                     'CIRURGIA PEDIÁTRICA': 1300, 'CIRURGIA PLÁSTICA': 2000, 'CIRURGIA TORÁCICA': 1700, 'CIRURGIA VASCULAR': 1600,
    #                     'GASTROCIRURGIA': 1100, 'GASTROCLINICA': 1000, 'GINECOLOGIA': 800, 'NEUROCIRURGIA': 550, 'OBSTETRÍCIA': 1000,
    #                     'OFTALMOLOGIA': 900, 'ORTOPEDIA': 1200, 'ORTOPEDIA TRAUMA': 1100, 'OTORRINOLARINGOLOGIA': 700, 'PROCTOLOGIA': 500, 'UROLOGIA': 900}

    # # Cost (artificial)
    # C = {k: P[k]*0.4 for k in P}

    # For testing the maximization of blocks rather than profit:
    P = {s: 1 for s in S}
    C = {s: 0 for s in S}

    zeta = {s: rd.randint(1, 5) for s in S}
    psi = buildFakePsi(O, S)
    lambda_ = buildFakeLambda(S, B)
    A = buildFakeAnesthetists(B)
    H = buildFakeTeams(B, S)
    return O, B, S, D, P, C, psi, lambda_, zeta, A, H

def createModel(O, B, S, D, P, C, psi, lambda_, zeta, A, H):
    m = gp.Model("HC_preliminar_model")

    x = m.addVars(O, B, S, vtype=gp.GRB.BINARY, name="x")
    z = m.addVars(S, vtype=gp.GRB.INTEGER, name="z")

    m.addConstrs((gp.quicksum(x.sum('*', b, s) for b in B) + z[s] >= D[s] for s in S), name='SpecialtyDemand')
    m.addConstrs((gp.quicksum(x.sum('*', b, s) for b in B) >= zeta[s] for s in S), name='SpecialtyDeficit')
    m.addConstrs((x.sum(o, b, '*') <= 1 for o in O for b in B), name='BlockSpecialty')
    m.addConstrs((x[o, b, s] == 0 for o in O for b in B for s in S if psi[o][s] == 0), name='Infrastructure')
    m.addConstrs((x[o, b, s] == 0 for o in O for b in B for s in S if lambda_[s][b] == 0), name='Team_Availability')
    m.addConstrs((gp.quicksum(x.sum('*', b, s) for s in S) <= A[b] for b in B), name='Anest_Anesthetists')
    m.addConstrs((x.sum('*', b, s) <= H[b][s] for b in B for s in S), name='SpecialtyPerBlock')

    m.setObjective(gp.quicksum((P[s] - C[s]) * x[o, b, s] for o in O for b in B for s in S) - gp.quicksum(P[s] * z[s] for s in S), gp.GRB.MAXIMIZE)

    return x, z, m

def saveResults(m, x, z, O, B, S):
    m.write('hc.lp')
    result = {}
    if m.SolCount > 1:
        for o in O:
            result[o] = {}
            for b in B:
                result[o][b] = [s for s in S if x[o, b, s].x > 0]

        df = pd.DataFrame(result)

        for column in df.columns:
            df[column] = df[column].apply(lambda x: x[0] if len(x) > 0 else '')

        df.to_csv('hc_output.csv')

        count_blocks = {}
        for o in O:
            for b in B:
                for s in S:
                    if x[o, b, s].x > 0:
                        count_blocks[s] = count_blocks.get(s, 0) + 1
        
        count_blocks['Empty blocks'] = len(B)*len(O) - sum(count_blocks.values())
        
        df_count = pd.DataFrame(count_blocks.items(), columns=['Specialty', 'Number of Blocks'])
        df_count.to_csv('hc_output_count.csv')

        count_deficit = {}
        for s in S:
            print(f"deficit for specialty {s} :{z[s].x}")
            count_deficit[s] = z[s].x
        
        df_deficit = pd.DataFrame(count_deficit.items(), columns=['Specialty', 'Deficit'])
        df_deficit.to_csv('hc_output_deficit.csv')       

    else:
        print('No solution found')

def main():
    rd.seed(123)
    O, B, S, D, P, C, psi, lambda_, zeta, A, H = getParameters()
    vars, z, model = createModel(O, B, S, D, P, C, psi, lambda_, zeta, A, H)
    model.optimize()

    saveResults(model, vars, z, O, B, S)

if __name__ == '__main__':
    main()