import os
import requests

def hay_conexion():
    try:
        requests.get("http://google.com", timeout=3)
        return True
    except:
        return False

def sincronizar():
    ruta_pendientes = "pendientes"
    for tienda in os.listdir(ruta_pendientes):
        ruta_tienda = os.path.join(ruta_pendientes, tienda)
        if os.path.isdir(ruta_tienda):
            for archivo in os.listdir(ruta_tienda):
                if archivo.endswith(".jpg") or archivo.endswith(".png"):
                    ruta_imagen = os.path.join(ruta_tienda, archivo)
                    ruta_txt = ruta_imagen.replace(".jpg", ".txt").replace(".png", ".txt")

                    # Enviar al servidor IA
                    try:
                        with open(ruta_imagen, "rb") as img, open(ruta_txt, "r") as txt:
                            observacion = txt.read()
                            files = {"file": img}
                            data = {"texto": observacion}
                            res = requests.post("http://localhost:8000/analizar", files=files, data=data)
                            if res.status_code == 200:
                                respuesta = res.json()
                                print(f"[✔] Enviado y analizado correctamente: {archivo}")
                                print(f"    Observación: {respuesta['observacion']}")
                                print("    Predicciones:")
                                for pred in respuesta["predicciones"]:
                                    print(f"     - Clase: {pred['clase']}, Confianza: {pred['confianza']}, BBox: {pred['bbox']}")
                                os.remove(ruta_imagen)
                                os.remove(ruta_txt)
                            else:
                                print(f"[✘] Error al enviar {archivo}: {res.status_code} - {res.text}")
                    except Exception as e:
                        print(f"[✘] Fallo al procesar {archivo}: {e}")

if __name__ == "__main__":
    if hay_conexion():
        print("📡 Conexión detectada. Sincronizando...")
        sincronizar()
    else:
        print("❌ Sin conexión. Reintentar más tarde.")
