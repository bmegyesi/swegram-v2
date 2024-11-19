"""tasks module"""
import os

from typing import Any, Dict
import requests


BASE_URL = f"http://127.0.0.1:8000{'/api' if os.environ.get('PRODUCTION') else ''}"
TASK_URL = f"{BASE_URL}/task"
TASKGROUP_URL = f"{BASE_URL}/taskgroup"


def create_taskgroup() -> Dict[str, int]:
    response = requests.post(f"{TASKGROUP_URL}/create")
    response.raise_for_status()
    return response.json()


def read_taskgroup(taskgroup_id: int) -> Dict[str, Any]:
    response = requests.get(f"{TASKGROUP_URL}/{taskgroup_id}")
    response.raise_for_status()
    return response.json()


def update_taskgroup(taskgroup_id: int, data: Dict[str, Any]) -> None:
    response = requests.put(f"{TASKGROUP_URL}/{taskgroup_id}", json=data)
    response.raise_for_status()


def create_task(text_id: int) -> Dict[str, int]:
    response = requests.post(f"{TASK_URL}/create", json={"text_id": text_id})
    response.raise_for_status()
    return response.json()


def read_task(task_id: int) -> Dict[str, Any]:
    response = requests.get(f"{TASK_URL}/{task_id}")
    response.raise_for_status()
    return response.json()


def update_task(task_id: int, data: Dict[str, Any]) -> None:
    response = requests.put(f"{TASK_URL}/{task_id}", data=data)
    response.raise_for_status()
