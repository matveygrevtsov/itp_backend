# Simple Flask Backend

Простой backend на Flask, запускаемый на порту 3000. Поддерживает запуск через Docker.

## Установка

### Обычная установка (без Docker)
1. Убедитесь, что у вас установлен Python 3.7+
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

### Docker установка
Для установки с использованием Docker убедитесь, что у вас установлены:
- Docker
- Docker Compose (рекомендуется)

## Запуск сервера

### Способ 1: Через скрипт управления (рекомендуется без Docker)
```bash
# Дайте права на выполнение
chmod +x manage.sh

# Запустить сервер
./manage.sh start

# Проверить статус
./manage.sh status

# Остановить сервер
./manage.sh stop

# Перезапустить
./manage.sh restart

# Протестировать эндпоинты
./manage.sh test

# Посмотреть логи
./manage.sh logs
```

### Способ 2: Через Docker (рекомендуется для production)
```bash
# Дайте права на выполнение Docker скрипта
chmod +x docker-manage.sh

# Собрать Docker образ
./docker-manage.sh build

# Запустить с docker-compose (рекомендуется)
./docker-manage.sh up

# Проверить статус контейнера
./docker-manage.sh status

# Посмотреть логи
./docker-manage.sh logs

# Протестировать эндпоинты
./docker-manage.sh test

# Остановить
./docker-manage.sh down

# Полная остановка и очистка
./docker-manage.sh clean
```

### Быстрый запуск Docker:
```bash
# С помощью docker-compose
docker-compose up -d

# Или напрямую с Docker
docker build -t flask-backend .
docker run -d --name flask-backend -p 3000:3000 flask-backend
```

### Способ 3: Через gunicorn напрямую
```bash
gunicorn --bind 0.0.0.0:3000 --workers 1 wsgi:app
```

### Способ 4: Через встроенный Flask сервер (только для разработки)
```bash
python app.py
```

Сервер запустится на `http://localhost:3000`

## API Endpoints

### GET /
Основная страница
```json
{
  "message": "Hello from Flask backend!",
  "status": "success",
  "timestamp": "2026-10-13 12:01:00"
}
```

### GET /api/health
Проверка здоровья сервера
```json
{
  "status": "healthy",
  "service": "Flask Backend",
  "port": 3000
}
```

### GET /api/test
Тестовый endpoint
```json
{
  "data": "This is a test endpoint",
  "items": [1, 2, 3, 4, 5]
}
```

### GET /api/echo/<message>
Эхо-эндпоинт
```json
{
  "received": "your-message",
  "echo": "You said: your-message"
}
```

## Структура проекта

```
.
├── app.py              # Основной файл Flask приложения
├── wsgi.py             # WSGI entry point для gunicorn
├── requirements.txt    # Зависимости Python
├── manage.sh           # Скрипт управления сервером
├── run.sh              # Простой скрипт запуска
├── Dockerfile          # Docker конфигурация
├── docker-compose.yml  # Docker Compose конфигурация
├── docker-manage.sh    # Docker management скрипт
└── README.md           # Эта документация
```

## Docker Configuration

### Dockerfile
Использует официальный Python 3.9 slim образ, устанавливает зависимости через pip, копирует код приложения и запускает через gunicorn.

### docker-compose.yml
Упрощает управление контейнером с поддержкой:
- Порта 3000
- Автоматического рестарта
- Volume монтирования для разработки

## Заметки

- Сервер использует CORS (Cross-Origin Resource Sharing) для разрешения запросов из браузера
- Для production использования рекомендуется настроить gunicorn с большим количеством воркеров
- Порт 3000 используется по умолчанию, но может быть изменен в аргументах gunicorn или Docker конфигурации
- Docker обеспечивает изолированное окружение и упрощает деплоймент на разных системах