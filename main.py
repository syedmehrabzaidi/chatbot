from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database, schemas
from database import get_db
from utils import hash_password, verify_password, create_access_token
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# Define the allowed origins (this can be a list of domains)
origins = [
    "http://localhost:3000",  # Your Next.js frontend
    # Add any other allowed origins as needed
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Create database tables
models.Base.metadata.create_all(bind=database.engine)

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if the username already exists
    db_user_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return { "message":"User is created successfully",
            "status" : 200,
        "user_details": new_user}


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
