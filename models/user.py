from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    unique_code = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
