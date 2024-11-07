<<<<<<< backend/app/main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from api.cohere_llm import get_suggestions

app = FastAPI(
    title="Stad Antwerpen API",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Elasticsearch client
es = Elasticsearch(["http://elasticsearch:9200"])

class Item(BaseModel):
    name: str
    description: str = None

def get_es_client():
    return es

@app.get("/api")
def read_root():
    return {"Hello": "World"}

@app.post("/api/get_suggestions")
def process_text_endpoint(text: str, text_type: str):
    result = get_suggestions(text, text_type)
    return {"result": result}

@app.get("/api/items")
def read_items(es: Elasticsearch = Depends(get_es_client)):
    try:
        result = es.search(index="items", body={"query": {"match_all": {}}, "size": 10000})
        items = [{"item_id": hit["_id"], "item": hit["_source"]} for hit in result["hits"]["hits"]]
        return {"items": items, "total": result["hits"]["total"]["value"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve items: {str(e)}")

@app.get("/api/items/{item_id}")
def read_item(item_id: str, es: Elasticsearch = Depends(get_es_client)):
    try:
        doc = es.get(index="items", id=item_id)
        return {"item_id": item_id, "item": doc["_source"]}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")

@app.post("/api/items/{item_id}")
def create_item(item_id: str, item: Item, es: Elasticsearch = Depends(get_es_client)):
    try:
        # Check if the item already exists
        es.get(index="items", id=item_id)
        raise HTTPException(status_code=400, detail="Item already exists")
    except NotFoundError:
        # Item doesn't exist, so we can create it
        result = es.index(index="items", id=item_id, document=item.dict())
        if result["result"] == "created":
            return {"item_id": item_id, "item": item}
        else:
            raise HTTPException(status_code=500, detail="Failed to create item")
