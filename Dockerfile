# Use a lightweight Python 3.11 image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (needed for some media processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker cache
COPY requirment.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirment.txt

# Copy the rest of your source code
COPY . .

# Command to run the bot
CMD ["python", "main.py"]