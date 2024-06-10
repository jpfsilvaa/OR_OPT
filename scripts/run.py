import multiprocessing
import subprocess
import os

def run_script(scriptPath):
    scriptPath.insert(0, 'python')
    subprocess.run(scriptPath)

if __name__ == '__main__':
    home = os.path.expanduser("~")
    pathToModel = os.path.join(home, 'github', 'OR_OPT', 'models','hc_model_gurobi.py')
    
    scriptCalls = [
        [pathToModel, 'instances/INST_3_1/']
    ]

    #todo: FINISH THIS