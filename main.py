import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

# 1. Leemos la llave y le quitamos espacios o comillas invisibles al pegar
raw_key = os.getenv("API_KEY_NEXO", "")
mi_llave_secreta = raw_key.strip().strip('"').strip("'")

# Verificación inicial en consola
if not mi_llave_secreta:
    print("⚠️ ALERTA: No se encontró la variable API_KEY_NEXO en el entorno.")
else:
    print("✅ API Key cargada correctamente.")

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

# --- MODELOS DE DATOS ---
class DatosEjercicio(BaseModel):
    nivel_ansiedad: int
    contexto: str
    paso: int

class DatosTexto(BaseModel):
    mensaje_usuario: str


# --- PUERTA 1: EJERCICIOS ADAPTATIVOS ---
@app.post("/analizar")
async def analizar_ansiedad(datos: DatosEjercicio):
    try:
        prompt = (
            f"El usuario está en {datos.contexto}, nivel de ansiedad {datos.nivel_ansiedad}/10, "
            f"paso {datos.paso}. Dale una instrucción o ejercicio muy breve, empático y calmante en 1 o 2 oraciones."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        es_ultimo = datos.paso >= 3 
        
        return {
            "asistente_dice": response.text.strip(),
            "explicacion": "Respira profundo y sigue las instrucciones.",
            "es_ultimo": es_ultimo
        }
    except Exception as e:
        print(f"\n--- ERROR DETECTADO EN /analizar --- \n{str(e)}\n-----------------------\n")
        raise HTTPException(status_code=500, detail=str(e))


# --- PUERTA 2: CHATBOT IA ---
@app.post("/chat_ia")
async def chat_terapeuta(datos: DatosTexto):
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Eres un terapeuta empático, cálido y breve: {datos.mensaje_usuario}"
        )
        return {"asistente_dice": response.text.strip()}
    except Exception as e:
        print(f"--- ERROR CHAT: {e} ---")
        raise HTTPException(status_code=500, detail=str(e))


# --- PUERTA 3: DIARIO DE DESAHOGO ---
@app.post("/desahogo")
async def diario_desahogo(datos: DatosTexto):
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"El usuario se está desahogando. Dile algo breve y validador: {datos.mensaje_usuario}"
        )
        return {"asistente_dice": response.text.strip()}
    except Exception as e:
        print(f"--- ERROR DESAHOGO: {e} ---")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    puerto = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=puerto)