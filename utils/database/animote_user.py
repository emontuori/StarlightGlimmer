from sqlalchemy import Column, Integer

from utils.database import Base


class AnimoteUser(Base):
    __tablename__ = "animote_users"

    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return "<AnimoteUser(id={0.id})>".format(self)
