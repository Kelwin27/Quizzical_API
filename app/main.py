from fastapi import FastAPI
from .routers import question, user, auth
from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)

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

@app.get("/")
def root():
    return {"massage": "Hello World!!!!"}




