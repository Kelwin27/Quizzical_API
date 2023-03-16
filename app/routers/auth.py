from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from .. import database, oauth2, models, utils, shemas
from ..config import settings

ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.refresh_token_expire_minutes

router = APIRouter(
    tags=['Authentication']
    )

@router.post('/login', response_model=shemas.Token)
def login(response: Response, user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user_querry = db.query(models.Users).filter(models.Users.username == user_credentials.username)
    user = user_querry.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})

    # response.set_cookie('refresh_token', refresh_token, settings.refresh_token_expire_minutes * 60, 
    #                     settings.refresh_token_expire_minutes * 60, '/', None, False, True, 'Lax')
    user_querry.update({"refresh" : refresh_token }, synchronize_session=False)
    db.commit()
    user.access_token = access_token
    user.refresh_token = refresh_token
    user.role = user.userrole
    return user 
    
@router.get('/refresh', response_model=shemas.TokenRefreshAnswer)
def refresh(response: Response, refresh: str = Depends(OAuth2PasswordBearer(tokenUrl="login")), db: Session = Depends(database.get_db)):
    user_querry = db.query(models.Users).filter(models.Users.refresh == refresh)
    user = user_querry.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} was not found")

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})
    user_querry.update({"refresh" : refresh_token }, synchronize_session=False)
    db.commit()
    return { "access_token": access_token, "refresh_token": refresh_token, "id": user.id }

