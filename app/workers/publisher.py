import json

import pika
from services.crud.prediction import create_prediction
from workers.connection import RABBITMQ_HOST, get_rabbitmq_connection


def publish_prediction_task(User, image_path: str, model_name: str, cost: float, prediction_id, session):
    task_data = {
        "task_id": prediction_id,
        "user_id": User.id,
        "username": User.username,
        "balance": User.balance,
        "image_path": image_path,
        "model_name": model_name,
        "cost": cost
    }

    print(task_data)

    connection, channel = get_rabbitmq_connection("ml_tasks")

    channel.basic_publish(
        exchange="",
        routing_key="ml_tasks",
        body=json.dumps(task_data),
        properties=pika.BasicProperties(delivery_mode=2),
    )

    connection.close()
    print(f"[x] Задача предсказания отправлена: {task_data}")

    create_prediction(
        user_id=User.id,
        photo_path=task_data["image_path"],
        cost=task_data["cost"],
        session=session
    )
