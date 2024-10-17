from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Stad Antwerpen API",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Een eenvoudige database om items op te slaan
items = {}

class Item(BaseModel):
    name: str
    description: str = None

@app.get("/api")
def read_root():
    return {"Hello": "World"}

@app.get("/api/items/{item_id}")
def read_item(item_id: int, q: str = None):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item": items[item_id], "q": q}

@app.post("/api//items/{item_id}")
def create_item(item_id: int, item: Item):
    if item_id in items:
        raise HTTPException(status_code=400, detail="Item already exists")
    items[item_id] = item
    return {"item_id": item_id, "item": item}