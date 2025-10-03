import os
from dotenv import load_dotenv

load_dotenv()


SERVER_ID = os.environ.get("SERVER_ID", f"server-hgoehgeghoeh")
AMQP_URL = "amqp://guest:guest@localhost/"
EXCHANGE_NAME = "chat.topic"
WS_QUEUE_NAME = f"ws.{SERVER_ID}.queue"

room_subscribers = {}

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

SECRET_KEY = os.getenv('SECRET_KEY')
SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')