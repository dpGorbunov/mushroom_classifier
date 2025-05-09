import pika

RABBITMQ_HOST = "rabbitmq"


def get_rabbitmq_connection(queue_name: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    return connection, channel
