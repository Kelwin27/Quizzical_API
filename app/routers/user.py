import aiofiles
import os
from fastapi import HTTPException, Depends, status, APIRouter, Form, UploadFile
from .. import shemas, models, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import Union, Optional
from ..config import settings

router = APIRouter(
    prefix="/users",
    tags=['Users']
    )
BASEDIR = os.getcwd()
BASE_URL = settings.base_url

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=shemas.UserOut)
async def create_user(username: str = Form(), password: str = Form(), image: Union[UploadFile, None] = None, db: Session = Depends(get_db)):

    user = shemas.UserCreate(
        username = username,
        password = password
    )
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    if user.username == "admin":
        user.userrole = "admin"
    exist_user = db.query(models.Users).filter(models.Users.username == user.username).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User alrady exist")
    if image:
        _, ext = os.path.splitext(image.filename)
        img_dir = os.path.join(BASEDIR,'app/images/')
        content = await image.read()
        if len(content) > 2*1024*1024:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File have too large size")
        if image.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Only .jpeg, .jpg or .png  files allowed")
        path = os.path.join(img_dir, f'{user.username}{ext}')
        async with aiofiles.open(path, "wb") as f:
            await f.write(content)

        user.image = f"{BASE_URL}/image/{user.username}{ext}"
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

@router.patch("/{id}")
def update_user(id: int, user_data: shemas.UserIn, db: Session = Depends(get_db), get_current_user: int = Depends(oauth2.get_current_user)):

    user_querry = db.query(models.Users).filter(models.Users.id == id)
    user = user_querry.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} was not found")

    user_querry.update(user_data.dict(), synchronize_session=False)
    db.commit()

    return {"data" : "succesful"}

@router.put("/{id}", response_model=shemas.UserUpdateOut)
async def edit_user(id: int, username: Optional[str] = Form(None), prew_password: Optional[str] = Form(None), new_password: Optional[str] = Form(None), image: Union[UploadFile, None] = None, db: Session = Depends(get_db), get_current_user: int = Depends(oauth2.get_current_user)):
    user = shemas.UserUpdate()
    if username:
        user.username = username
    user_querry = db.query(models.Users).filter(models.Users.id == id)
    exist_username = db.query(models.Users).filter(models.Users.username == username).first()
    exist_user = user_querry.first()
    if prew_password and new_password:
        hashed_new_password = utils.hash(new_password)
        user.password = hashed_new_password
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not exist")
    if exist_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username alrady exist")
    if prew_password and not new_password or not prew_password and new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalide password sittings")
    if prew_password and not utils.verify(prew_password, exist_user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong password")
    if not username:
        user.username = exist_user.username
    if not prew_password and not new_password:
        user.password = exist_user.password
    if image:  
        _, ext = os.path.splitext(image.filename)
        img_dir = os.path.join(BASEDIR,'app/images/')
        content = await image.read()
        if len(content) > 2*1024*1024:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File have too large size")
        if image.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Only .jpeg, .jpg or .png  files allowed")
        path = os.path.join(img_dir, f'{id}{ext}')
        async with aiofiles.open(path, "wb") as f:
            await f.write(content)
        user.image = f"{BASE_URL}/image/{id}{ext}"
    else:
        user.image = exist_user.image 
    user_querry.update(user.dict(), synchronize_session=False)
    db.commit()
    db.refresh(exist_user)

    return exist_user