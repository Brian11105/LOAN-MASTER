import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/loan_management_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # M-PESA Daraja API Config
    MPESA_CONSUMER_KEY = 'your_consumer_key'
    MPESA_CONSUMER_SECRET = 'your_consumer_secret'
    MPESA_SHORTCODE = 'your_shortcode'
    MPESA_PASSKEY = 'your_passkey'
    MPESA_CALLBACK_URL = 'https://your-domain.com/mpesa/callback'
    
    # Africa's Talking SMS Config
    AT_USERNAME = 'your_username'
    AT_API_KEY = 'your_api_key'
    AT_SENDER_ID = 'your_sender_id'
    
    # Email Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email@gmail.com'
    MAIL_PASSWORD = 'your_email_password'