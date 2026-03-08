from sqlalchemy import Boolean, Column, Integer

from core.database import Base


class BotSettings(Base):
    __tablename__ = "bot_settings"

    id = Column(Integer, primary_key=True)
    debug_mode = Column(Boolean, default=False)
