# decorators module to create job and task
import logging
import traceback
from functools import wraps
from typing import Optional

from server.config import Config
from server.models.job import Job
from server.models.task import Task
from server.database.handler import DatabaseHandler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobDecorator:
    """Decorator for creating and managing jobs."""
    db = next(DatabaseHandler().get_db())

    def create_job(self, language: str, filename: str, job_name: Optional[str] = None, parent_id: Optional[int] = None) -> None:
        self.db_job = Job(language=language, filename=filename, job_name=job_name, parent_id=parent_id, state=0, verdict=0)
        self.db.add(self.db_job)
        self.db.commit()
        self.db.refresh(self.db_job)

    def update_job(self, state: Optional[int] = None, verdict: Optional[int] = None) -> None:
        if state is not None:
            self.db_job.state = state
        if verdict is not None:
            self.db_job.verdict = verdict

        self.db.commit()
        self.db.refresh(self.db_job)

    def __call__(self, func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not kwargs.get("config"):
                raise ValueError("Configuration must be provided as keyword arguments to the decorated function.")
            config: Config = kwargs["config"]
            self.create_job(
                language=config.language, filename=config.filename,
                parent_id=kwargs.get("parent_id"), job_name=kwargs.get("job_name")
            )
            try:
                logger.info("Executing job...")
                kwargs["job_id"] = self.db_job.id  # Pass job_id to the decorated function
                response = func(*args, **kwargs)
                self.update_job(state=1)
            except Exception as e:
                logger.error(f"Error occurred while executing the job: {e}")
                self.update_job(verdict=1)
            else:
                logger.info("Job executed successfully.")
                self.update_job(verdict=0)
                return response
            finally:
                logger.info("Terminating job...")
                self.update_job(state=2)
        return wrapper


class TaskDecorator:
    """Decorator for creating and managing tasks."""
    db = next(DatabaseHandler().get_db())

    def create_task(self, name: str, job_id: int) -> None:
        self.db_task = Task(state=0, verdict=0, name=name, job_id=job_id)
        self.db.add(self.db_task)
        self.db.commit()
        self.db.refresh(self.db_task)

    def update_task(self, state: Optional[int] = None, verdict: Optional[int] = None) -> None:
        if state is not None:
            self.db_task.state = state
        if verdict is not None:
            self.db_task.verdict = verdict
        self.db.commit()
        self.db.refresh(self.db_task)

    def __init__(self, task_name: Optional[str] = None) -> None:
        self.task_name = task_name

    def __call__(self, func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if kwargs.get("job_id") is None:
                raise ValueError("job_id must be provided as a keyword argument to the decorated function.")
            logger.info("Creating task...")
            self.create_task(name=self.task_name or func.__name__, job_id=kwargs.get("job_id"))
            try:
                response = func(*args, **kwargs)
            except Exception as e:
                traceback.print_exc()
                logger.error(f"Error occurred while executing the task: {e}")
                self.update_task(verdict=1)
            else:
                logger.info("Task executed successfully.")
                self.update_task(verdict=0)
                return response
            finally:
                logger.info("Terminating task...")
                self.update_task(state=2)
                logger.info("Task terminated.")
        return wrapper
