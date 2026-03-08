from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text

from core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_user_id = Column(BigInteger, nullable=False)
    to_user_id = Column(BigInteger, nullable=False)
    message_type = Column(String, default="text")
    content = Column(Text, nullable=True)
    file_id = Column(String, nullable=True)
    caption = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
