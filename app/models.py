from sqlalchemy import TIMESTAMP, Column, Integer, String, ARRAY, ForeignKey, text
from sqlalchemy.orm import relationship
from .database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, nullable=False)
    question = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    incorrect_answers = Column(ARRAY(String), nullable=False)
    difficulty_id = Column(Integer, ForeignKey("difficulty.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("Users")
    dif = relationship("Difficulty")
    cat = relationship("Category")

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    userrole = Column(String, nullable=False)
    score = Column(Integer, nullable=True, default=0)
    games = Column(Integer, nullable=True, default=0)
    refresh = Column(String, nullable=True)
    image = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
class Difficulty(Base):
    __tablename__ = 'difficulty'
    
    id = Column(Integer, primary_key=True, nullable=False)
    difficulty = Column(String, nullable=False)

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, nullable=False)
    category = Column(String, nullable=False)
