
# 🧠 Sistema de Detección y Descripción de Personas en Video

Este sistema detecta personas y rostros en tiempo real desde un flujo de video (por ejemplo, RTSP), recorta sus imágenes, analiza visualmente a las personas con IA (Google Gemini o VILA) y guarda sus descripciones e imágenes en una base de datos MySQL.

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
│   ├── gemini_utils.py
│   └── imagenes_utils.py
├── db_manager.py
├── dbconfig.py                # Incluido en el repositorio
├── models/
│   ├── yolo11-person.pt       # Incluido en el repositorio
│   └── yolov11m-face.pt       # Incluido en el repositorio
└── Personas_Detectadas/       # Carpeta de salida automática
```

---

## 🚀 Funcionamiento

1. `main.py`: Captura el video, coordina el procesamiento y muestra resultados en pantalla.
2. `detector_personas.py`: Detecta personas en cada frame utilizando YOLO y recorta su cuerpo.
3. `detector_caras.py`: Envía la imagen a un servidor para detectar rostro y orientación.
4. `gestor_descripciones.py`: Usa Gemini o VILA para generar una descripción detallada.
5. `db_manager.py`: Guarda la información recolectada en una base de datos MySQL.

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

---

## 🔐 Configuración

1. **Clave API de Gemini**  
   Abre `utils/gemini_utils.py` y reemplaza tu clave:

   ```python
   genai.configure(api_key="TU_CLAVE_AQUI")
   ```

2. **Conexión a Base de Datos**  
   Asegúrate de tener un archivo `dbconfig.py` como este:

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

3. **Modelos YOLO**  
   Ambos modelos `.pt` ya están incluidos en la carpeta `models/`.

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

Las imágenes se guardan automáticamente en la ruta:

```
Personas_Detectadas/persona_<ID>/
```

---

## 🧪 Estado del Proyecto

✅ Funcional en tiempo real  
✅ Modular y escalable  
❌ No incluye pruebas automatizadas aún  

---

## ✨ Créditos

Desarrollado por Magali Soto.  
Basado en modelos de código abierto de Ultralytics, Google AI, InsightFace y MediaPipe.

---

