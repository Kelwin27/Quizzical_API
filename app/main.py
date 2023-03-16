import os
from fastapi import FastAPI
from .routers import question, user, auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine
from . import models

models.Base.metadata.create_all(bind=engine)
BASEDIR = os.path.dirname(__file__)

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(question.router)
app.include_router(user.router)
app.include_router(auth.router)

app.mount("/image", StaticFiles(directory=BASEDIR + "/images"), name="image")

@app.get("/")
def root():
    return {"massage": "Hello World!!!!"}




