import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def numberOfBlocksPerSpecialtyPlot(resultsPath, instancesToCompare):
    # create a bar plot with the number of blocks per specialty for each instance
    # the x-axis should be the specialties and the y-axis the number of blocks
    # each instance should be a different color
    # save the plot in a file called 'numberOfBlocksPerSpecialty.png'
    results = {}
    for instance in instancesToCompare:
        df = pd.read_csv(f'{resultsPath}{instance}/hc_output_count.csv')
        results[instance] = df.set_index('Specialty')['Number of Blocks'].head(len(df) - 1)
    df = pd.DataFrame(results)
    df.plot(kind='bar')
    plt.xlabel('Specialty')
    plt.ylabel('Number of Blocks')
    plt.title('Number of Blocks per Specialty')
    plt.savefig('numberOfBlocksPerSpecialty.png')
    plt.show()    

def numberOfBlocksTotalPlot():
    pass

def anesthesistIncreasePlot(resultsPath, instance):
    currentAnestDF = pd.read_csv(f'{resultsPath}{instance}/disp_anestesista(A).csv')
    currentAnest = currentAnestDF['Anestesistas - total'].sum()
    newAnestDF = pd.read_csv(f'{resultsPath}{instance}/hc_output_anest.csv')
    newAnest = newAnestDF['Anesthetists'].sum()

    x_bars = ['Qtd. atual', 'Qtd. necessário']
    x_pos = np.arange(2)

    plt.bar(x_pos, [currentAnest, newAnest], color=('deepskyblue', 'tomato'))
    plt.xlabel('')
    plt.xticks(x_pos, x_bars)
    for i, v in enumerate([currentAnest, newAnest]):
        plt.text(i, v + 5, str(v), ha='center')

    plt.ylabel('Qtd. Anestesistas total no mês')
    plt.title('Anestesistas - Diagnóstico')
    plt.show()
    plt.savefig('anesthesistIncrease.png')

def teamsIncreasePlot(resultsPath, instance):
    currentTeamsDF = pd.read_csv(f'{resultsPath}{instance}/disp_times(lambda).csv')
    currentTeams = {}
    newTeams = {}
    for column in currentTeamsDF.columns[2:]:
        currentTeams[column] = currentTeamsDF[column].sum()
    newTeamsDF = pd.read_csv(f'{resultsPath}{instance}/hc_output_teams.csv')
    for column in newTeamsDF.columns[1:]:
        newTeams[column] = newTeamsDF[column].sum()

    N = len(currentTeams)
    ind = np.arange(N)
    width = 0.35
    plt.bar(ind, [currentTeams[s] for s in currentTeams], width, color='deepskyblue', label='Qtd. atual')
    plt.bar(ind + width, [newTeams[s] for s in newTeams], width, color='tomato', label='Qtd. necessária')
    plt.xlabel('Equipes')
    plt.ylabel('Qtd. Equipes total no mês')
    plt.title('Equipes - Diagnóstico')
    plt.xticks(ind + width / 2, [s for s in currentTeams.keys()])
    plt.show()

def main():
    resultsPath = '../output/'
    results = ['AprilOffer', 'INST_1_M1', 'INST_2_M2', 'INST_3_M2', 'INST_3_1_M1']
    # numberOfBlocksPerSpecialtyPlot(resultsPath, results[0:2])
    # numberOfBlocksTotalPlot()
    # anesthesistIncreasePlot(resultsPath, results[4])
    teamsIncreasePlot(resultsPath, results[4])

if __name__ == '__main__':
    main()