from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from ultralytics import YOLO
from PIL import Image
import uvicorn
import io

app = FastAPI()

# ✅ Cargar el modelo entrenado
modelo = YOLO("best.pt")  # Asegurate que esté en la misma carpeta o da la ruta completa

@app.post("/analizar")
async def analizar_imagen(file: UploadFile = File(...), texto: str = Form(...)):
    try:
        # Leer imagen recibida
        imagen_bytes = await file.read()
        imagen = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")

        # Realizar predicción
        resultados = modelo.predict(source=imagen, conf=0.5, save=False)

        predicciones = []
        for r in resultados:
            for box in r.boxes:
                clase = int(box.cls[0])
                conf = float(box.conf[0])
                bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

                predicciones.append({
                    "clase": modelo.names[clase],
                    "confianza": round(conf, 2),
                    "bbox": bbox
                })

        return JSONResponse(content={
            "estado": "ok",
            "observacion": texto,
            "predicciones": predicciones
        })

    except Exception as e:
        return JSONResponse(content={"estado": "error", "detalle": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
