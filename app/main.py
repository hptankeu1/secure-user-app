"""FastAPI application exposing user registration and login."""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserRead


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Secure User API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(
        select(User).where(or_(User.username == payload.username, User.email == payload.email))
    )
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username or email already registered")

    user = User(username=payload.username, email=payload.email)
    user.set_password(payload.password)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Covers the race where two requests pass the check at the same time
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Username or email already registered")
    db.refresh(user)
    return user


@app.post("/users/login", response_model=UserRead)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == payload.username))
    if not user or not user.check_password(payload.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")
    return user


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user
