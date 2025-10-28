import cv2
import time
from detectores.detector_personas import DetectorPersonas

def main():
    # ---------------- CONFIGURACIÓN ----------------
    rtsp_in = "rtsp://admin:2Mini001.@192.168.0.204"  # Stream de entrada
    ancho, alto = 1080, 1920

    # Inicializar detector YOLO
    detector = DetectorPersonas()

    # Abrir stream de entrada
    cap = cv2.VideoCapture(rtsp_in)
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la cámara RTSP.")
        return

    # Crear ventana normal
    cv2.namedWindow("Detección de Personas", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Detección de Personas", 960, 540)  # Tamaño de ventana (opcional)

    print("[INFO] Mostrando video. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Frame inválido. Reintentando...")
            time.sleep(0.5)
            continue

        # Redimensionar frame si querés mantener la resolución deseada
        frame = cv2.resize(frame, (ancho, alto))

        # Procesar detección
        frame_procesado = detector.procesar_frame(frame)

        # Mostrar video en ventana normal
        cv2.imshow("Detección de Personas", frame_procesado)

        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Finalizando transmisión...")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
