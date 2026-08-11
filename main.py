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

# --- MODELOS DE DATOS (Lo que Python espera recibir) ---

# Para los Ejercicios (espera números y texto)
class DatosEjercicio(BaseModel):
    nivel_ansiedad: int
    contexto: str
    paso: int

# Para el Chatbot y el Diario (solo espera el mensaje)
class DatosTexto(BaseModel):
    mensaje_usuario: str


# --- PUERTA 1: EJERCICIOS ADAPTATIVOS (/analizar) ---
@app.post("/analizar")
async def analizar_ansiedad(datos: DatosEjercicio):
    try:
        prompt = f"El usuario está en {datos.contexto}, tiene un nivel de ansiedad de {datos.nivel_ansiedad} sobre 10, y va en el paso {datos.paso} del ejercicio. Dale una instrucción de respiración o grounding breve, empática y calmante en 1 o 2 oraciones."
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        
        # El ejercicio terminará en el paso 3
        es_ultimo = datos.paso >= 3 
        
        return {
            "asistente_dice": response.text.strip(),
            "explicacion": "Sigue las instrucciones de la voz y respira profundamente.",
            "es_ultimo": es_ultimo
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- PUERTA 2: CHATBOT IA (/chat_ia) ---
@app.post("/chat_ia")
async def chat_terapeuta(datos: DatosTexto):
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"Eres un terapeuta empático, cálido y breve. Responde a este mensaje del usuario para hacerle sentir mejor: {datos.mensaje_usuario}"
        )
        return {"asistente_dice": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- PUERTA 3: DIARIO DE DESAHOGO (/desahogo) ---
@app.post("/desahogo")
async def diario_desahogo(datos: DatosTexto):
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"El usuario se está desahogando. Dile algo validador, muy breve y que lo anime a seguir exagerando y sacando todo: {datos.mensaje_usuario}"
        )
        return {"asistente_dice": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    # Ajuste final para que funcione perfecto en local y en Render
    puerto = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=puerto)