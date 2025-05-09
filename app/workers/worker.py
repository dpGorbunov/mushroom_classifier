import io
import json
import logging
import os

import torch
from database.database import get_session
from models.prediction import PredictionStatus
from models_class.ml_model import MushroomModel
from models_class.ml_task import IdentificationTask
from models_class.user import MushroomAppUser
from PIL import Image
from services.crud.prediction import (update_prediction_result,
                                      update_prediction_status)
from services.crud.user import get_user_by_id, update_user_balance
from torchvision import transforms
from workers.connection import RABBITMQ_HOST, get_rabbitmq_connection

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "worker.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

models = {}


def load_model(model: str):
    if model not in models:
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", f"{model}.pth")
        try:
            models[model] = torch.load(model_path, weights_only=False)
            models[model].eval()
            logging.info(f"Модель '{model}' загружена успешно.")
        except FileNotFoundError:
            logging.error(f"Модель '{model}' не найдена.")
            raise FileNotFoundError(f"Модель '{model}' не найдена.")
        except Exception as e:
            logging.exception(f"Не удалось загрузить модель '{model}': {e}")
            raise e
    return models[model]


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])


def process_prediction(task_data):
    with next(get_session()) as session:
        try:
            user = get_user_by_id(task_data["user_id"], session)

            with open(task_data["image_path"], "rb") as img_file:
                image_bytes = img_file.read()

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image = transform(image).unsqueeze(0)

            ml_task = IdentificationTask(
                user=MushroomAppUser(user.id, user.username, user.balance),
                task_id=task_data["task_id"],
                photo=image,
                photo_path=task_data["image_path"],
                model=MushroomModel(),
                cost=task_data["cost"]
            )

            update_prediction_status(task_data["task_id"], PredictionStatus.PROCESSING, session)
            ml_task.run_identification()

            update_prediction_result(task_data["task_id"], ml_task.result, session)
            update_prediction_status(task_data["task_id"], PredictionStatus.COMPLETED, session)

            update_user_balance(user.id, -task_data["cost"], session)

            logging.info(f"✅ Предсказание выполнено: ID {task_data['task_id']}, результат: {ml_task.result}")

        except Exception as e:
            logging.exception(f"Ошибка обработки предсказания: {e}")
            update_prediction_status(task_data["task_id"], PredictionStatus.FAILED, session)


def callback(ch, method, properties, body):
    task_data = json.loads(body)
    logging.info(f"📩 Получено сообщение: {task_data}")
    process_prediction(task_data)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker():
    try:
        connection, channel = get_rabbitmq_connection("ml_tasks")
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue="ml_tasks", on_message_callback=callback)

        logging.info("Worker запущен и ожидает сообщений...")
        channel.start_consuming()

    except Exception as e:
        logging.exception(f"Worker завершился с ошибкой: {e}")


if __name__ == "__main__":
    start_worker()
