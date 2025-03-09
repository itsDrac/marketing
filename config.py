from dotenv import load_dotenv
import os


load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "you'll never know"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        "sqlite:///debug.db"
    ADMINS = ["gpt.sahaj28@gmail.com", "sahaj@agency", "rezaghazi2410@outlook.de"]
    CLIENT_KEY = os.environ.get('CLIENT_KEY')
    EMAIL_PASSWORD_KEY = os.environ.get('EMAIL_PASSWORD_KEY')
