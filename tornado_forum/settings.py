import os

SERVER_ID = os.environ.get("SERVER_ID", f"server-hgoehgeghoeh")
AMQP_URL = "amqp://guest:guest@localhost/"
EXCHANGE_NAME = "chat.topic"
WS_QUEUE_NAME = f"ws.{SERVER_ID}.queue"

room_subscribers = {}