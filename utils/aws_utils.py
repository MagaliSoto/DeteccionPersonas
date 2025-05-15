import boto3
from dotenv import load_dotenv

load_dotenv()

def obtener_cliente_s3():
    try:
        s3 = boto3.client('s3')
        return s3
    except Exception as e:
        print(f"[ERROR] No se pudo inicializar el cliente S3: {e}")
        return None
