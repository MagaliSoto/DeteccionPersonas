import cv2, os, datetime, boto3, mediapipe as mp
from insightface.app import FaceAnalysis
from utils.aws_utils import obtener_cliente_s3

# Inicialización del modelo de rostros
face_model = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
face_model.prepare(ctx_id=0)

# Inicialización de MediaPipe para posturas
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

# Inicializar cliente de AWS S3
s3 = obtener_cliente_s3()
BUCKET_NAME = "descripciones-personas-magali"

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

import os
import datetime
import cv2

def guardar_imagen(imagen, id_interno, carpeta_salida, tipo):
    """
    Guarda una imagen (Cuerpo o Cara) en la carpeta correspondiente con un nombre único.

    Parámetros:
        imagen (ndarray): Imagen a guardar.
        id_interno (str): ID único de la persona.
        carpeta_salida (str): Carpeta raíz donde guardar imágenes.
        tipo (str): 'Cuerpo' o 'Caras'. Define la subcarpeta y nombre del archivo.

    Retorna:
        str | None: Ruta del archivo guardado o None si hubo error.
    """
    if imagen is None or imagen.size == 0:
        print(f"[ADVERTENCIA] Imagen vacía para ID {id_interno}")
        return None

    # Carpeta: personas/persona_X/Cuerpo o Caras
    carpeta_persona = os.path.join(carpeta_salida, f"persona_{id_interno}", tipo)
    os.makedirs(carpeta_persona, exist_ok=True)

    # Nombre único con timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    nombre_archivo = f"{tipo}_{id_interno}_{timestamp}.jpg"
    ruta_completa = os.path.join(carpeta_persona, nombre_archivo)

    # Guardar imagen localmente
    if not cv2.imwrite(ruta_completa, imagen):
        print(f"[ERROR] No se pudo guardar la imagen para ID {id_interno}")
        return None

    print(f"[INFO] Imagen guardada: {ruta_completa}")

    # Subir a S3
    subida_exitosa = guardar_imagen_en_s3(ruta_completa, id_interno, tipo)
    if not subida_exitosa:
        print(f"[ERROR] No se pudo subir la imagen a S3 para ID {id_interno} ({tipo})")

    return ruta_completa


def guardar_imagen_en_s3(ruta_imagen_local, id_interno, tipo="Cuerpo"):
    """
    Sube una imagen al bucket de S3 en la carpeta correspondiente.

    Parámetros:
        ruta_imagen_local (str): Ruta de la imagen guardada localmente.
        id_interno (str): ID único de la persona.
        tipo (str): Subcarpeta (ej. 'Cara' o 'Cuerpo').

    Retorna:
        bool: True si se subió correctamente, False si hubo error.
    """
    try:
        nombre_archivo = os.path.basename(ruta_imagen_local)
        clave_s3 = f"personas/persona_{id_interno}/{tipo}/{nombre_archivo}"

        s3.upload_file(ruta_imagen_local, BUCKET_NAME, clave_s3)
        print(f"[S3] Imagen subida a: {clave_s3}")
        return True
    except Exception as e:
        print(f"[ERROR] Falló la subida a S3: {e}")
        return False