# Imagen base ligera de Python
FROM python:3.10-slim

# Evitar preguntas durante instalaciones
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    g++ \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . .

# Copiar e instalar las dependencias de Python
COPY requirements.txt /app/requirements.txt

# Usar pip con cache deshabilitado
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Variable de entorno por defecto para la ruta de video
ENV RUTA_VIDEO="rtsp://admin:2Mini001.@192.168.0.195"

# Comando por defecto
CMD ["python", "main.py"]
