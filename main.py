import cv2
from queue import Queue
from threading import Thread
from descripciones.gestor_descripciones import GestorDescripciones
from detectores.detector_personas import DetectorPersonas
from concurrent.futures import ThreadPoolExecutor

def principal():
    # Dirección del flujo de video (puede ser RTSP, cámara IP, etc.)
    ruta_video = "rtsp://admin:2Mini001.@192.168.0.195"
    carpeta_salida = "Personas_Detectadas"  # Carpeta donde se guardarán las imágenes detectadas

    # Gestor para generar descripciones automáticas de las personas
    gestor_descripciones = GestorDescripciones()

    # Ejecutores en segundo plano para tareas paralelas como descripciones y base de datos
    ejecutor = ThreadPoolExecutor(max_workers=4)

    # Inicialización del detector de personas
    detector = DetectorPersonas(
        ruta_video,
        carpeta_salida,
        gestor_descripciones.describir_con_gemini,
        executor=ejecutor
    )

    # Colas para enviar y recibir frames entre hilos
    cola_frames = Queue(maxsize=5)
    cola_resultados = Queue(maxsize=5)

    # Hilo trabajador que procesa los frames usando el detector
    def trabajador():
        while True:
            item = cola_frames.get()
            if item is None:
                break
            indice, frame = item
            procesado = detector.procesar_frame(frame.copy())
            cola_resultados.put((indice, procesado))
            cola_frames.task_done()

    # Iniciar hilo en modo demonio (termina automáticamente al cerrar el programa)
    Thread(target=trabajador, daemon=True).start()

    # Obtener video y configurar resolución
    video = detector.video
    fps = int(video.get(cv2.CAP_PROP_FPS)) or 30
    ancho_frame, alto_frame = 1280, 720
    contador_frames = 0
    ultimo_frame_procesado = None

    # Bucle principal de lectura del video
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break

        # Redimensionar el frame a la resolución deseada
        frame = cv2.resize(frame, (ancho_frame, alto_frame))

        # Enviar solo uno de cada N frames para evitar sobrecarga
        if contador_frames % 5 == 0 and not cola_frames.full():
            cola_frames.put((contador_frames, frame.copy()))

        # Si hay resultados procesados disponibles, mostrarlos
        while not cola_resultados.empty():
            _, ultimo_frame_procesado = cola_resultados.get()

        # Mostrar el último frame procesado, o el frame crudo si no hay
        mostrar = ultimo_frame_procesado if ultimo_frame_procesado is not None else frame
        cv2.imshow("Detección", mostrar)

        contador_frames += 1

        # Presionar ESC (27) para salir
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Finalizar correctamente
    cola_frames.put(None)           # Señal para terminar el hilo
    video.release()                 # Liberar la cámara o video
    cv2.destroyAllWindows()         # Cerrar ventanas de OpenCV
    ejecutor.shutdown(wait=True)   # Esperar que terminen los hilos

if __name__ == "__main__":
    principal()
