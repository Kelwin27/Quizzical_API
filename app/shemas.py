from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username : str
    password : str

class UserOut(BaseModel):
    username : str
    id : int
    created_at : datetime

    class Config:
        orm_mode = True

class Questions(BaseModel):
    question : str
    correct_answer : str
    incorrect_answers : list
    category : str
    type : str
    difficulty : str

class SendQuestion(Questions):
    id : int
    owner_id : int
    owner : UserOut
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenDate(BaseModel):
    id : Optional[str] = None
