# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY src/ ./src/

# Default command: passe main.py an deinen Einstiegspunkt an
CMD ["python", "src/main.py"]