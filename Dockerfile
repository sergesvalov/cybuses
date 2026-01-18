FROM python:3.11-slim

WORKDIR /app

# Set PYTHONPATH so Python can find the 'parsers' module in /app
ENV PYTHONPATH=/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create the cache file and grant read/write permissions for all users
# This prevents 'Permission denied' errors in Docker
RUN touch bus_cache.json && chmod 666 bus_cache.json

# Expose the FastAPI port
EXPOSE 8000

# Start the application
CMD ["python", "main.py"]