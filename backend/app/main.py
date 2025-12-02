# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, users, borrowers, loans, repayments, reports


app = FastAPI(title="Ka-Ro Loan Management API")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Greeting to Ka-Ro Loan Management"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(borrowers.router)
app.include_router(loans.router)
app.include_router(repayments.router)
app.include_router(reports.router)
