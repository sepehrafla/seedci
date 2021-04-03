import os
import sys

from server import AccessDeniedException, register_runner
from worker import Worker

CONNECT_STATE = 'CONNECT'
DISCONNECT_STATE = 'DISCONNECT'

INIT_CONFIG = {
    'runner_name': 'smoked_meat',
    'key': '123test',
    'ip_address': '127.0.0.1',
    'env': 'dev'
}

# Redirecting all prints to a file:
sys.stdout = open('/tmp/runner_print_out', 'w')


class Runner:
    # Initial configuration

    def __init__(self, config=None):
        # Internal system states
        if config is None:
            config = INIT_CONFIG
        self.system_state = DISCONNECT_STATE
        self.project = None
        self.runner_id = None
        self.CONFIG = config
        os.environ["RUNNING_ENV"] = self.CONFIG.get('env')

    def getId(self):
        return self.runner_id

    def getProjectName(self):
        return self.project

    def connectToServer(self):
        # Trying to register with the server
        try:
            response = register_runner(
                self.CONFIG.get('runner_name'),
                self.CONFIG.get('key'),
                self.CONFIG.get('ip_address')
            )

        except AccessDeniedException:
            print("This runner is not allowed to register on this server. Exiting ...")
            exit(-1)

        print("Successfully Registered with id:{} for project"
              .format(response.get('id'), response.get('project')))

        self.project = response.get('project')
        self.runner_id = response.get('id')
        self.system_state = CONNECT_STATE
        worker = Worker(self)
        worker.run()


if __name__ == '__main__':
    arguments = sys.argv
    runner_name = sys.argv[1]
    key = sys.argv[2]
    ip_address = sys.argv[3]

    r = Runner(config={
        'runner_name': runner_name,
        'key': key,
        'ip_address': ip_address,
        'env': 'prod'
    })
    r.connectToServer()
