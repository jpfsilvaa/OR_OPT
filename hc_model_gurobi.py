import gurobipy as gp
import random as rd
import pandas as pd
from classes.parameters import ModelParameters

def getParameters(instance, modelType):
    params = ModelParameters()
    params.instance = instance
    params.modelType = modelType
    instancePath = f'instances/{instance}/'

    df_infra = pd.read_csv(f'{instancePath}infra_salas(psi).csv', sep=',')
    params.operRooms = df_infra.columns[1:].tolist()

    df_espec = pd.read_csv(f'{instancePath}especialidades.csv', sep=',')
    params.specialties = df_espec['Sub-especialidades'].tolist()
    params.demand = {s: df_espec.loc[df_espec['Sub-especialidades'] == s, 'Demanda'].values[0] for s in params.specialties}
    params.priority = {s: df_espec.loc[df_espec['Sub-especialidades'] == s, 'Prioridade'].values[0] for s in params.specialties}
    params.pastDeficit = {s: df_espec.loc[df_espec['Sub-especialidades'] == s, 'Deficit passado'].values[0] for s in params.specialties}
    params.needAnest = {s: df_espec.loc[df_espec['Sub-especialidades'] == s, 'Precisa anestesista'].values[0] for s in params.specialties}
   
    infra = {}
    for i in params.operRooms:
        infra[i] = {}
        for k in params.specialties:
            infra[i][k] = df_infra.loc[df_infra['Sub-especialidade/sala'] == k, i].values[0]
    params.infra = infra
    
    df_disp_times = pd.read_csv(f'{instancePath}disp_times(lambda).csv', sep=',')
    blockWeekIds = df_disp_times['bloco_semana_id'].tolist()
    
    teamsAvailab = {}
    for k in params.specialties:
        teamsAvailab[k] = {}
        for j in blockWeekIds:
            teamsAvailab[k][j] = df_disp_times.loc[df_disp_times['bloco_semana_id'] == j, k].values[0]
    params.teamsAvailab = teamsAvailab
    
    df_disp_anest = pd.read_csv(f'{instancePath}disp_anestesista(A).csv', sep=',')
    params.blockIds = df_disp_anest['bloco_id'].tolist()[:-1]

    anestAvailab = {}
    for i in range(len(params.blockIds)):
        anestAvailab[df_disp_anest.loc[i, 'bloco_id']] = df_disp_anest.loc[i, 'Anestesistas - total']
    params.anestAvailab = anestAvailab

    params.revenue = {s: 1 for s in params.specialties}
    params.cost = {s: 0 for s in params.specialties}
    
    return params

def createModel(params):
    m = gp.Model("HC_preliminary_model")

    x = m.addVars(params.operRooms, params.blockIds, params.specialties, vtype=gp.GRB.BINARY, name="x")
    z = m.addVars(params.specialties, vtype=gp.GRB.INTEGER, name="z")
    h = m.addVars(params.blockIds, params.specialties, vtype=gp.GRB.INTEGER, name="H")
    a = m.addVars(params.blockIds, vtype=gp.GRB.INTEGER, name="A")

    m.addConstrs((gp.quicksum(x.sum('*', b, s) for b in params.blockIds) <= (1 + params.ubDemand) * params.demand[s] for s in params.specialties), name='UpperBoundDemand')
    m.addConstrs((x.sum(o, b, '*') <= 1 for o in params.operRooms for b in params.blockIds), name='BlockSpecialty')
    m.addConstrs((x.sum(o, '*', s) == 0 for o in params.operRooms for s in params.specialties if params.infra[o][s] == 0), name='Infrastructure')
    m.addConstrs((x.sum(o, b, '*') == 0 for o in params.operRooms[-2:] for i,b in enumerate(params.blockIds) if i % 2 != 0), name='CCAWorkPeriod')
    m.addConstrs((gp.quicksum(params.needAnest[s] * x.sum('*', b, s) for s in params.specialties) <= params.anestAvailab[b] for b in params.blockIds), name='Anesthetists')
    m.addConstrs((x.sum('*', b, s) <= params.teamsAvailab[s][b[:3]] for b in params.blockIds for s in params.specialties), name='SpecialtyPerBlock')
    # m.addConstrs((gp.quicksum(params.needAnest[s] * x.sum('*', b, s) for s in params.specialties) <= a[b] for b in params.blockIds), name='Anesthesists')
    # m.addConstrs((x.sum('*', b, s) <= h[b, s] for b in params.blockIds for s in params.specialties), name='SpecialtyPerBlock')

    if params.modelType == 'M1':
        m.addConstrs((gp.quicksum(x.sum('*', b, s) for b in params.blockIds) >= params.demand[s] for s in params.specialties), name='SpecialtyDemand')
        m.setObjective(gp.quicksum(params.priority[s] * (params.revenue[s] - params.cost[s]) * x[o, b, s] for o in params.operRooms for b in params.blockIds for s in params.specialties), gp.GRB.MAXIMIZE)
    elif params.modelType == 'M2':
        m.addConstrs((gp.quicksum(x.sum('*', b, s) for b in params.blockIds) + z[s] >= params.demand[s] for s in params.specialties), name='SpecialtyDemand')
        m.setObjective(gp.quicksum(params.priority[s] * (params.revenue[s] - params.cost[s]) * x[o, b, s] for o in params.operRooms for b in params.blockIds for s in params.specialties) - gp.quicksum(params.revenue[s]* z[s] for s in params.specialties), gp.GRB.MAXIMIZE)

    return x, z, h, a, m

def saveResults(m, x, z, h, a, params):
    outputPath = f'output/{params.instance}_{params.modelType}'
    m.write(f'{outputPath}/hc.lp')
    result = {}

    if m.SolCount >= 1:
        # saving schedule result
        for o in params.operRooms:
            result[o] = {}
            for b in params.blockIds:
                result[o][b] = [s for s in params.specialties if x[o, b, s].x > 0]

        df = pd.DataFrame(result)

        for column in df.columns:
            df[column] = df[column].apply(lambda x: x[0] if len(x) > 0 else '')

        df.to_csv(f'{outputPath}/hc_output.csv')

        # saving count of blocks per specialty
        count_blocks = {}
        for o in params.operRooms:
            for b in params.blockIds:
                for s in params.specialties:
                    if x[o, b, s].x > 0:
                        count_blocks[s] = count_blocks.get(s, 0) + 1
        
        count_blocks['Empty blocks'] = len(params.blockIds)*len(params.operRooms) - sum(count_blocks.values())
        
        df_count = pd.DataFrame(count_blocks.items(), columns=['Specialty', 'Number of Blocks'])
        df_count.to_csv(f'{outputPath}/hc_output_count.csv') 

        # saving deficit per specialty
        count_deficit = {}
        for s in params.specialties:
            count_deficit[s] = z[s].x

        df_deficit = pd.DataFrame(count_deficit.items(), columns=['Specialty', 'Deficit'])
        df_deficit.to_csv(f'{outputPath}/hc_output_deficit.csv')   

        # saving teams availability per block
        teams = {}
        for b in params.blockIds:
            teams[b] = {}
            for s in params.specialties:
                teams[b][s] = int(h[b, s].x)
        df_teams = pd.DataFrame(teams)
        df_teams.transpose().to_csv(f'{outputPath}/hc_output_teams.csv')

        # saving anesthetists availability per block
        anest = {}
        for b in params.blockIds:
            anest[b] = int(a[b].x)
        df_anest = pd.DataFrame(anest.items(), columns=['Block', 'Anesthetists'])
        df_anest.to_csv(f'{outputPath}/hc_output_anest.csv')

    else:
        print('No solution found')

def main():
    rd.seed(123)
    
    instance = 'INST_3_1'
    modelType = 'M1'
    modelParams = getParameters(instance, modelType)
    alocVars, deficitVars, teamVars, anesthesistsVar, model = createModel(modelParams)
    model.optimize()

    saveResults(model, alocVars, deficitVars, teamVars, anesthesistsVar, modelParams)

if __name__ == '__main__':
    main()