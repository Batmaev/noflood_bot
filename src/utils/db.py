import enum

from sqlalchemy import Column, Integer, Text, Enum, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from aiogram.types import User

from .config import DATABASE_FILE
from ..messaging import logs

engine = create_engine('sqlite:///' + DATABASE_FILE)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class MonitoredLink(Base):
    __tablename__ = 'monitored_links'
    link = Column(Text, primary_key=True)
    chat_name = Column(Text)

class UserStatus(enum.Enum):
    NOT_AUTHORIZED = enum.auto()
    AUTHORIZING = enum.auto()
    AUTHORIZED = enum.auto()

class BotUser(Base):
    __tablename__ = 'bot_users'
    id = Column(Integer, primary_key=True)
    username = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    email = Column(Text)
    code = Column(Text)
    status = Column(Enum(UserStatus))
    utm_source_id = Column(Text, ForeignKey(MonitoredLink.link))
    utm_source = relationship(MonitoredLink)
    created_at = Column(DateTime, server_default='now()')



if __name__ == '__main__':
    engine2 = create_engine('sqlite:///' + DATABASE_FILE, echo=True)
    Base.metadata.create_all(engine2)




def save_user(user: User, utm_source: MonitoredLink = None):
    with Session() as session:
        session.expire_on_commit = False
        bot_user = session.query(BotUser).filter(BotUser.id == user.id).first()
        if bot_user:
            if utm_source:
                bot_user.utm_source = utm_source
                logs.new_user(user, utm_source)
            session.commit()
        else:
            bot_user = BotUser(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                status=UserStatus.NOT_AUTHORIZED,
                utm_source=utm_source
            )
            session.merge(bot_user)
            session.commit()
            logs.new_user(user, utm_source)

def save_email(user: User, email: str):
    with Session() as session:
        bot_user = session.query(BotUser).filter(BotUser.id == user.id).first()
        bot_user.email = email
        bot_user.status = UserStatus.AUTHORIZING
        session.commit()

def save_code(user: User, code: str):
    with Session() as session:
        bot_user = session.query(BotUser).filter(BotUser.id == user.id).first()
        bot_user.code = code
        session.commit()
        logs.new_code(user, bot_user.email, code)

def get_user(user: User) -> BotUser:
    with Session() as session:
        bot_user = session.query(BotUser).filter(BotUser.id == user.id).first()
        return bot_user

def authorize(user: User):
    with Session() as session:
        bot_user = session.query(BotUser).filter(BotUser.id == user.id).first()
        bot_user.status = UserStatus.AUTHORIZED
        session.commit()
        logs.finished_authorization(user, bot_user.utm_source)

def save_link(link: str, chat_name: str):
    with Session() as session:
        session.expire_on_commit = False
        monitored_link = MonitoredLink(link=link, chat_name=chat_name)
        session.add(monitored_link)
        session.commit()
        logs.new_link(monitored_link)

def get_link(link: str) -> MonitoredLink:
    with Session() as session:
        return session.query(MonitoredLink).filter(MonitoredLink.link == link).first()
