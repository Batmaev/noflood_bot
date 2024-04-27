import datetime

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .config import DATABASE_FILE
from .db import Base, BotUser, Session


class NotifiedUser(Base):
    __tablename__ = 'notified_users'
    user_id = Column(Integer, ForeignKey(BotUser.id), primary_key=True)
    n_notifications = Column(Integer, default=1)
    notified_at = Column(DateTime, server_default=func.now()) # pylint: disable=not-callable

    user = relationship(BotUser)


class NotificationErrors(Base):
    __tablename__ = 'notification_errors'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(BotUser.id))
    text = Column(Text)
    time = Column(DateTime, server_default=func.now()) # pylint: disable=not-callable


def get_notified_user(user_id: int):
    with Session() as session:
        notified_user = session.query(NotifiedUser).filter(
            NotifiedUser.user_id == user_id
        ).first()
        return notified_user


def save_notification(bot_user: BotUser):
    with Session() as session:
        notified_user = session.query(NotifiedUser).filter(
            NotifiedUser.user_id == bot_user.id
        ).first()

        if notified_user is None:
            notified_user = NotifiedUser(user_id=bot_user.id)
            session.add(notified_user)
        else:
            notified_user.n_notifications += 1
            notified_user.notified_at = datetime.datetime.now()

        session.commit()


def save_notification_error(bot_user: BotUser, text: str):
    with Session() as session:
        notification_error = NotificationErrors(user_id=bot_user.id, text=text)
        session.add(notification_error)
        session.commit()




if __name__ == '__main__':
    engine2 = create_engine('sqlite:///' + DATABASE_FILE, echo=True)
    Base.metadata.create_all(engine2)

