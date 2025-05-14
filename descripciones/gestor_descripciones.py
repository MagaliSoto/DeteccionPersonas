import cv2, requests, time
from utils import gemini_utils as gu
from db_manager import DBManager

class GestorDescripciones:
    def __init__(self):
        # Inicializar conexión con la base de datos
        self.db = DBManager()
    
    def guardar(self, texto, id_persona):
        """
        Guarda una descripción generada en la base de datos asociada al ID de la persona.
        """
        self.db.guardar_descripcion(id_persona, texto)

    def describir_con_gemini(self, imagen, id_persona):
        """
        Genera una descripción de una persona usando el modelo Gemini de Google.
        """
        prompt = (
            "Describe con el mayor detalle posible a la persona en esta imagen..."
        )
        try:
            # Analizar imagen con Gemini y guardar el resultado
            descripcion = gu.analizar_img_con_gemini(imagen, prompt)
            self.guardar(descripcion, id_persona)
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
            else:
                print(f"[ERROR] VILA: respuesta {r.status_code}")
        except Exception as e:
            print(f"[ERROR] VILA: ID {id_persona} - {e}")
