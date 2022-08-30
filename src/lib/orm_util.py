from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool

from src.lib.exception import RollBack
from src.lib.log import logger


class DBInstance:

    def __init__(self, db_info, **kwargs):
        connect_string = "mysql+pymysql://{user_name}:{password}@{host}:{port}/{database}?charset=utf8"
        engine = create_engine(
            connect_string.format(user_name=db_info.user_name,
                                  password=db_info.password,
                                  host=db_info.host,
                                  database=db_info.database,
                                  port=db_info.port),
            echo=kwargs.get('echo', False),
            encoding='utf-8',
            poolclass=NullPool,
            pool_pre_ping=True,
            # pool_recycle=3600, pool_size=10,
        )
        self.Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))

    def get_session(self):
        return self.Session()


def update_tables(engine, base):
    base.metadata.create_all(engine)


@contextmanager
def get_session_from(db_instance):
    """Provide a transactional scope around a series of operations."""
    session = db_instance.get_session()
    try:
        yield session
        session.commit()
    except RollBack:
        raise
    except:
        # session.rollback()
        raise
    finally:
        session.close()
