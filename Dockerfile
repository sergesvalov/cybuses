FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Делаем скрипт запуска исполняемым
RUN chmod +x start.sh

EXPOSE 8000 8888

# Запускаем оба сервиса: FastAPI (8000) + MCP (8888)
CMD ["./start.sh"]