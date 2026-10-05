from sqlalchemy import URL, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import DATABASE_PATH

Base = declarative_base()
engine = create_engine(URL.create("sqlite", database=str(DATABASE_PATH)), echo=False)
Session = sessionmaker(bind=engine, expire_on_commit=False)


def create_db():
    from models import bot_settings, question, user

    Base.metadata.create_all(engine)
