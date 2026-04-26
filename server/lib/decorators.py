# decorators module to create job and task
import logging
from functools import wraps
from urllib import response

from server.models.job import Job
from server.models.task import Task
from server.database.handler import TaskDatabaseHandler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobDecorator:
    """Decorator for creating and managing jobs."""
    db = next(TaskDatabaseHandler().get_db())

    def create_job(self, language: str, filename: str) -> None:
        self.db_job = Job(language=language, filename=filename, state=0, verdict=0)
        self.db.add(self.db_job)
        self.db.commit()
        self.db.refresh(self.db_job)

    def update_job(self, state: int = None, verdict: int = None) -> None:
        if state is not None:
            self.db_job.state = state
        if verdict is not None:
            self.db_job.verdict = verdict
        self.db.commit()
        self.db.refresh(self.db_job)

    def __call__(self, cls: callable) -> callable:
        @wraps(cls)
        def wrapper(*args, **kwargs):
            self.create_job(*args, **kwargs)
            try:
                logger.info("Executing job...")
                self.update_job(state=1)
                instance = cls(*args, **kwargs)
                setattr(instance, "job_id", self.db_job.id)
            except Exception as e:
                logger.error(f"Error occurred while executing the job: {e}")
                self.update_job(verdict=1)
            else:
                logger.info("Job executed successfully.")
                self.update_job(verdict=0)
                return instance
            finally:
                logger.info("Terminating job...")
                self.update_job(state=2)
        return wrapper


class TaskDecorator:
    """Decorator for creating and managing tasks."""
    db = next(TaskDatabaseHandler().get_db())

    def create_task(self, name: str, job_id: int) -> None:
        self.db_task = Task(state=0, verdict=0, name=name, job_id=job_id)
        self.db.add(self.db_task)
        self.db.commit()
        self.db.refresh(self.db_task)

    def update_task(self, state: int = None, verdict: int = None) -> None:
        if state is not None:
            self.db_task.state = state
        if verdict is not None:
            self.db_task.verdict = verdict
        self.db.commit()
        self.db.refresh(self.db_task)

    def __init__(self, task_name: str) -> None:
        self.task_name = task_name

    def __call__(self, func: callable) -> callable:
        @wraps(func)
        def wrapper(job, *args, **kwargs):
            logger.info("Creating task...")
            self.create_task(name=self.task_name, job_id=job.job_id)
            try:
                response = func(job, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error occurred while executing the task: {e}")
                self.update_task(verdict=1)
            else:
                logger.info("Task executed successfully.")
                self.update_task(verdict=0)
                return response
            finally:
                logger.info("Terminating task...")
                self.update_task(state=2)
        return wrapper
