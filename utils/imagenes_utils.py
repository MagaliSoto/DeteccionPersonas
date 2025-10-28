import cv2, os, datetime, mediapipe as mp


def mejorar_imagen(img):
    """
    Convierte la imagen a RGB si es necesario.

    Parámetros:
        img (np.array): Imagen en formato BGR o RGB.

    Retorna:
        np.array: Imagen en formato RGB.
    """
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if len(img.shape) == 3 else img

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

    return ruta_completa