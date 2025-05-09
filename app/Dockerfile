FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

COPY ./ /app

CMD ["python", "api.py"]