FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT 8080

CMD exec functions-framework --target run_script --source main.py --port $PORT
