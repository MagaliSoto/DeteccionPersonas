import os, google.generativeai as genai
from utils import imagenes_utils as iu
from PIL import Image

# Configuración segura
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

modelo = genai.GenerativeModel("gemini-2.0-flash")

def analizar_img_con_gemini(img_path, prompt):
    img_mejorada = iu.mejorar_imagen(img_path)
    pil_img = Image.fromarray(img_mejorada)
    respuesta = modelo.generate_content([prompt, pil_img])
    return respuesta.text
