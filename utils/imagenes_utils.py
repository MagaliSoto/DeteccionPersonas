import cv2
import os
import datetime
import mediapipe as mp
from insightface.app import FaceAnalysis

# Inicialización del modelo de rostros
face_model = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
face_model.prepare(ctx_id=0)

# Inicialización de MediaPipe para posturas
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

def mejorar_imagen(img):
    """
    Convierte la imagen a RGB si es necesario.

    Parámetros:
        img (np.array): Imagen en formato BGR o RGB.

    Retorna:
        np.array: Imagen en formato RGB.
    """
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if len(img.shape) == 3 else img

def obtener_orientacion(img):
    """
    Determina la orientación corporal a partir de una imagen.

    Retorna:
        str: 'frente', 'perfil', 'espaldas' o 'desconocido'.
    """
    resultado = pose.process(img)
    if not resultado.pose_landmarks:
        return "desconocido"

    lms = resultado.pose_landmarks.landmark
    nariz = lms[mp_pose.PoseLandmark.NOSE]
    hombro_izq = lms[mp_pose.PoseLandmark.LEFT_SHOULDER]
    hombro_der = lms[mp_pose.PoseLandmark.RIGHT_SHOULDER]

    centro_hombros = (hombro_izq.x + hombro_der.x) / 2

    if nariz.visibility < 0.2:
        return "espaldas"
    elif abs(nariz.x - centro_hombros) > 0.1:
        return "perfil"
    return "frente"

def detectar_rostro_si_frente(img):
    """
    Detecta el rostro solo si la persona está de frente o de perfil.

    Retorna:
        (tuple | None, str): Coordenadas del rostro y orientación detectada.
    """
    img_rgb = mejorar_imagen(img)
    orientacion = obtener_orientacion(img_rgb)

    if orientacion == "espaldas":
        return None, "espaldas"

    rostros = face_model.get(img_rgb)
    if not rostros:
        return None, orientacion

    rostro = rostros[0]
    x1, y1, x2, y2 = map(int, rostro.bbox)
    return (x1, y1, x2, y2), orientacion

def guardar_imagen(imagen, id_interno, carpeta_salida):
    """
    Guarda una imagen en la carpeta correspondiente con un nombre único.

    Retorna:
        str | None: Ruta del archivo guardado o None si hubo error.
    """
    if imagen is None or imagen.size == 0:
        print(f"[ADVERTENCIA] Imagen vacía para ID {id_interno}")
        return None

    carpeta_persona = os.path.join(carpeta_salida, f"persona_{id_interno}")
    os.makedirs(carpeta_persona, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    nombre_archivo = f"Persona_{id_interno}_{timestamp}.jpg"
    ruta_completa = os.path.join(carpeta_persona, nombre_archivo)

    if not cv2.imwrite(ruta_completa, imagen):
        print(f"[ERROR] No se pudo guardar la imagen para ID {id_interno}")
        return None

    print(f"[INFO] Imagen guardada: {ruta_completa}")
    return ruta_completa
