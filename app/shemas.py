from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
class UserCreate(BaseModel):
    username : str
    password : str
    userrole : str = "user"
    image : str = ""
class UserOut(BaseModel):
    username : str
    score : int
    games : int
    userrole : str
    image : str
    created_at : datetime
    class Config:
        orm_mode = True
class UserIn(BaseModel):
    score : int
    games : int
class UserUpdate(BaseModel):
    username : str = ''
    password : str = ''
    image : str = ''
class UserUpdateOut(BaseModel):
    username : str
    image : str 
    class Config:
        orm_mode = True
class QuestionsIn(BaseModel):
    question : str
    correct_answer : str
    incorrect_answers : list
    difficulty: str
    category: str
class QuestionsEdit(BaseModel):
    question : Optional[str] = None
    correct_answer : Optional[str] = None
    incorrect_answers : list
    difficulty: Optional[str] = None
    category: Optional[str] = None
    owner_id: int
class Questions(BaseModel):
    question : str
    correct_answer : str
    incorrect_answers : list
class SendQuestion(QuestionsIn):
    username: str
    id: int
    class Config:
        orm_mode = True
class SendQuestionData(QuestionsIn):
    username: str
    id: int
    class Config:
        orm_mode = True
class SendQuestionUser(BaseModel):
    questions: List[SendQuestionData]
    title: int
class Token(BaseModel):
    access_token : str
    refresh_token : str
    score : int
    games : int
    role : str
    id : int
    image: str
    class Config:
        orm_mode = True
class TokenRefreshAnswer(BaseModel):
    access_token : str
    refresh_token : str
    id : int
class TokenDate(BaseModel):
    id : Optional[str] = None

