import google.generativeai as genai
from utils import imagenes_utils as iu
from PIL import Image

# Configuración de la API de Gemini
genai.configure(api_key="AIzaSyDYpFaek9ZpYXlSkdd1hNblG1pQiNSERfw")
modelo = genai.GenerativeModel("gemini-2.0-flash")

def analizar_img_con_gemini(img_path, prompt):
    img_mejorada = iu.mejorar_imagen(img_path)
    pil_img = Image.fromarray(img_mejorada)
    respuesta = modelo.generate_content([prompt, pil_img])
    return respuesta.text
