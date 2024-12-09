FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wkhtmltopdf curl build-essential libssl-dev libffi-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py .
COPY ./src ./src

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
