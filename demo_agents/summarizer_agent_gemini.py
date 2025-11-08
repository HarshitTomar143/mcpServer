# summarizer_agent_gemini.py
import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="SummarizerAgent-Gemini")
AGENT_NAME = "summarizer-gemini"

# Initialize Gemini client.
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required")

# Choose a model — using a model that's known to be available
MODEL_NAME = "gemini-flash-latest" 

class CallIn(BaseModel):
    input: dict
    meta: dict = {}

class CallOut(BaseModel):
    status: str
    result: dict
    meta: dict = {}

@app.get("/health")
def health():
    return {"status": "ok", "agent": AGENT_NAME, "ts": time.time()}

@app.post("/call")
def call(payload: CallIn):
    text = payload.input.get("text", "")
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="text is required in input.text")

    
    prompt = (
        "Summarize the following text into a short, 2-4 bullet point summary. "
        "Keep it factual and concise.\n\n"
        f"TEXT:\n{text}"
    )

    try:
        # Create the model
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Extract the text from the response
        summary_text = response.text if response and hasattr(response, 'text') else "Failed to generate summary"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini request failed: {str(e)}")

    return CallOut(status="ok", result={"summary": summary_text.strip()}, meta={"agent": AGENT_NAME})