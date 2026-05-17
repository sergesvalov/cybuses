FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Make the startup script executable
RUN chmod +x start.sh

EXPOSE 8000 8888

# Run both services: FastAPI (8000) and MCP (8888)
CMD ["./start.sh"]