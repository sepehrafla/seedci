import os
import requests
import server_mock

import json

BASE_URL = 'http://159.89.118.23:8070/api/'


class AccessDeniedException(Exception):
    pass


def register_runner(runner_name, key, ip_address) -> dict:
    register_params = {
        'runner_name': runner_name,
        'key': key,
        'ip_address': ip_address
    }
    response = requests.post(
        BASE_URL + 'register_runner',
        register_params
    )

    if response.status_code != 200:
        raise AccessDeniedException()

    return response.json()


def get_jobs(runner_id):
    if os.environ["RUNNING_ENV"] == 'dev':
        print("Getting job from a mock server")
        return server_mock.get_jobs(runner_id)

    response = requests.get(
        BASE_URL + 'get_job',
        {"runner_id": runner_id}
    )

    print("Getting job from a real server")

    if response.status_code == 200:
        return response.json()


def send_metrics(project_name, metrics):
    new_metrics_params = {
        'project_name': project_name,
        'metrics': json.dumps(metrics)
    }
    response = requests.post(
        BASE_URL + 'new_metrics',
        new_metrics_params
    )
    if response.status_code != 200:
        print("Something went wrong")
