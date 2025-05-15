import cv2, requests, os, re
from utils import gemini_utils as gu
from db_manager import DBManager
from datetime import datetime
from utils.aws_utils import obtener_cliente_s3

class GestorDescripciones:
    def __init__(self, prompt):
        self.prompt = prompt

        # Inicializar conexión con la base de datos
        self.db = DBManager()

        # Intentar inicializar cliente S3
        self.s3 = obtener_cliente_s3()
        self.bucket = "descripciones-personas-magali" 

    def guardar(self, texto, id_persona):
        """
        Guarda una descripción generada en en un bucket de AWS S3 y en la base de datos asociada al ID de la persona.
        """
        self.db.guardar_descripcion(id_persona, texto )

    def guardar_en_s3(self, texto, id_persona):
        """
        Guarda una descripción como archivo TXT en un bucket de AWS S3.
        """
        # Crear el nombre del archivo local temporal
        filename = f"descripcion_{id_persona}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(texto)

        # Ruta en S3
        fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        s3_key = f"personas/persona_{id_persona}/Descripcion/descripcion_{fecha}.txt"

        try:
            self.s3.upload_file(filename, self.bucket, s3_key)
            print(f"[S3] Descripción de {id_persona} guardada en {s3_key}")
        except Exception as e:
            print(f"[ERROR] S3: {e}")
        finally:
            os.remove(filename)  # Limpiar archivo local        

    def describir_con_gemini(self, imagen, id_persona):
        """
        Genera una descripción de una persona usando el modelo Gemini de Google.
        """        

        try:
            # Analizar imagen con Gemini y guardar el resultado
            descripcion = gu.analizar_img_con_gemini(imagen, self.prompt)

            self.guardar(descripcion, id_persona)
            self.guardar_en_s3(descripcion, id_persona)
        except Exception as e:
            print(f"[ERROR] Gemini: ID {id_persona} - {e}")

    def describir_con_vila(self, imagen, id_persona):
        """
        Alternativa: usa un servicio HTTP externo (VILA) para describir la imagen.
        """
        try:
            # Codificar imagen a formato JPEG
            _, img_encoded = cv2.imencode(".jpg", cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB))
            files = {'file': ('persona.jpg', img_encoded.tobytes(), 'image/jpeg')}

            # Enviar al servidor VILA
            r = requests.post("http://18.228.157.19:7000/describe_image_file/", files=files, timeout=60)

            if r.status_code == 200:
                self.guardar(r.text, id_persona)
                self.guardar_en_s3(r.text, id_persona)
            else:
                print(f"[ERROR] VILA: respuesta {r.status_code}")
        except Exception as e:
            print(f"[ERROR] VILA: ID {id_persona} - {e}")
