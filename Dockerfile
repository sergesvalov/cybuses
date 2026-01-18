# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1
# Force Python to send logs straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# Install system dependencies (gcc is often required for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Create an empty cache file and set read/write permissions for the container user
RUN touch bus_cache.json && chmod 666 bus_cache.json

# Inform Docker that the container listens on port 8000 at runtime
EXPOSE 8000

# Set the default command to run the FastAPI server
CMD ["python", "main.py"]