from fastapi import FastAPI, HTTPException, Depends, Response, status, APIRouter
from .. import shemas, models, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(
    prefix="/questions",
    tags=['Questions']
    )

@router.get("/", response_model=List[shemas.SendQuestion])
def get_questions(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), 
limit: int = 5, skip: int = 0, search: Optional[str] = ""):

    questions = db.query(models.Question).filter(models.Question.category.contains(search)).limit(limit).offset(skip).all()
    return questions

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=shemas.SendQuestion)
def create_question(post: shemas.Questions, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    new_question = models.Question(owner_id = current_user.id, **post.dict())

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question

@router.get("/{id}", response_model=shemas.SendQuestion)
def get_question(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    question = db.query(models.Question).filter(models.Question.id == id).first()

    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"question with id: {id} was not found")

    return question

@router.delete("/{id}")
def delete_question(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    question_query = db.query(models.Question).filter(models.Question.id == id)

    deleted_question = question_query.first()

    if deleted_question == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"question with id: {id} does not exist")

    if deleted_question.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    question_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_question(id: int, question: shemas.Questions, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    question_query = db.query(models.Question).filter(models.Question.id == id)

    update_question = question_query.first()

    if update_question == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"question with id: {id} does not exist")

    if update_question.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    question_query.update(question.dict(), synchronize_session=False)
    db.commit()

    return {"data" : "succesful"}