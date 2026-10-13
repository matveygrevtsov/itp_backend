# Используем официальный Python образ как базовый
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения в контейнер
COPY . .

# Устанавливаем переменную окружения для Flask
ENV FLASK_APP=app.py

# Открываем порт, на котором работает приложение
EXPOSE 3000

# Команда для запуска приложения
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "1", "wsgi:app"]