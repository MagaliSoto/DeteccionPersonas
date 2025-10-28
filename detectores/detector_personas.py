import cv2
from ultralytics import YOLO

class DetectorPersonas:
    def __init__(self, ruta_modelo="models/yolo11-person.pt"):
        """
        Inicializa el sistema de detección de personas usando YOLO, junto con
        detección de rostros, descripciones automáticas y gestión de base de datos.
        """
        self.modelo = YOLO(ruta_modelo)

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
        return frame
