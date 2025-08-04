# 1. Basisimage
FROM python:3.12-slim

# 2. Arbeitsverzeichnis
WORKDIR /app

# 3. Systempakete installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 5. Projektcode kopieren
COPY . .

# 6. Cloud Run Port
ENV PORT 8080

# 7. Functions Framework starten
CMD exec functions-framework --target run_script --port $PORT
