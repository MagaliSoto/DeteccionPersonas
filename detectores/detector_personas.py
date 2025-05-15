import cv2, os, time
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLO
from detectores.detector_caras import DetectorCaras
from utils import imagenes_utils as iu
from db_manager import DBManager

class DetectorPersonas:
    def __init__(self, ruta_video, carpeta_salida, funcion_descripcion, ruta_modelo="models/yolo11-person.pt", executor=None):
        """
        Inicializa el sistema de detección de personas usando YOLO, junto con
        detección de rostros, descripciones automáticas y gestión de base de datos.
        """
        self.ruta_video = ruta_video
        self.video = cv2.VideoCapture(ruta_video)
        self.modelo = YOLO(ruta_modelo)
        
        self.track_id_tiempo = {}  # Para controlar frecuencia de descripción por ID
        self.intervalo_descripcion = 2  # segundos
        self.carpeta_salida = carpeta_salida
        os.makedirs(self.carpeta_salida, exist_ok=True)

        self.funcion_descripcion = funcion_descripcion
        self.executor = executor or ThreadPoolExecutor(max_workers=4)
        self.detector_caras = DetectorCaras(self.carpeta_salida, self.executor)

        self.db = DBManager()

    def cortar_y_guardar(self, frame, caja, id_persona):
        """
        Recorta la región de la persona detectada, guarda la imagen y la registra.

        Retorna:
            np.array: Imagen recortada
        """
        x1, y1, x2, y2 = map(int, caja)
        imagen = frame[y1:y2, x1:x2]

        carpeta_persona = os.path.join(self.carpeta_salida, f"persona_{id_persona}")
        os.makedirs(carpeta_persona, exist_ok=True)

        #Guarda la ruta de la carpeta con las imagenes del cuerpo en la base de datos
        self.executor.submit(self.db.guardar_imagen_cuerpo, id_persona, carpeta_persona)    
        #Guarda las imagenes del cuerpo en una carpeta local y en un bucket s3
        self.executor.submit(iu.guardar_imagen, imagen, id_persona, self.carpeta_salida, "Cuerpo")

        return imagen

    def procesar_frame(self, frame):
        """
        Procesa un frame para detectar personas, cortar sus imágenes, describirlas
        y detectar sus rostros.

        Retorna:
            np.array: Frame con anotaciones visuales
        """
        resultados = self.modelo.track(frame, conf=0.7, iou=0.5, tracker="botsort.yaml", persist=True, verbose=False)
        if not resultados or resultados[0].boxes is None:
            return frame

        # Extraer datos de detección
        cajas = resultados[0].boxes.xyxy.int().cpu().tolist()
        clases = resultados[0].boxes.cls.int().cpu().tolist()
        ids = resultados[0].boxes.id.int().cpu().tolist() if resultados[0].boxes.id is not None else [-1] * len(cajas)

        for caja, clase, id_persona in zip(cajas, clases, ids):
            x1, y1, x2, y2 = map(int, caja)

            # Dibujar caja de persona
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, f"{self.modelo.names[clase]} ID:{id_persona}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # Recortar y guardar imagen
            imagen = self.cortar_y_guardar(frame, caja, id_persona)

            # Generar descripción textual si ha pasado suficiente tiempo
            ahora = time.time()
            if ahora - self.track_id_tiempo.get(id_persona, 0) >= self.intervalo_descripcion:
                self.track_id_tiempo[id_persona] = ahora
                self.executor.submit(self.funcion_descripcion, imagen, id_persona)

            # Detección de rostro en el recorte
            resultado = self.detector_caras.detectar_caras_en_imagen(imagen, id_persona)
            if resultado:
                cx1, cy1, cx2, cy2 = resultado
                cx1 += caja[0]; cy1 += caja[1]; cx2 += caja[0]; cy2 += caja[1]  # Ajustar a coordenadas globales
                cv2.rectangle(frame, (cx1, cy1), (cx2, cy2), (0, 255, 0), 2)
                cv2.putText(frame, f"Cara ID:{id_persona}", (cx1, cy1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return frame
