from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
from pydantic import BaseModel
from typing import List
import uuid
import scraper.scraper as scraper_module

app = FastAPI()

# ElasticSearch client
es = Elasticsearch("http://localhost:9200")

# Data model for adding data to ElasticSearch
class Document(BaseModel):
    title: str
    content: str

# Endpoint: Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Endpoint: Start scraping task
@app.post("/scrape/")
def start_scraping(url: str):
    try:
        task_id = str(uuid.uuid4())  # Generate a unique task ID
        result = scraper_module.scrape(url)
        # Store result in Elasticsearch
        es.index(index="scraping_results", id=task_id, body=result)
        return {"task_id": task_id, "status": "Scraping completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint: Add new document to ElasticSearch
@app.post("/data/")
def add_document(doc: Document):
    try:
        doc_id = str(uuid.uuid4())  # Generate a unique ID
        es.index(index="documents", id=doc_id, body=doc.dict())
        return {"message": "Document added", "doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint: Get document from ElasticSearch by ID
@app.get("/data/{doc_id}")
def get_document(doc_id: str):
    try:
        response = es.get(index="documents", id=doc_id)
        return response["_source"]
    except Exception as e:
        raise HTTPException(status_code=404, detail="Document not found")

# Endpoint: Update document in ElasticSearch by ID
@app.put("/data/{doc_id}")
def update_document(doc_id: str, doc: Document):
    try:
        es.update(index="documents", id=doc_id, body={"doc": doc.dict()})
        return {"message": "Document updated"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Document not found")

# Endpoint: Delete document from ElasticSearch by ID
@app.delete("/data/{doc_id}")
def delete_document(doc_id: str):
    try:
        es.delete(index="documents", id=doc_id)
        return {"message": "Document deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Document not found")
