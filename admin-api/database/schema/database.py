from sqlalchemy import create_engine, URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils.constants import DATABASE_LOG_LEVEL
from utils.environment import DATABASE_URL

from utils.logger_utility import getlogger

databse_logger = getlogger(name="sqlalchemy.engine.Engine", log_level=DATABASE_LOG_LEVEL)


engine = create_engine(DATABASE_URL, logging_name="AppDatabase", pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()