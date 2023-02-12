from fastapi import FastAPI, HTTPException, Depends, Response, status, APIRouter
from .. import shemas, models, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=['Users']
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=shemas.UserOut)
def create_user(user: shemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.Users(**user.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/{id}", response_model=shemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), get_current_user: int = Depends(oauth2.get_current_user)):

    user = db.query(models.Users).filter(models.Users.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} was not found")

    return user