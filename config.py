import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-academic-use-only'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///epro.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration (for demo purposes, in production use real SMTP settings)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@example.com'  # Replace with actual email
    MAIL_PASSWORD = 'your-email-password'     # Replace with actual password
    MAIL_DEFAULT_SENDER = 'noreply@epro-demo.ac.in'
