"""tasks module"""
import os
import requests


TASK_URL = f"http://127.0.0.1:8000{'/api' if os.environ.get('PRODUCTION') else ''}/task"

def create_task(text_id: int):
    response = requests.post(f"{TASK_URL}/create/{text_id}")
    response.raise_for_status()

def update_task():
    ...


def read_task():
    ...
