FROM python:3.10-slim

# Отключение кэширования bytecode и включение буферизации логов
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копирование заменяемого списка зависимостей и их установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода проекта
COPY . .

# Команда запуска бота
CMD ["python", "main.py"]
