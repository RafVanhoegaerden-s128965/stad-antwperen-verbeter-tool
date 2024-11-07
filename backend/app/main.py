from fastapi import FastAPI
from api.cohere_llm import get_suggestions

app = FastAPI()

@app.get("/api")
def read_root():
    return {"Hello": "World"}

@app.post("/get_suggestions")
def process_text_endpoint(text: str, text_type: str):
    result = get_suggestions(text, text_type)
    return {"result": result}
