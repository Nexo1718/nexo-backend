import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

# 1. Leemos la llave (ya sea nueva con AQ.Ab o viejita con AIza)
mi_llave_secreta = os.getenv("API_KEY_NEXO")

# Inicializamos cliente
client = genai.Client(api_key=mi_llave_secreta)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DatosEjercicio(BaseModel):
    nivel_ansiedad: int
    contexto: str
    paso: int

class DatosTexto(BaseModel):
    mensaje_usuario: str

@app.post("/analizar")
async def analizar_ansiedad(datos: DatosEjercicio):
    try:
        prompt = f"El usuario está en {datos.contexto}, nivel de ansiedad {datos.nivel_ansiedad}/10, paso {datos.paso}. Dale un consejo o ejercicio muy breve y empático de 1 o 2 oraciones."
        
        # Probamos con el modelo estable
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        
        es_ultimo = datos.paso >= 3 
        
        return {
            "asistente_dice": response.text.strip(),
            "explicacion": "Respira profundo y sigue las instrucciones.",
            "es_ultimo": es_ultimo
        }
    except Exception as e:
        # Imprime el detalle en los logs de Render para ver qué dijo Google
        print(f"--- ERROR GEMINI: {e} ---")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat_ia")
async def chat_terapeuta(datos: DatosTexto):
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=f"Eres un terapeuta empático y breve: {datos.mensaje_usuario}"
        )
        return {"asistente_dice": response.text.strip()}
    except Exception as e:
        print(f"--- ERROR CHAT: {e} ---")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/desahogo")
async def diario_desahogo(datos: DatosTexto):
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=f"El usuario se desahoga. Dile algo breve y validador: {datos.mensaje_usuario}"
        )
        return {"asistente_dice": response.text.strip()}
    except Exception as e:
        print(f"--- ERROR DESAHOGO: {e} ---")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    puerto = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=puerto)