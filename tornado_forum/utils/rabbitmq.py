import aio_pika
from aio_pika import ExchangeType, Message, DeliveryMode
import json

# from tornado_forum.settings import AMQP_URL, EXCHANGE_NAME, WS_QUEUE_NAME, room_subscribers
from settings import AMQP_URL, EXCHANGE_NAME, WS_QUEUE_NAME, room_subscribers

_amqp_connection = None
_amqp_channel = None
_amqp_exchange = None
_amqp_queue = None

async def init_amqp():
    global _amqp_connection, _amqp_channel, _amqp_exchange, _amqp_queue
    _amqp_connection = await aio_pika.connect_robust(AMQP_URL)
    print(f'The _amqp_connection value is {_amqp_connection}')
    _amqp_channel = await _amqp_connection.channel()
    print(f'The _amqp_channel value is {_amqp_channel}')
    await _amqp_channel.set_qos(prefetch_count=50)
    _amqp_exchange = await _amqp_channel.declare_exchange(EXCHANGE_NAME, ExchangeType.TOPIC)
    print(f'The _ampqp_exchange value is {_amqp_exchange}')
    # create server queue that will be bound dynamically to room.* and user.* as needed
    _amqp_queue = await _amqp_channel.declare_queue(WS_QUEUE_NAME, durable=False, auto_delete=True)
    print(f'The _ampqp_queue value value is {_amqp_queue}')
    # start consuming
    await _amqp_queue.consume(on_amqp_message)
    print("AMQP initialized and consumer started")

async def amqp_bind_room(room_id):
    rk = f"room.{room_id}"
    await _amqp_queue.bind(_amqp_exchange, routing_key=rk)
    print(f"Bound queue to {rk}")

async def amqp_unbind_room(room_id):
    rk = f"room.{room_id}"
    try:
        await _amqp_queue.unbind(_amqp_exchange, routing_key=rk)
        print(f"Unbound queue from {rk}")
    except Exception:
        pass

async def publish_message(payload, routing_key):
    body = json.dumps(payload).encode()
    message = Message(body, delivery_mode=DeliveryMode.PERSISTENT)
    await _amqp_exchange.publish(message, routing_key=routing_key)

# ---------- AMQP consumer callback ----------
async def on_amqp_message(amqp_msg: aio_pika.IncomingMessage):
    async with amqp_msg.process():  # ensures ack on exit if successful
        try:
            payload = json.loads(amqp_msg.body.decode())
            print(payload)
        except Exception:
            return
        # Deliver to all connected WS handlers on this server who subscribed to the room
        room_id = payload.get("room_id")
        if not room_id:
            return
        subs = room_subscribers.get(int(room_id), set()).copy()
        for ws in subs:
            # schedule send on tornado IOLoop; write_message is coroutine, run on asyncio loop
            # Ensure the type is 'chat' and send the payload directly as expected by client
            payload['type'] = 'chat' # Ensure the type is 'chat' for client-side handling
            await send_to_client(ws, payload)

def list_all_server_ws():
    # room_subscribers holds sets; flatten to unique WS instances
    all_ws = set()
    for s in room_subscribers.values():
        all_ws.update(s)
    return all_ws

async def send_to_client(ws, obj):
    try:
        await ws.write_message(json.dumps(obj))
    except Exception:
        # handle broken connection
        pass