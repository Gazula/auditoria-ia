from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from ultralytics import YOLO
import cv2
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Cargar variables de entorno (para la clave del mail)
load_dotenv()

app = FastAPI()

# Cargar modelo YOLO
model = YOLO("best.pt")

# Diccionario de tiendas y sus correos
TIENDAS = {
    "101": "tienda101@gmail.com",
    "102": "tienda102@gmail.com",
    "103": "tienda103@gmail.com"
}

# --- Función para analizar imagen con YOLO ---
def analizar_imagen(ruta_imagen: str):
    results = model(ruta_imagen)
    img = cv2.imread(ruta_imagen)

    hallazgos = []
    for r in results[0].boxes:
        x1, y1, x2, y2 = map(int, r.xyxy[0])
        label = model.names[int(r.cls[0])]
        conf = float(r.conf[0])
        hallazgos.append(f"{label} ({conf:.2f})")

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(img, f"{label} {conf:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    salida = ruta_imagen.replace(".jpg", "_marcada.jpg")
    cv2.imwrite(salida, img)
    return hallazgos, salida

# --- Función para enviar correos ---
def enviar_mail(resultado, destinatario, archivo_imagen, texto_extra, tienda_id):
    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    msg = MIMEMultipart()
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = f"Informe de Auditoría - Tienda {tienda_id}"

    cuerpo = f"""
    Estimado responsable de la tienda {tienda_id},

    Se realizó una auditoría automática y se detectaron los siguientes puntos:

    {resultado}

    Observación ingresada por el auditor:
    {texto_extra}

    Adjuntamos la imagen con los errores resaltados.

    Saludos,
    Sistema de Auditoría
    """
    msg.attach(MIMEText(cuerpo, "plain"))

    with open(archivo_imagen, "rb") as adj:
        mime = MIMEBase("application", "octet-stream")
        mime.set_payload(adj.read())
        encoders.encode_base64(mime)
        mime.add_header("Content-Disposition", f"attachment; filename={os.path.basename(archivo_imagen)}")
        msg.attach(mime)

    with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario, msg.as_string())

# --- Endpoint principal ---
@app.post("/analizar")
async def analizar(
    file: UploadFile = File(...),
    texto: str = Form(...),
    tienda: str = Form(...)
):
    try:
        # Guardar imagen temporal
        ruta = f"temp_{file.filename}"
        with open(ruta, "wb") as f:
            f.write(await file.read())

        # Analizar con YOLO
        hallazgos, imagen_marcada = analizar_imagen(ruta)

        # Buscar correo de tienda
        destinatario = TIENDAS.get(tienda)
        if not destinatario:
            return JSONResponse(status_code=404, content={"error": "Tienda no encontrada"})

        # Preparar informe
        resultado = "\n".join(hallazgos) if hallazgos else "No se detectaron errores."

        # Enviar mail
        enviar_mail(resultado, destinatario, imagen_marcada, texto, tienda)

        # Respuesta a la app
        return {"status": "ok", "mensaje": "Auditoría enviada con éxito", "hallazgos": resultado}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
