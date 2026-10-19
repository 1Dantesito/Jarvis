FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema mínimas para multimedia y red
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar dependencias Python
COPY requirements-cloud.txt .
RUN pip install --no-cache-dir -r requirements-cloud.txt

# Copiar código fuente
COPY . .

# Variables de entorno
ENV HOST=0.0.0.0
ENV PORT=5001
ENV PYTHONUNBUFFERED=1

EXPOSE 5001

# Comando de inicio usando el puerto asignado dinámicamente por plataformas cloud ($PORT)
CMD ["sh", "-c", "uvicorn api.server:app --host 0.0.0.0 --port ${PORT:-5001}"]
