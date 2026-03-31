# Use a tiny Python image
FROM python:3.14-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (needed if you use subprocess to call other tools)
RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script into the container
COPY listener.py .

# Run the script
CMD ["python", "-u", "listener.py"]
