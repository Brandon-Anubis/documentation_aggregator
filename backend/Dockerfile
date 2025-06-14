# Use the official Playwright image to ensure all dependencies are present
FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

# Set the working directory
WORKDIR /app

# 1. Install system dependencies first (least frequently changed)
# Use DEBIAN_FRONTEND to avoid interactive prompts.
# This layer will be cached unless you add more system packages.
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y wkhtmltopdf && \
    rm -rf /var/lib/apt/lists/*

# 2. Copy only the requirements file and install Python packages
# This is the next most stable layer. It will only be rebuilt if you change requirements.txt.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the rest of your application code
# This is the most frequently changed part. By copying it last, we ensure that
# changes to your Python code don't cause the system and Python package
# dependencies to be re-installed every time.
COPY config.py .
COPY ./src ./src

# Expose the port your application will run on
EXPOSE 8000

# Command to run your application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]