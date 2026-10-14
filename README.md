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

### POST /api/images-to-pdf
Принимает несколько картинок (поле `files`, форматы PNG, JPG, JPEG) и возвращает
один объединённый `.pdf`-файл (`application/pdf`).

Перед сборкой PDF картинки сжимаются **без потери качества**:

- **PNG** пересжимается lossless (`optimize=True` + максимальный уровень
  DEFLATE-сжатия). Пиксели и альфа-канал остаются бит-в-бит неизменными, а
  итоговый PDF становится меньше.
- **JPEG** не перекодируется: `img2pdf` встраивает исходные байты в PDF без
  пересжатия (фильтр `DCTDecode`), поэтому качество не меняется.
- Прозрачность PNG сохраняется: она выносится в отдельный soft mask (`/SMask`).
- Если сжатая версия PNG получилась не меньше исходной, используется исходный файл.

Пример:
```bash
curl -X POST http://localhost:3000/api/images-to-pdf \
  -F "files=@page1.png" -F "files=@photo.jpg" -o merged_images.pdf
```

### GET /api/pdf-info
Информация о сервисе конвертации (поддерживаемые форматы, лимиты, режим сжатия).

## Тестирование

```bash
# Тесты lossless-сжатия картинок и сборки PDF (сервер запускать не нужно)
python3 test_lossless_compression.py

# Тесты HTTP API (требуется запущенный сервер и библиотека requests)
python3 test_pdf_api.py
```

## Структура проекта

```
.
├── app.py              # Основной файл Flask приложения
├── wsgi.py             # WSGI entry point для gunicorn
├── requirements.txt    # Зависимости Python
├── test_lossless_compression.py  # Тесты lossless-сжатия картинок и сборки PDF
├── test_pdf_api.py     # Тесты HTTP API
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