import os
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DEFAULT_MYSQL_HOST = "127.0.0.1"
DEFAULT_MYSQL_USER = "root"
DEFAULT_MYSQL_PASSWORD = "swegram_pass"
DEFAULT_MYSQL_TASK_DATABASE = "taskdb"
DEFAULT_MYSQL_CORPUS_DATABASE = "swegram_corpus"

MYSQL_HOST_QA = "127.0.0.1"
MYSQL_USER_QA = "root"
MYSQL_PASSWORD_QA = "rootpassword"
MYSQL_TASK_DATABASE_QA = "taskdb_qa"
MYSQL_CORPUS_DATABASE_QA = "swegram_corpus_qa"


def _declarative_constructor(self, **kwargs) -> None:
    """Don't raise a TypeError for unknown attribute names."""
    cls_ = type(self)
    for k, v in kwargs.items():
        if not hasattr(cls_, k):
            continue
        setattr(self, k, v)


Base = declarative_base(constructor=_declarative_constructor)


class DatabaseConfig:
    """Database configuration class."""

    port: int = 3306

    def __init__(self, is_qa: bool = False, database_name: Optional[str] = None):
        self.is_qa = is_qa
        self._datebase_name = database_name

    @property
    def database_url(self) -> str:
        """Construct the database URL."""
        print("host", self.host)
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database_name}"

    @property
    def mysql_url(self) -> str:
        """Construct the MySQL URL without database name."""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}"

    @property
    def database_name(self) -> str:
        if self._datebase_name:
            return self._datebase_name
        if "MYSQL_DATABASE" in os.environ:
            return os.environ["MYSQL_DATABASE"]
        raise ValueError("Database name must be provided either through environment variable or constructor argument.")

    @property
    def user(self) -> str:
        return MYSQL_USER_QA if self.is_qa else os.environ.get("MYSQL_USER", DEFAULT_MYSQL_USER)

    @property
    def password(self) -> str:
        return MYSQL_PASSWORD_QA if self.is_qa else os.environ.get("MYSQL_PASSWORD", DEFAULT_MYSQL_PASSWORD)

    @property
    def host(self) -> str:
        return MYSQL_HOST_QA if self.is_qa else os.environ.get("MYSQL_HOST", DEFAULT_MYSQL_HOST)


class DatabaseHandler:
    """Database handler for managing database connections and operations."""

    def __init__(self, database_name: str, is_qa: bool = False) -> None:
        if hasattr(self, "engine"):
            return  # Avoid reinitialization
        self.config = DatabaseConfig(is_qa=is_qa, database_name=database_name)
        engine = create_engine(self.config.mysql_url)
        with engine.begin() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {database_name}"))
        self.engine = create_engine(self.config.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    @staticmethod
    def get_db():
        """Get a new database session."""
        db = TaskDatabaseHandler().SessionLocal()
        try:
            yield db
        finally:
            db.close()


class TaskDatabaseHandler(DatabaseHandler):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, is_qa: bool = False, database_name: Optional[str] = None) -> None:
        if database_name:
            self.database_name = database_name
        elif "MYSQL_DATABASE" in os.environ:
            self.database_name = os.environ["MYSQL_DATABASE"]
        elif is_qa:
            self.database_name = MYSQL_TASK_DATABASE_QA
        else:
            self.database_name = DEFAULT_MYSQL_TASK_DATABASE
        super().__init__(database_name=self.database_name, is_qa=is_qa)


class CorpusDatabaseHandler(DatabaseHandler):
    """Database handler for managing database connections and operations."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, is_qa: bool = False, database_name: Optional[str] = None):
        if database_name:
            self.database_name = database_name
        elif "MYSQL_DATABASE" in os.environ:
            self.database_name = os.environ["MYSQL_DATABASE"]
        elif is_qa:
            self.database_name = MYSQL_CORPUS_DATABASE_QA
        else:
            self.database_name = DEFAULT_MYSQL_CORPUS_DATABASE
        super().__init__(database_name=self.database_name, is_qa=is_qa)
