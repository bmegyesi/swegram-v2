import os
import sys
import threading
import time
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import declarative_base, sessionmaker
from swegram_main.lib.logger import get_logger


DEFAULT_MYSQL_HOST = "127.0.0.1"
DEFAULT_MYSQL_USER = "root"
DEFAULT_MYSQL_PASSWORD = "swegram_pass"
DEFAULT_MYSQL_DATABASE = "swegram_corpus"
MYSQL_HOST_QA = "127.0.0.1"
MYSQL_USER_QA = "root"
MYSQL_PASSWORD_QA = "rootpassword"
MYSQL_DATABASE_QA = "swegram_corpus_qa"
logger = get_logger(__name__)


def _declarative_constructor(self, **kwargs) -> None:
    """Don't raise a TypeError for unknown attribute names."""
    cls_ = type(self)
    for k, v in kwargs.items():
        if not hasattr(cls_, k):
            continue
        try:
            setattr(self, k, v)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning(f"Not able to set attribute, {k=}, {v=} with error {e}")


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

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    @property
    def database_name(self):
        if self._database_name:
            return self._database_name
        if self.is_qa:
            return MYSQL_DATABASE_QA
        if "MYSQL_DATABASE" in os.environ:
            return os.environ["MYSQL_DATABASE"]
        return DEFAULT_MYSQL_DATABASE    

    @property
    def config(self):
        return DatabaseConfig(is_qa=self.is_qa, database_name=self.database_name)

    def __init__(self, is_qa: bool = False, database_name: Optional[str] = None) -> None:
        if hasattr(self, "engine"):
            return  # Avoid reinitialization

        # ----------------------
        # Database configuration
        # ----------------------
        self._database_name = database_name
        self.is_qa = is_qa

        # Server-level connection
        # Used only for CREATE DATABASE
        admin_engine = create_engine(self.config.mysql_url, pool_pre_ping=True, pool_recycle=1800)
        with admin_engine.begin() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {self.database_name}"))
        admin_engine.dispose()

        self._create_engine()

    def _create_engine(self) -> None:
        """Create a new SQLAlchemy engine and connection pool"""

        self.engine = create_engine(
            self.config.database_url, pool_pre_ping=True, pool_recycle=1800,
            pool_size=10, max_overflow=20, pool_timeout=30
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )

    def recreate_engine(self) -> None:
        """Dispose the old engine/pool and create a new one"""

        with self._lock:
            old_engine = getattr(self, "engine", None)

            if old_engine is not None:
                old_engine.dispose()
    
            self._create_engine()

    def check_connection(self) -> bool:
        """Check whether MySQL is currently reachable"""

        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except DBAPIError as error:
            logger.info(f"Lost connection to database: {error}")
        except Exception as error:  # pylint: disable=broad-exception-caught
            logger.info(f"Lost connection due to {error}")
        return False 

    def create_tables(self):
        """Create tables in the database."""

        Base.metadata.create_all(bind=self.engine)

def get_db(retry_number = 3):
    """Get database session"""
    db_handler = DatabaseHandler()

    for _ in range(retry_number):
        if db_handler.check_connection():
            break
        db_handler.recreate_engine()
        time.sleep(5)
    else:
        sys.exit(1)

    try:
        db = db_handler.SessionLocal()
        yield db
    finally:
        db.close()
