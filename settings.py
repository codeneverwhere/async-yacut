import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db.sqlite3')
    SECRET_KEY = os.getenv('SECRET_KEY', 'SUP3R-S3CR3T-K3Y')
    DISK_TOKEN = os.getenv('DISK_TOKEN', '')
