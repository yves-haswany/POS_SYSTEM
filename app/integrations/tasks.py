from redis import Redis
from rq import Queue

redis_conn = Redis()
queue = Queue(connection=redis_conn)

def enqueue_push_order(provider, order_id):
    queue.enqueue("app.workers.tasks.push_order", provider, order_id)