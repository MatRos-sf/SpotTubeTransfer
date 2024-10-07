from sqlalchemy import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class DataBase:
    def __init__(self, database: Engine, session: sessionmaker, base: DeclarativeBase):
        self.db = database
        self.session = session
        self.base = base
