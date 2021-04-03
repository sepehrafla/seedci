from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.deployment import ScriptDeployment, SSHKeyDeployment
from django.conf import settings
import os


class GoogleCloudPlatform:

    def __init__(self):
        ComputeEngine = get_driver(Provider.GCE)
        self.driver = ComputeEngine('seedci@neat-drummer-277200.iam.gserviceaccount.com',
                                    os.path.join('cicd4ml/neat-drummer-277200-1306ea0b4719.json'),
                                    datacenter='us-central1-a',
                                    project='neat-drummer-277200')

    def prepareServer(self, runner_name, key):
        KEY_PATH = os.path.join(settings.BASE_DIR, 'MLCICD/keys/config_servers.pub')
        PRIVATE_KEY_PATH = os.path.join(settings.BASE_DIR, 'MLCICD/keys/config_servers')

        SSH_KEY_FINGERPRINT = os.path.join(settings.BASE_DIR, 'MLCICD/keys/bitbucket')
        DEPLOY_PRIVATE_KEY = os.path.join(settings.BASE_DIR, 'MLCICD/keys/deploy')

        with open(KEY_PATH) as fp:
            content = fp.read()

        with open(SSH_KEY_FINGERPRINT) as finger_print_file:
            finger_content = finger_print_file.read()

        with open(DEPLOY_PRIVATE_KEY) as deploy_private_key:
            deploy_private_key_content = deploy_private_key.read()

        SCRIPT = '''#!/usr/bin/env bash
                apt-get -y update && apt-get -y install git
                mkdir ~/.ssh
                chmod 700 ~/.ssh
                echo '{}' >> ~/.ssh/id_rsa
                chmod 600 ~/.ssh/id_rsa
                echo '{}' >> ~/.ssh/known_hosts
                git clone git@bitbucket.org:saflatounian/mlrunnerclient.git
                apt-get install software-properties-common -y
                add-apt-repository -y ppa:deadsnakes/ppa
                apt-get -y install python3.8
                apt -y install python3-pip
                pip3 install -r mlrunnerclient/requirements.txt
                python3 mlrunnerclient/runner.py {} {} {}
                '''.format(deploy_private_key_content, finger_content, runner_name, key, '127.0.0.1')
        step = ScriptDeployment(SCRIPT)
        metadata = {
            'items': [
                {
                    'key': 'ssh-keys',
                    'value': 'root: %s' % content
                }
            ]
        }
        images = self.driver.list_images()
        sizes = self.driver.list_sizes()

        image = [i for i in images if 'ubuntu-1804' in i.name][0]
        size = [s for s in sizes if s.name == 'e2-micro'][0]
        node = self.driver.deploy_node(name='test', image=image, size=size, ex_metadata=metadata,
                                       deploy=step, ssh_key=PRIVATE_KEY_PATH)
        print(node)