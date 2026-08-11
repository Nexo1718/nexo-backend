import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai    

# 1. Configuración de tu llave
mi_llave_secreta = os.getenv("API_KEY_NEXO")

# Inicializamos el cliente de Google GenAI
client = genai.Client(api_key=mi_llave_secreta)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DatosTexto(BaseModel):
    mensaje_usuario: str

@app.post("/analizar")
async def chat_terapeuta(datos: DatosTexto):
    try:
        # Llamada directa y sencilla a Gemini
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"Eres un terapeuta empático. Responde brevemente a esto: {datos.mensaje_usuario}"
        )
        return {"asistente_dice": response.text.strip()}
    except Exception as e:
        # Esto imprimirá el error real en tu terminal de Python para que lo veamos
        print(f"\n--- ERROR DETECTADO --- \n{str(e)}\n-----------------------\n")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)