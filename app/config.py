import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///pos.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "dev-secret-key"