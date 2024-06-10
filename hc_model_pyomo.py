import pyomo.environ as pyo
import random as rd
import pandas as pd
from classes.parameters import ModelParameters
import sys

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
    m = pyo.ConcreteModel()

    O = params.operRooms
    B = params.blockIds
    S = params.specialties
    D = params.demand

    m.x = pyo.Var(O, B, S, domain=pyo.Binary)
    m.z = pyo.Var(S, domain=pyo.NonNegativeIntegers)
    m.h = pyo.Var(B, S, domain=pyo.NonNegativeIntegers)
    m.a = pyo.Var(B, domain=pyo.NonNegativeIntegers)

    m.UpperBoundDemand = pyo.ConstraintList()
    for k in S:
        m.UpperBoundDemand.add(sum(m.x[i, j, k] for i in O for j in B) <= (1 + params.ubDemand) * D[k])
    
    m.BlockSpecialty = pyo.ConstraintList()
    for i in O:
        for j in B:
            m.BlockSpecialty.add(sum(m.x[i, j, k] for k in S) <= 1)

    m.Infrasctructure = pyo.ConstraintList()
    for i in O:
        for k in S:
            if params.infra[i][k] == 0:
                m.Infrasctructure.add(sum(m.x[i, j, k] for j in B) == 0)
    
    m.CCAWorkPeriod = pyo.ConstraintList()
    for o in O[-2:]:
        for i,b in enumerate(params.blockIds):
            if i % 2 != 0:
                m.CCAWorkPeriod.add(sum(m.x[o, j, k] for k in S) == 0)
    
    m.Anesthetists = pyo.ConstraintList()
    for b in B:
        sum(params.needAnest[s] * m.x[i, b, s] for i in O for s in S) <= params.anestAvailab[b]

    m.SpecialtyPerBlock = pyo.ConstraintList()
    for b in B:
        for s in S:
            m.SpecialtyPerBlock.add(sum(m.x[i, b, s] for i in O) <= params.teamsAvailab[s][b[:3]])

    expr=sum(sum(sum(params.priority[k] * (params.revenue[k] - params.cost[k]) * m.x[i, j, k] for k in S) for j in B) for i in O)
    if params.modelType == 'M1':
        m.SpecialtyDemand = pyo.ConstraintList()
        for s in S:
            m.SpecialtyDemand.add(sum(m.x[i, j, s] for i in O for j in B) >= D[s])
        m.obj = pyo.Objective(rule=expr, sense=pyo.maximize)
    else:
        m.SpecialtyDemand = pyo.ConstraintList()
        for s in S:
            m.SpecialtyDemand.add(sum(m.x[i, j, s] for i in O for j in B) + m.z[s] >= D[s])
        expr = expr - sum(params.revenue[s]* m.z[s] for s in S)
        m.obj = pyo.Objective(rule=expr, sense=pyo.maximize)

    return m, m.x, m.z, m.h, m.a

def saveResults(m, x, z, h, a, params):
    outputPath = f'output/{params.instance}_{params.modelType}'
    m.write(f'{outputPath}/hc.lp', io_options={'symbolic_solver_labels': True})
    result = {}

    # saving schedule result
    for o in params.operRooms:
        result[o] = {}
        for b in params.blockIds:
            result[o][b] = [s for s in params.specialties if m.x[o, b, s].value > 0]

    df = pd.DataFrame(result)

    for column in df.columns:
        df[column] = df[column].apply(lambda x: x[0] if len(x) > 0 else '')

    df.to_csv(f'{outputPath}/hc_output.csv')

    # saving count of blocks per specialty
    count_blocks = {}
    for o in params.operRooms:
        for b in params.blockIds:
            for s in params.specialties:
                if m.x[o, b, s].value > 0:
                    count_blocks[s] = count_blocks.get(s, 0) + 1
    
    count_blocks['Empty blocks'] = len(params.blockIds)*len(params.operRooms) - sum(count_blocks.values())
    
    df_count = pd.DataFrame(count_blocks.items(), columns=['Specialty', 'Number of Blocks'])
    df_count.to_csv(f'{outputPath}/hc_output_count.csv') 

    # # saving deficit per specialty
    # count_deficit = {}
    # for s in params.specialties:
    #     count_deficit[s] = m.z[s].value

    # df_deficit = pd.DataFrame(count_deficit.items(), columns=['Specialty', 'Deficit'])
    # df_deficit.to_csv(f'{outputPath}/hc_output_deficit.csv')   

    # # saving teams availability per block
    # teams = {}
    # for b in params.blockIds:
    #     teams[b] = {}
    #     for s in params.specialties:
    #         teams[b][s] = int(m.h[b, s].value)
    # df_teams = pd.DataFrame(teams)
    # df_teams.transpose().to_csv(f'{outputPath}/hc_output_teams.csv')

    # # saving anesthetists availability per block
    # anest = {}
    # for b in params.blockIds:
    #     anest[b] = int(m.a[b].value)
    # df_anest = pd.DataFrame(anest.items(), columns=['Block', 'Anesthetists'])
    # df_anest.to_csv(f'{outputPath}/hc_output_anest.csv')

def main(instance, modelType, seed):
    rd.seed(int(seed))
    
    modelParams = getParameters(instance, modelType)
    model, alocVars, deficitVars, teamVars, anesthesistsVar = createModel(modelParams)
    solver = pyo.SolverFactory('gurobi')
    results = solver.solve(model)
    model.display()

    if (results.solver.status == pyo.SolverStatus.ok) and (results.solver.termination_condition == pyo.TerminationCondition.optimal):
        saveResults(model, alocVars, deficitVars, teamVars, anesthesistsVar, modelParams)
    else:
        print('No solution found')

if __name__ == '__main__':
    instance = sys.argv[1:][0]
    modelType = sys.argv[1:][1]
    seed = sys.argv[1:][2]
    main(instance, modelType, seed)