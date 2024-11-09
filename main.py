from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from datetime import date
from typing import List
import models, database, schemas
from database import get_db
from utils import hash_password, verify_password, create_access_token, query_chatgpt, extract_text_from_pdf
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

@app.options("/signup")
async def options_signup():
    return {"message": "CORS preflight request handled"}

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

@app.post("/record_entry")
def create_entry(entry: schemas.EntryCreate, db: Session = Depends(get_db)):
    new_entry = models.Entry(
        # entry_type=entry.entry_type,
        # description=entry.description,
        date=entry.date,
        company_name=entry.company_name,
        keyword=entry.keyword,
        detail_description=entry.detail_description
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


@app.post("/entry_to_gpt")
async def create_entry(entry_type: str = Body(...), description: str = Body(...)):
    prompt = f"{entry_type}: {description}"
    response_text = query_chatgpt(prompt)
    return {"response": response_text}



@app.post("/upload_pdf")
def bulk_entry(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    for file in files:
        # Extract text from the file
        file_content = extract_text_from_pdf(file)
        print("----------",file_content)
        response_text = query_chatgpt(file_content)
        
        # Return the response from the ChatGPT API
        return {"response": response_text}


@app.get("/view_journal", response_model=List[schemas.EntryResponse])
def get_entries(from_date: date, to_date: date, db: Session = Depends(get_db)):
    entries = db.query(models.Entry).filter(models.Entry.date.between(from_date, to_date)).all()
    if not entries:
        raise HTTPException(status_code=404, detail="No entries found")
    return entries