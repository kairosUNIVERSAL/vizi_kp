FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей (включая шрифты для PDF)
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Запуск
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
