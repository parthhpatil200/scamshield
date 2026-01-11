from fastapi import FastAPI
from pydantic import BaseModel
from .pipeline import analyze_text

app = FastAPI(title="ScamShield API")


class TextInput(BaseModel):
    text: str


@app.post("/analyze")
def analyze(input: TextInput):
    return analyze_text(input.text)
