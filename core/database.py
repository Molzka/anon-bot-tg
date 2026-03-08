from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///bot.db", echo=False)
Session = sessionmaker(bind=engine, expire_on_commit=False)

def create_db():
    Base.metadata.create_all(engine)
