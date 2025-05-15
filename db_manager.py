import mysql.connector
import dbconfig
import time
import re

class DBManager:
    def guardar_imagen_cuerpo(self, track_id, ruta_cuerpo):
        """
        Guarda la ruta de la imagen del cuerpo asociada a un ID.
        """
        sql = """
        INSERT INTO registro_personas (ID, Imagen_cuerpo)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE Imagen_cuerpo = VALUES(Imagen_cuerpo);
        """
        self._ejecutar_sql(sql, (track_id, ruta_cuerpo), f"Imagen cuerpo ID {track_id}")

    def guardar_imagen_cara(self, track_id, ruta_cara):
        """
        Guarda la ruta de la imagen de la cara asociada a un ID.
        """
        sql = """
        INSERT INTO registro_personas (ID, Imagen_cara)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE Imagen_cara = VALUES(Imagen_cara);
        """
        self._ejecutar_sql(sql, (track_id, ruta_cara), f"Imagen cara ID {track_id}")

    def guardar_descripcion(self, track_id, nueva_desc):
        """
        Guarda una descripción textual fusionada con la anterior, si existe.
        """
        fecha = time.strftime('%Y-%m-%d %H:%M:%S')
        nueva_desc = nueva_desc.strip()

        desc_anterior = self._obtener_descripcion(track_id)

        if desc_anterior:
            descripcion_final = self._fusionar_descripciones(desc_anterior, nueva_desc)
        else:
            descripcion_final = nueva_desc

        sql = """
        INSERT INTO registro_personas (ID, Descripcion, Fecha_registro)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE Descripcion = VALUES(Descripcion), Fecha_registro = VALUES(Fecha_registro);
        """
        self._ejecutar_sql(sql, (track_id, descripcion_final, fecha), f"Descripción ID {track_id}")

    def _obtener_descripcion(self, track_id):
        """
        Recupera la descripción actual de una persona desde la base de datos.
        """
        try:
            conn = dbconfig.conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT Descripcion FROM registro_personas WHERE ID = %s", (track_id,))
            row = cursor.fetchone()
            return row[0] if row else ""
        except mysql.connector.Error as err:
            print(f"[ERROR BD] Obtener descripción ID {track_id}: {err}")
            return ""
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
                
    def parsear_descripcion(self, texto):
        """
        Extrae secciones del texto formateadas con títulos en negrita (**Título**)
        y devuelve un diccionario {seccion: contenido}.
        """
        import re
        bloques = re.split(r"\*\*(.*?)\*\*", texto)
        mapa = {}
        i = 1
        while i < len(bloques):
            clave = bloques[i].strip()
            valor = bloques[i+1].strip()
            if clave in mapa:
                mapa[clave] += "\n" + valor
            else:
                mapa[clave] = valor
            i += 2
        return mapa

    def _fusionar_descripciones(self, anterior, nueva):
        """
        Une dos descripciones sección por sección, evitando duplicados y manteniendo formato limpio.
        """
        mapa_anterior = self.parsear_descripcion(anterior)
        mapa_nueva = self.parsear_descripcion(nueva)

        orden = [
            "Apariencia General", "Rostro", "Cabello", "Ropa", "Accesorios",
            "Postura", "Acciones", "Entorno", "Otros Detalles"
        ]

        mapa_final = {}

        for clave in set(mapa_anterior.keys()).union(mapa_nueva.keys()):
            texto1 = mapa_anterior.get(clave, "").strip()
            texto2 = mapa_nueva.get(clave, "").strip()

            frases1 = set([f.strip("-•* ").strip() for f in texto1.split("\n") if f.strip()])
            frases2 = set([f.strip("-•* ").strip() for f in texto2.split("\n") if f.strip()])

            frases_unidas = sorted(frases1.union(frases2))
            if frases_unidas:
                texto_final = "\n".join(f"* {f}" for f in frases_unidas)
                mapa_final[clave] = texto_final

        # Ordenar las secciones según la lista de orden predeterminada
        descripcion_final = ""
        for clave in orden:
            if clave in mapa_final:
                descripcion_final += f"**{clave}**\n{mapa_final[clave]}\n\n"

        # Agregar secciones no contempladas en la lista de orden
        for clave in mapa_final:
            if clave not in orden:
                descripcion_final += f"**{clave}**\n{mapa_final[clave]}\n\n"

        return descripcion_final.strip()

    def _ejecutar_sql(self, sql, params, log_mensaje):
        """
        Ejecuta una consulta SQL de forma segura.
        """
        try:
            conn = dbconfig.conectar()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            print(f"[BD] Guardado correcto: {log_mensaje}")
        except mysql.connector.Error as err:
            print(f"[ERROR BD] {log_mensaje}: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
