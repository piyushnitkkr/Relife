FROM python:3.11-slim

WORKDIR /app

# Install system deps for ML libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./server/

WORKDIR /app/server

# Create ml/models directory for bootstrap
RUN mkdir -p ml/models

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
