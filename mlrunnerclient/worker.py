import importlib
from server import get_jobs, send_metrics
import os
import time
import subprocess
import yaml
import shutil


class Worker:
    def __init__(self, runnerObject):
        self.runnerObject = runnerObject
        self.configFile = None
        self.workingDir = '.'

    def getJobFromServer(self):
        jobs = get_jobs(self.runnerObject.getId())
        for job in jobs:
            print("Got a new job with id {} for repo {}".format(job.get('id'), job.get('repo')))

            # In testing env, we skip cloning from git.
            if os.environ["RUNNING_ENV"] == 'dev':
                self.workingDir = 'sample'
                self.handleConfigFile('sample/seedci.yaml')
            else:
                print("Cloning the repo ...")
                commandToRun = "git clone {} output_repo".format(job.get('repo'))
                cloneProcess = subprocess.run(commandToRun, shell=True)
                if cloneProcess.returncode == 0:
                    print("Successfully cloned the repo")
                else:
                    print("An error occurred: {} {}".format(cloneProcess.stderr, cloneProcess.stdout))
                self.workingDir = 'output_repo'
                self.handleConfigFile("output_repo/seedci.yaml")

    def run(self):
        while True:
            self.getJobFromServer()
            time.sleep(1)

    def handleConfigFile(self, config_file_path):
        with open(config_file_path, 'r') as in_file:
            self.configFile = yaml.safe_load(in_file)
        self.handleInitialize()
        self.handleWorkflow()
        shutil.rmtree('output_repo', ignore_errors=True)

    def handleInitialize(self):
        if 'initialize' in self.configFile:
            initObject = self.configFile.get('initialize')
            print("Running initialization commands ...")
            for command in initObject:
                process = subprocess.run(command, shell=True)
                if process.returncode != 0:
                    print("An error occurred: {} {}".format(process.stderr, process.stdout))
            print("Done!")

    def handleWorkflow(self):
        for step in self.configFile.get('workflows'):
            print("Running step: {}".format(step.get('name')))
            my_module = importlib.import_module(self.workingDir + '.' + step.get('file'))
            functionObject = getattr(my_module, step.get('function'))
            metrics = functionObject()
            send_metrics(self.runnerObject.getProjectName(), metrics)
            print(functionObject())