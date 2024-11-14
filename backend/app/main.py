import logging
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.params import Query
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from api.cohere_llm import CohereLLM
from api.openai_llm import OpenAILLM

import re
import json

app = FastAPI(
    title="Stad Antwerpen API",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Elasticsearch client
es = Elasticsearch(["http://elasticsearch:9200"])

# LLM setup, API keys loaded from environment variables
COHERE_API_KEY = None
OPENAI_API_KEY = None
cohere_model = CohereLLM(api_key=COHERE_API_KEY)
openai_model = OpenAILLM(api_key=OPENAI_API_KEY)

class Item(BaseModel):
    name: str
    description: str = None

def get_es_client():
    return es

@app.get("/api")
def read_root():
    return {"Hello": "World"}

class GetSuggestionsBody(BaseModel):
    text: str
    text_type: str

@app.post("/api/get_suggestions")
def process_text_endpoint(request: GetSuggestionsBody, 
    model: str = "cohere",
    temperature: float = Query(0.65, ge=0, le=1),
    frequency_penalty: float = Query(0.0, ge=0, le=1),
    presence_penalty: float = Query(0.0, ge=0, le=1)):
    text = request.text
    text_type = request.text_type
    text_type = text_type.strip().lower().capitalize()
    if model.lower() == "cohere":
        result = cohere_model.get_suggestions(
            text,
            text_type,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
            )
    elif model.lower() == "openai":
        result = openai_model.get_suggestions(
            text,
            text_type,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
            )
    else:
        return {"error": "Invalid model specified"}
    result_dict = result if isinstance(result, dict) else json.loads(result)
    
    # Add startPos and endPos to each correction based on `incorrect_part` in `text`
    for correction in result_dict.get("corrections", []):
        incorrect_part = correction.get("incorrect_part", "")
        
        # Find the start and end position of `incorrect_part` in the `text`
        match = re.search(re.escape(incorrect_part), text)
        
        if match:
            start_pos = match.start()
            end_pos = match.end()
        else:
            start_pos = 0
            end_pos = 0

        # Add info to the correction
        correction["info"] = {
            "startPos": start_pos,
            "endPos": end_pos
        }

    # Convert result_dict back to JSON string
    response_content = json.dumps(result_dict)
    
    # Return response as JSON
    return Response(content=response_content, media_type="application/json")

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
