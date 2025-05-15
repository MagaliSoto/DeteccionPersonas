
# 🧠 Sistema de Detección y Descripción de Personas en Video

Este sistema detecta personas y rostros en tiempo real desde un flujo de video (por ejemplo, RTSP), recorta sus imágenes, analiza visualmente a las personas con IA (Google Gemini o VILA), y guarda sus descripciones e imágenes en una base de datos MySQL **y en un bucket S3**.

---

## 📂 Estructura del Proyecto

```
.
├── main.py
├── descripciones/
│   └── gestor_descripciones.py
├── detectores/
│   ├── detector_personas.py
│   └── detector_caras.py
├── utils/
│   ├── aws_utils.py               # ✅ Subida a S3
│   ├── gemini_utils.py            # 🔑 Clave API de Gemini
│   └── imagenes_utils.py          # 📸 Guardado local y S3
├── resultados/                    # 🗂️ Carpeta temporal para resultados
├── db_manager.py
├── dbconfig.py                    # 🔧 Configuración DB
├── models/
│   ├── yolo11-person.pt
│   └── yolov11m-face.pt
├── Personas_Detectadas/           # 📁 Salida automática
└── README.md
```

---

## 🚀 Funcionamiento

1. `main.py`: Captura el video, coordina el procesamiento y muestra resultados en pantalla.
2. `detector_personas.py`: Detecta personas en cada frame utilizando YOLO y recorta su cuerpo.
3. `detector_caras.py`: Envía la imagen a un servidor para detectar rostro y orientación.
4. `gestor_descripciones.py`: Usa Gemini o VILA para generar una descripción detallada.
5. `imagenes_utils.py`: Guarda imágenes en disco y las sube a AWS S3.
6. `aws_utils.py`: Maneja la conexión y subida a un bucket S3.
7. `db_manager.py`: Guarda la información recolectada en una base de datos MySQL.

---

## ⚙️ Requisitos

- Python ≥ 3.8
- OpenCV
- Ultralytics YOLO
- MediaPipe
- InsightFace
- google-generativeai
- requests
- mysql-connector-python
- boto3
- python-dotenv

---

## 🔐 Configuración

### 1. Clave API de Gemini  
Abre `utils/gemini_utils.py` y reemplaza tu clave:

```python
genai.configure(api_key="TU_CLAVE_AQUI")
```

O bien, colócala en `.env`:

```
GEMINI_API_KEY=tu_clave
```

### 2. Conexión a Base de Datos  
Archivo `dbconfig.py`:

```python
def conectar():
    import mysql.connector
    return mysql.connector.connect(
        host="localhost",
        user="usuario",
        password="contraseña",
        database="nombre_base_datos"
    )
```

### 3. Configuración AWS S3  
En el archivo `.env`, agrega:

```
AWS_ACCESS_KEY_ID=tu_clave
AWS_SECRET_ACCESS_KEY=tu_secreto
AWS_BUCKET_NAME=nombre_del_bucket
AWS_REGION=us-east-1
```

---

## ▶️ Ejecución

```bash
python main.py
```

Presiona `ESC` para salir de la visualización en vivo.

---

## 🧠 Tecnologías Usadas

- **YOLOv8**: Detección de personas.
- **Google Gemini**: Generación de descripciones detalladas.
- **MediaPipe Pose**: Determinación de orientación corporal.
- **InsightFace**: Detección facial robusta.
- **VILA**: Alternativa para descripciones desde servidor HTTP.
- **AWS S3**: Almacenamiento remoto de resultados.

---

## 🗃️ Estructura de la Base de Datos

La tabla `registro_personas` debe tener al menos las siguientes columnas:

```sql
CREATE TABLE registro_personas (
    ID INT PRIMARY KEY,
    Imagen_cuerpo TEXT,
    Imagen_cara TEXT,
    Descripcion TEXT,
    Fecha_registro DATETIME
);
```

---

## 📸 Almacenamiento de Resultados

- **Local**:  
  ```
  Personas_Detectadas/persona_<ID>/
  ```

- **Remoto (S3)**:  
  ```
  s3://<nombre_bucket>/persona_<ID>/
  ```

- **Temporales**:  
  Se almacenan brevemente en `resultados/` antes de subirlos.

---

## 🧪 Estado del Proyecto

✅ Funcional en tiempo real  
✅ Modular y escalable  
✅ Soporte para S3  
❌ No incluye pruebas automatizadas aún  

---

## ✨ Créditos

Desarrollado por Magali Soto.  
Basado en modelos de código abierto de Ultralytics, Google AI, InsightFace, MediaPipe y AWS.

---
