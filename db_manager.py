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

    def _fusionar_descripciones(self, anterior, nueva):
        """
        Une dos descripciones, evitando duplicados y priorizando mayor nivel de detalle.
        """
        mapa_anterior = self.parsear_descripcion(anterior)
        mapa_nueva = self.parsear_descripcion(nueva)
        mapa_final = {}

        for clave in set(mapa_anterior) | set(mapa_nueva):
            viejo = mapa_anterior.get(clave, "").strip()
            nuevo = mapa_nueva.get(clave, "").strip()

            if not viejo:
                mapa_final[clave] = nuevo
            elif not nuevo:
                mapa_final[clave] = viejo
            elif nuevo != viejo:
                conjunto = set(re.split(r' ?/ ?', viejo)) | set(re.split(r' ?/ ?', nuevo))
                mapa_final[clave] = " / ".join(sorted(conjunto))
            else:
                mapa_final[clave] = viejo

        return "\n\n".join(f"{k}\n\n{v}" for k, v in mapa_final.items())

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
