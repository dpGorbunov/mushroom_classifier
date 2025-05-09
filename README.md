# 🍄 Mushroom Identification Service

**Сервис для определения видов грибов** по фотографии с использованием нейросетевых моделей

# Инструкция по запуску проекта

---

## 1. Необходимые компоненты
- Docker и Docker Compose (версия 1.29+)
- Файл `.env` с настройками (см. ниже)

---

## 2. Настройка окружения

### Создание файла `.env`
В корневой папке проекта создайте файл `.env` с следующими параметрами:
```dotenv
DB_HOST=postgres_db
DB_PORT=5432
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=your_db_name
SECRET_KEY=your_secret_key

Пример:
DB_HOST=database
DB_PORT=5432
DB_USER=postgres
DB_PASS=1234
DB_NAME=sa
SECRET_KEY=06699c43232730d4d466edcd003acfb2c8f9341408da2b3f04bc9c435915a

```

---

## 3. Запуск приложения

### Запуск через Docker Compose
1. **Построение и запуск контейнеров**:
   ```bash
   docker-compose up --build
   ```
   - Запустятся контейнеры: PostgreSQL, RabbitMQ, FastAPI-сервис, Worker и Nginx.

2. **Остановка контейнеров**:
   ```bash
   docker-compose down
   ```

---

## 4. Проверка работы

### Веб-интерфейс
- Откройте в браузере: `http://localhost`
- Для доступа к админке RabbitMQ: `http://localhost:15672` (логин/пароль из `.env`)

### API-тестирование
- **Swagger-документация**: `http://localhost/docs`
- Пример запроса на предсказание:
  ```bash
  curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/путь/к/файлу.jpg" \
  http://localhost/predict
  ```

### Работа с базой данных
- Инициализация таблиц (если нужно):
  ```bash
  docker-compose run --rm app python app/main.py
  ```

---

## 5. Особенности

### Worker-сервис
- Обрабатывает задания из очереди RabbitMQ.
- Для увеличения параллелизма измените `replicas: 2` в `docker-compose.yml`.

### Баланс пользователей
- Списание средств происходит при отправке фото для распознавания.
- Пополнение баланса через форму на странице `/dashboard`.

### Модели распознавания
- Используется модель `dima806/mushrooms_image_detection` из Hugging Face.
- Для замены модели измените код в `app/models_class/ml_model.py`.

---
