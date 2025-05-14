import cv2, os, time, requests, numpy as np
from ultralytics import YOLO
from db_manager import DBManager

class DetectorCaras:
    def __init__(self, ruta_salida, ruta_entrada, executor):
        """
        Inicializa el detector de caras con un modelo YOLO específico,
        una ruta para guardar imágenes, y un ejecutor para tareas en segundo plano.
        """
        self.modelo = YOLO("models/yolov11m-face.pt")
        self.ruta_entrada = ruta_entrada
        self.ruta_salida = ruta_salida
        os.makedirs(self.ruta_salida, exist_ok=True)

        self.db = DBManager()
        self.executor = executor

    def detectar_rostro_remoto(self, imagen, id_persona, url_servidor="http://18.228.157.19:8000/detectar_rostro"):
        """
        Envía una imagen a un servidor remoto para detectar el rostro y orientación.

        Retorna:
            - Coordenadas del rostro (x1, y1, x2, y2)
            - Orientación estimada (frente, perfil, espaldas, etc.)
        """
        if imagen is not None and isinstance(imagen, np.ndarray):
            _, img_encoded = cv2.imencode('.jpg', imagen)
        else:
            print("La imagen no es válida")
            return None, "error"

        files = {
            "file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")
        }
        params = {"track_id": id_persona}

        try:
            resp = requests.post(url_servidor, params=params, files=files, timeout=5)
        except requests.RequestException as e:
            print(f"[ERROR] Conexión al servidor: {e}")
            return None, "error"

        if resp.status_code != 200:
            print(f"[ERROR] Código {resp.status_code}: {resp.text}")
            return None, "error"

        datos = resp.json()
        return datos.get("box"), datos.get("orientacion")

    def detectar_caras_en_imagen(self, imagen, id_persona):
        """
        Dado un frame y un ID de persona, detecta el rostro si existe y lo guarda en disco.

        Retorna:
            - Coordenadas recorte rostro (x1, y1, x2, y2)
        """
        coordenadas, orientacion = self.detectar_rostro_remoto(imagen, id_persona)

        if coordenadas is None:
            print(f"[INFO] ID {id_persona}: Sin rostro detectado (orientación: {orientacion})")
            return None

        # Ajustar coordenadas al tamaño de la imagen
        x1, y1, x2, y2 = coordenadas
        h, w = imagen.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        recorte = imagen[y1:y2, x1:x2]

        if recorte.size == 0:
            print(f"[ADVERTENCIA] ID {id_persona}: recorte vacío")
            return None

        # Guardar imagen del rostro recortado
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        carpeta_id = os.path.join(self.ruta_salida, f"persona_{id_persona}", "Caras")
        os.makedirs(carpeta_id, exist_ok=True)
        nombre_archivo = f"Cara_{id_persona}_{timestamp}.jpg"
        ruta_archivo = os.path.join(carpeta_id, nombre_archivo)
        cv2.imwrite(ruta_archivo, recorte)

        print(f"[INFO] ID {id_persona}: Cara guardada en {ruta_archivo} (orientación: {orientacion})")

        # Registrar en base de datos en segundo plano
        self.executor.submit(self.db.guardar_imagen_cara, id_persona, carpeta_id)

        return x1, y1, x2, y2
