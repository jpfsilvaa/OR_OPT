import gurobipy as gp
import random as rd
import pandas as pd

def getParameters():
    df_infra = pd.read_csv('instances/INST_1/infra_salas(psi).csv', sep=',')
    operRooms = df_infra.columns[1:].tolist()

    df_espec = pd.read_csv('instances/INST_1/especialidades.csv', sep=',')
    specialties = df_espec['Sub-especialidades'].tolist()
    demand = {s: df_espec.loc[df_espec['Sub-especialidades'] == s, 'Demanda'].values[0] for s in specialties}
    priorities = {s: df_espec.loc[df_espec['Sub-especialidades'] == s, 'Prioridade'].values[0] for s in specialties}
    pastDeficit = {s: df_espec.loc[df_espec['Sub-especialidades'] == s, 'Deficit passado'].values[0] for s in specialties}
    needAnest = {s: df_espec.loc[df_espec['Sub-especialidades'] == s, 'Precisa anestesista'].values[0] for s in specialties}
    infra = {}
    for i in operRooms:
        infra[i] = {}
        for k in specialties:
            infra[i][k] = df_infra.loc[df_infra['Sub-especialidade/sala'] == k, i].values[0]
    
    df_disp_times = pd.read_csv('instances/INST_1/disp_times(lambda).csv', sep=',')
    blockWeekIds = df_disp_times['bloco_semana_id'].tolist()
    teamsAvailab = {}
    for k in specialties:
        teamsAvailab[k] = {}
        for j in blockWeekIds:
            teamsAvailab[k][j] = df_disp_times.loc[df_disp_times['bloco_semana_id'] == j, k].values[0]
    
    df_disp_anest = pd.read_csv('instances/INST_1/disp_anestesista(A).csv', sep=',')
    blockIds = df_disp_anest['bloco_id'].tolist()

    anestAvailab = {}
    for i in range(len(blockIds)):
        anestAvailab[df_disp_anest.loc[i, 'bloco_id']] = df_disp_anest.loc[i, 'Anestesistas - total']

    revenue = {s: 1 for s in specialties}
    cost = {s: 0 for s in specialties}
    
    return operRooms, blockIds, specialties, demand, revenue, cost, infra, pastDeficit, anestAvailab, teamsAvailab, priorities, needAnest

def createModel(O, B, S, D, P, C, psi, zeta, A, H, phi, gamma):
    m = gp.Model("HC_preliminaryvari[avel de folga_model")

    x = m.addVars(O, B, S, vtype=gp.GRB.BINARY, name="x")

    m.addConstrs((gp.quicksum(x.sum('*', b, s) for b in B) >= D[s] for s in S), name='SpecialtyDemand')
    m.addConstrs((gp.quicksum(x.sum('*', b, s) for b in B) >= zeta[s] for s in S), name='SpecialtyDeficit')
    m.addConstrs((x.sum(o, b, '*') <= 1 for o in O for b in B), name='BlockSpecialty')
    m.addConstrs((x[o, b, s] == 0 for o in O for b in B for s in S if psi[o][s] == 0), name='Infrastructure')
    m.addConstrs((gp.quicksum(gamma[s] * x.sum('*', b, s) for s in S) <= A[b] for b in B), name='Anesthetists')
    m.addConstrs((x.sum('*', b, s) <= H[s][b[:3]] for b in B for s in S), name='SpecialtyPerBlock')

    m.setObjective(gp.quicksum(phi[s] * (P[s] - C[s]) * x[o, b, s] for o in O for b in B for s in S), gp.GRB.MAXIMIZE)

    return x, m

def saveResults(m, x, O, B, S):
    m.write('output/hc.lp')
    result = {}
    if m.SolCount >= 1:
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

    else:
        print('No solution found')

def main():
    rd.seed(123)
    O, B, S, D, P, C, psi, zeta, A, H, phi, gamma = getParameters()
    vars, model = createModel(O, B, S, D, P, C, psi, zeta, A, H, phi, gamma)
    model.optimize()

    saveResults(model, vars, O, B, S)

if __name__ == '__main__':
    main()