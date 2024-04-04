import gurobipy as gp
import random as rd
import pandas as pd

def buildFakeAnesthetists(B):
    A = {}
    for j in B:
        A[j] = rd.randint(8, 13)
    return A

def getParameters():
    # Operating Rooms (real)
    df_infra = pd.read_csv('instances/INST_1/infra_salas(psi).csv', sep=',')
    O = df_infra.columns[1:].tolist()

    # Blocks (one week -- the real planning is for a month)
    df_disp = pd.read_csv('instances/INST_1/disp_times(lambda).csv', sep=',')
    BWeekIds = df_disp['bloco'].tolist()

    B = []
    for b in range(1, 23): # TODO - ADAPT THE NUMBER OF DAYS AS SOMETHING FROM THE FILES
        weekDay = BWeekIds[(b-1) % 5]
        B.append(f'{weekDay}_{b}')

    # Specialties (real)
    df_espec = pd.read_csv('instances/INST_1/especialidades.csv', sep=',')
    S = df_espec['Especialidades'].tolist()

    # Demand (artificial)
    D = {s: df_espec.loc[df_espec['Especialidades'] == s, 'Demanda'].values[0] for s in S}

    # Priorities (artificial)
    phi = {s: df_espec.loc[df_espec['Especialidades'] == s, 'Prioridade'].values[0] for s in S}

    # Past deficit (artificial)
    zeta = {s: df_espec.loc[df_espec['Especialidades'] == s, 'Deficit passado'].values[0] for s in S}

    # Room infrasctructure (real)
    psi = {}
    for i in O:
        psi[i] = {}
        for k in S:
            psi[i][k] = df_infra.loc[df_infra['Especialidade/sala'] == k, i].values[0]
    
    # Teams availability (real)
    H = {}
    for k in S:
        H[k] = {}
        for j in BWeekIds:
            H[k][j] = df_disp.loc[df_disp['bloco'] == j, k].values[0]    
    
    A = buildFakeAnesthetists(B)
    
    # Testing the maximization of blocks rather than profit (for now):
    # TODO - MAKE IT AS A PARAMETER FROM FILES
    P = {s: 1 for s in S}
    C = {s: 0 for s in S}
    
    return O, B, S, D, P, C, psi, zeta, A, H, phi

def createModel(O, B, S, D, P, C, psi, zeta, A, H, phi):
    m = gp.Model("HC_preliminar_model")

    x = m.addVars(O, B, S, vtype=gp.GRB.BINARY, name="x")
    z = m.addVars(S, vtype=gp.GRB.INTEGER, name="z")
    print(psi)

    m.addConstrs((gp.quicksum(x.sum('*', b, s) for b in B) + z[s] >= D[s] for s in S), name='SpecialtyDemand')
    m.addConstrs((gp.quicksum(x.sum('*', b, s) for b in B) >= zeta[s] for s in S), name='SpecialtyDeficit')
    m.addConstrs((x.sum(o, b, '*') <= 1 for o in O for b in B), name='BlockSpecialty')
    m.addConstrs((x[o, b, s] == 0 for o in O for b in B for s in S if psi[o][s] == 0), name='Infrastructure')
    m.addConstrs((gp.quicksum(x.sum('*', b, s) for s in S) <= A[b] for b in B), name='Anesthetists')
    m.addConstrs((x.sum('*', b, s) <= H[s][b[:3]] for b in B for s in S), name='SpecialtyPerBlock')

    m.setObjective(gp.quicksum(phi[s] * (P[s] - C[s]) * x[o, b, s] for o in O for b in B for s in S) - gp.quicksum(P[s] * z[s] for s in S), gp.GRB.MAXIMIZE)

    return x, z, m

def saveResults(m, x, z, O, B, S):
    m.write('output/hc.lp')
    result = {}
    if m.SolCount > 1:
        for o in O:
            result[o] = {}
            for b in B:
                result[o][b] = [s for s in S if x[o, b, s].x > 0]

        df = pd.DataFrame(result)

        for column in df.columns:
            df[column] = df[column].apply(lambda x: x[0] if len(x) > 0 else '')

        df.to_csv('output/hc_output.csv')

        count_blocks = {}
        for o in O:
            for b in B:
                for s in S:
                    if x[o, b, s].x > 0:
                        count_blocks[s] = count_blocks.get(s, 0) + 1
        
        count_blocks['Empty blocks'] = len(B)*len(O) - sum(count_blocks.values())
        
        df_count = pd.DataFrame(count_blocks.items(), columns=['Specialty', 'Number of Blocks'])
        df_count.to_csv('output/hc_output_count.csv')

        count_deficit = {}
        for s in S:
            print(f"deficit for specialty {s} :{z[s].x}")
            count_deficit[s] = z[s].x
        
        df_deficit = pd.DataFrame(count_deficit.items(), columns=['Specialty', 'Deficit'])
        df_deficit.to_csv('output/hc_output_deficit.csv')       

    else:
        print('No solution found')

def main():
    rd.seed(123)
    O, B, S, D, P, C, psi, zeta, A, H, phi = getParameters()
    vars, z, model = createModel(O, B, S, D, P, C, psi, zeta, A, H, phi)
    model.optimize()

    saveResults(model, vars, z, O, B, S)

if __name__ == '__main__':
    main()