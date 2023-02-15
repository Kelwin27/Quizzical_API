from sqlalchemy import TIMESTAMP, Column, Integer, String, ARRAY, ForeignKey, text
from sqlalchemy.orm import relationship
from .database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, nullable=False)
    question = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    incorrect_answers = Column(ARRAY(String), nullable=False)
    category = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("Users")

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    userrole = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
