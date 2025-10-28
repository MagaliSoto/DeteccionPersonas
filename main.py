import cv2
import time
from detectores.detector_personas import DetectorPersonas
from smstreamer import Streamer  # <- importamos el streamer

def main():
    # ---------------- CONFIGURACIÓN ----------------
    rtsp_in = "rtsp://admin:2Mini001.@192.168.0.204"  # Stream de entrada
    ancho, alto = 1080, 1920
    puerto_stream = 8080  # puerto donde se verá el video por navegador

    # Inicializar detector YOLO
    detector = DetectorPersonas()

    # Abrir stream de entrada
    cap = cv2.VideoCapture(rtsp_in)
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la cámara RTSP.")
        return

    # Inicializar SMStreamer
    streamer = Streamer(width=ancho, height=alto, fps=20, port=puerto_stream)

    print(f"[INFO] Mostrando video por http://<IP_RASPBERRY>:{puerto_stream}")
    print("[INFO] Presiona Ctrl+C para salir.")

    try:
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

            # Enviar frame al streamer
            streamer.send(frame_procesado)

    except KeyboardInterrupt:
        print("[INFO] Finalizando transmisión...")

    finally:
        cap.release()
        streamer.close()

if __name__ == "__main__":
    main()
