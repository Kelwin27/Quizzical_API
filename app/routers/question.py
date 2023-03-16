from random import choice
from fastapi import HTTPException, Depends, Response, status, APIRouter
from .. import shemas, models, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(
    prefix="/questions",
    tags=['Questions']
    )

@router.get("/", response_model=List[shemas.SendQuestion])
def get_questions(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 5, dif: Optional[str] = "", search: Optional[str] = ""): 

    questions_query = db.query(models.Question.id, models.Question.question, models.Question.correct_answer, models.Question.incorrect_answers, models.Difficulty.difficulty, models.Category.category, models.Users.username).join(models.Difficulty).join(models.Category).join(models.Users).filter(models.Category.category.contains(search), models.Difficulty.difficulty.contains(dif)).all()
    questions = []
    if len(questions_query) > limit:
        while len(questions) < limit:
            variant = choice(questions_query)
            if variant not in questions:
                questions.append(variant)
    return questions

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=shemas.SendQuestion)
def create_question(post: shemas.QuestionsIn, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_post = shemas.Questions(
        correct_answer= post.correct_answer,
        incorrect_answers=post.incorrect_answers,
        question=post.question
    )
    new_difficulty = db.query(models.Difficulty.id).filter(models.Difficulty.difficulty == post.difficulty).first()
    if not new_difficulty:
        new_difficulty = models.Difficulty(difficulty=post.difficulty)
        db.add(new_difficulty)
        db.commit()
        db.refresh(new_difficulty)
    difficulty_id = new_difficulty.id
    new_category = db.query(models.Category.id).filter(models.Category.category == post.category).first()
    if not new_category:
        new_category = models.Category(category=post.category)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
    category_id = new_category.id
    new_question = models.Question(owner_id = current_user.id, difficulty_id = difficulty_id, category_id= category_id, **new_post.dict())
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    question = db.query(models.Question.id, models.Question.question, models.Question.correct_answer, models.Question.incorrect_answers, models.Difficulty.difficulty, models.Category.category, models.Users.username).join(models.Difficulty).join(models.Category).join(models.Users).filter(models.Question.id == new_question.id).first()
    return question

@router.get("/{id}", response_model=shemas.SendQuestionUser)
def get_question(response: Response, id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0):

    questions = db.query(models.Question).filter(models.Question.owner_id == id)
    all_questions = questions.all()
    if skip:
        response_questions = questions.offset(skip).limit(limit).all()
    else:
        response_questions = questions.limit(limit).all()
    for q in response_questions:
        q.username = q.owner.username
        q.difficulty = q.dif.difficulty
        q.category = q.cat.category
    if not response_questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"question with id: {id} was not found")

    return {"questions": response_questions, "title": len(all_questions)}

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
def update_question(id: int, question: shemas.QuestionsEdit, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    question_query = db.query(models.Question).filter(models.Question.id == id)
    update_question = question_query.first()

    if update_question == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"question with id: {id} does not exist")

    if update_question.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    if question.difficulty:
        difficulty_id = db.query(models.Difficulty.id).filter(models.Difficulty.difficulty == question.difficulty).first()
        update_question.difficulty_id = difficulty_id[0]
        del question.difficulty

    if question.category:
        category_id = db.query(models.Category.id).filter(models.Category.category == question.category).first()
        update_question.category_id = category_id[0]
        del question.category
    for i in range(len(question.incorrect_answers)):
        if not question.incorrect_answers[i]:
            question.incorrect_answers[i] = update_question.incorrect_answers[i]
    question_data = question.dict(exclude_unset=True)

    for key, value in question_data.items():
        if value:
            setattr(update_question, key, value)
    db.add(update_question)
    db.commit()

    return Response(status_code=status.HTTP_201_CREATED)
