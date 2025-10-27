import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost/dailyplanner_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
