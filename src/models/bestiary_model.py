from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import TINYINT, BIGINT, DATE, DATETIME, VARCHAR, INTEGER, DOUBLE, TEXT
from sqlalchemy.sql.expression import text, func

RemoteBase = declarative_base()


class Bestiary(RemoteBase):
    __tablename__ = "bestiary"

    id = Column(INTEGER(20), primary_key=True)
    identifier = Column(VARCHAR(255))
    file_name = Column(VARCHAR(255))
    link = Column(VARCHAR(255))
    translator = Column(VARCHAR(255))

    source = Column(VARCHAR(255))
    cn_name = Column(VARCHAR(255))
    en_name = Column(VARCHAR(255))

    header = Column(TEXT)
    basic = Column(TEXT)
    offense = Column(TEXT)
    defense = Column(TEXT)
    statistics = Column(TEXT)
    ecology = Column(TEXT)
    tactics = Column(TEXT)
    special_ability = Column(TEXT)
    description = Column(TEXT)

