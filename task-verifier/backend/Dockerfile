# Imagen base oficial de Python, slim = más liviana
FROM python:3.11-slim

# Evita que Python escriba .pyc y bufferee stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Primero copiamos solo requirements para aprovechar caché de Docker
# Si no cambian las deps, Docker no las reinstala en cada build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ahora sí copiamos el código
COPY . .

# Carpeta para fotos subidas localmente
RUN mkdir -p /app/uploads

EXPOSE 8000

# --reload activo: detecta cambios en el código sin reiniciar el contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]