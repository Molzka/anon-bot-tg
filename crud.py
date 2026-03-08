import hashlib
from datetime import datetime

from core.database import Session
from models.bot_settings import BotSettings
from models.question import Question
from models.user import User


def db_get_or_create_user(
    user_id: int, username: str = None, full_name: str = None
) -> User:
    session = Session()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            code = hashlib.md5(
                f"{user_id}_{datetime.utcnow().timestamp()}".encode()
            ).hexdigest()[:10]
            user = User(
                user_id=user_id,
                username=username,
                full_name=full_name,
                unique_code=code,
            )
            session.add(user)
            session.commit()
        else:
            user.username = username
            user.full_name = full_name
            session.commit()
        session.expunge(user)
        return user
    finally:
        session.close()


def db_user_by_code(code: str):
    session = Session()
    try:
        user = session.query(User).filter_by(unique_code=code).first()
        if user:
            session.expunge(user)
        return user
    finally:
        session.close()


def db_save_question(
    from_id, to_id, msg_type, content=None, file_id=None, caption=None
) -> Question:
    session = Session()
    try:
        q = Question(
            from_user_id=from_id,
            to_user_id=to_id,
            message_type=msg_type,
            content=content,
            file_id=file_id,
            caption=caption,
        )
        session.add(q)
        session.commit()
        session.expunge(q)
        return q
    finally:
        session.close()


def db_get_question(qid: int):
    session = Session()
    try:
        q = session.query(Question).filter_by(id=qid).first()
        if q:
            session.expunge(q)
        return q
    finally:
        session.close()


def db_all_users() -> list[User]:
    session = Session()
    try:
        users = session.query(User).all()
        for u in users:
            session.expunge(u)
        return users
    finally:
        session.close()


def db_debug_enabled() -> bool:
    session = Session()
    try:
        s = session.query(BotSettings).first()
        if not s:
            s = BotSettings(debug_mode=False)
            session.add(s)
            session.commit()
        return s.debug_mode
    finally:
        session.close()


def db_toggle_debug() -> bool:
    session = Session()
    try:
        s = session.query(BotSettings).first()
        if not s:
            s = BotSettings(debug_mode=True)
            session.add(s)
        else:
            s.debug_mode = not s.debug_mode
        session.commit()
        return s.debug_mode
    finally:
        session.close()


def db_count_users() -> int:
    session = Session()
    try:
        return session.query(User).count()
    finally:
        session.close()


def db_count_questions() -> int:
    session = Session()
    try:
        return session.query(Question).count()
    finally:
        session.close()
