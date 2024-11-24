from fastapi import FastAPI, HTTPException, Depends, Request, status, Body
from fastapi.exceptions import RequestValidationError
from fastapi.params import Query
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch, NotFoundError
from pydantic import BaseModel
import hashlib
import datetime
import json
import logging
import re
import os
from typing import Optional, List

from api.cohere_llm import CohereLLM
# from api.openai_llm import OpenAILLM

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Stad Antwerpen API",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Elasticsearch configuration
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD', 'elastic')
ELASTIC_URL = os.getenv('ELASTIC_URL', 'http://elasticsearch:9200')

# LLM configuration
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
cohere_model = CohereLLM(api_key=COHERE_API_KEY)
# openai_model = OpenAILLM(api_key=OPENAI_API_KEY)

# Pydantic models
class RawTextBody(BaseModel):
    text: str
    text_type: str

class FinalTextBody(BaseModel):
    text: str
    raw_text_id: str
    suggestion_id: str

# Elasticsearch client dependency
def get_es_client():
    es = Elasticsearch(
        ELASTIC_URL,
        basic_auth=("elastic", ELASTIC_PASSWORD),
        verify_certs=False
    )
    try:
        yield es
    finally:
        es.close()

# Error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

# Endpoints
@app.post("/api/raw_text")
def CreateRawText(
    request: RawTextBody,
    es: Elasticsearch = Depends(get_es_client)
):
    text = request.text
    text_type = request.text_type.strip().lower().capitalize()

    # Create hash of text
    hashed_id = hashlib.sha256(text.encode()).hexdigest()

    # Store raw_text in Database
    storage_data = {
        "text": text,
        "text_type": text_type,
        "timestamp": datetime.datetime.now().isoformat()
    }

    try:
        es.index(index="raw_texts", id=hashed_id, document=storage_data, refresh=True)
        return {"message": "Raw text created successfully", "id": hashed_id, "data": storage_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store text: {str(e)}")

@app.post("/api/suggestions/{raw_text_id}")
def CreateSuggestions(
    raw_text_id: str,
    model: str = "cohere",
    temperature: float = Query(0.65, ge=0, le=1),
    frequency_penalty: float = Query(0.0, ge=0, le=1),
    presence_penalty: float = Query(0.0, ge=0, le=1),
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        # Get the raw text
        raw_text_doc = es.get(index="raw_texts", id=raw_text_id, refresh=True)
        text = raw_text_doc["_source"]["text"]
        text_type = raw_text_doc["_source"]["text_type"]

        # Generate suggestions
        if model.lower() == "cohere":
            result = cohere_model.get_suggestions(
                text,
                text_type,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
        # elif model.lower() == "openai":
        #     result = openai_model.get_suggestions(
        #         text,
        #         text_type,
        #         temperature=temperature,
        #         frequency_penalty=frequency_penalty,
        #         presence_penalty=presence_penalty
        #     )
        else:
            raise HTTPException(status_code=400, detail="Invalid model specified")

        result_dict = result if isinstance(result, dict) else json.loads(result)
        
        # Add position information
        for correction in result_dict.get("corrections", []):
            incorrect_part = correction.get("incorrect_part", "")
            match = re.search(re.escape(incorrect_part), text)
            correction["info"] = {
                "startPos": match.start() if match else 0,
                "endPos": match.end() if match else 0
            }

        # Store suggestions
        suggestions_data = {
            "raw_text_id": raw_text_id,
            "text": text,
            "suggestions": result_dict,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        result = es.index(index="suggestions", document=suggestions_data, refresh=True)
        
        return {
            "message": "Suggestions created successfully",
            "id": result["_id"],
            "data": suggestions_data
        }

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Raw text not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process suggestions: {str(e)}")
    
@app.post("/api/final_text")
def CreateFinalText(
    request: FinalTextBody,
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        # Verify that raw_text exists
        if not es.exists(index="raw_texts", id=request.raw_text_id):
            raise HTTPException(status_code=404, detail="Raw text not found")
            
        # Verify that suggestion exists
        if not es.exists(index="suggestions", id=request.suggestion_id):
            raise HTTPException(status_code=404, detail="Suggestion not found")

        # Store final_text in Database
        final_text_data = {
            "text": request.text,
            "raw_text_id": request.raw_text_id,
            "suggestion_id": request.suggestion_id,
            "timestamp": datetime.datetime.now().isoformat()
        }

        result = es.index(
            index="final_texts",
            document=final_text_data,
            refresh=True
        )

        return {
            "message": "Final text created successfully",
            "id": result["_id"],
            "data": final_text_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store final text: {str(e)}")

@app.put("/api/raw_text/{raw_text_id}")
def UpdateRawText(
    raw_text_id: str, 
    request: RawTextBody,
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        if not es.exists(index="raw_texts", id=raw_text_id):
            raise HTTPException(status_code=404, detail="Raw text not found")

        update_data = {
            "text": request.text,
            "text_type": request.text_type.strip().lower().capitalize(),
            "timestamp": datetime.datetime.now().isoformat()
        }

        es.update(
            index="raw_texts",
            id=raw_text_id,
            doc=update_data,
            refresh=True
        )

        updated_doc = es.get(index="raw_texts", id=raw_text_id, refresh=True)
        
        return {
            "message": "Raw text updated successfully",
            "id": raw_text_id,
            "data": updated_doc["_source"]
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update raw text: {str(e)}")

@app.put("/api/suggestions/{suggestion_id}")
def UpdateSuggestion(
    suggestion_id: str,
    model: str = "cohere",
    temperature: float = Query(0.65, ge=0, le=1),
    frequency_penalty: float = Query(0.0, ge=0, le=1),
    presence_penalty: float = Query(0.0, ge=0, le=1),
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        # Get existing suggestion to get raw_text_id
        existing_suggestion = es.get(index="suggestions", id=suggestion_id, refresh=True)
        raw_text_id = existing_suggestion["_source"]["raw_text_id"]

        # Get latest raw_text
        raw_text_doc = es.get(index="raw_texts", id=raw_text_id, refresh=True)
        text = raw_text_doc["_source"]["text"]
        text_type = raw_text_doc["_source"]["text_type"]

        # Generate new suggestions
        if model.lower() == "cohere":
            result = cohere_model.get_suggestions(
                text,
                text_type,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
        # elif model.lower() == "openai":
        #     result = openai_model.get_suggestions(
        #         text,
        #         text_type,
        #         temperature=temperature,
        #         frequency_penalty=frequency_penalty,
        #         presence_penalty=presence_penalty
        #     )
        else:
            raise HTTPException(status_code=400, detail="Invalid model specified")

        result_dict = result if isinstance(result, dict) else json.loads(result)
        
        # Add position information
        for correction in result_dict.get("corrections", []):
            incorrect_part = correction.get("incorrect_part", "")
            match = re.search(re.escape(incorrect_part), text)
            correction["info"] = {
                "startPos": match.start() if match else 0,
                "endPos": match.end() if match else 0
            }

        # Update suggestion
        update_data = {
            "raw_text_id": raw_text_id,
            "text": text,
            "suggestions": result_dict,
            "timestamp": datetime.datetime.now().isoformat()
        }

        es.update(
            index="suggestions",
            id=suggestion_id,
            doc=update_data,
            refresh=True
        )
        
        # Return the same format as create suggestions
        return {
            "message": "Suggestions updated successfully",
            "suggestion_id": suggestion_id,
            "data": update_data
        }

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="Suggestion or raw text not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update suggestion: {str(e)}")

@app.get("/api/raw_texts")
def GetAllRawTexts(es: Elasticsearch = Depends(get_es_client)):
    try:
        result = es.search(
            index="raw_texts",
            body={
                "query": {"match_all": {}},
                "sort": [{"timestamp": "desc"}],
                "size": 10000
            }
        )
        
        texts = [{
            "id": hit["_id"],
            **hit["_source"]
        } for hit in result["hits"]["hits"]]
        
        return {"texts": texts, "total": result["hits"]["total"]["value"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve texts: {str(e)}")

@app.get("/api/suggestions")
def GetAllSuggestions(es: Elasticsearch = Depends(get_es_client)):
    try:
        result = es.search(
            index="suggestions",
            body={
                "query": {"match_all": {}},
                "sort": [{"timestamp": "desc"}],
                "size": 10000
            }
        )
        
        suggestions = [{
            "id": hit["_id"],
            **hit["_source"]
        } for hit in result["hits"]["hits"]]
        
        return {"suggestions": suggestions, "total": result["hits"]["total"]["value"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve suggestions: {str(e)}")
    
@app.get("/api/final_texts")
def GetAllFinalTexts(es: Elasticsearch = Depends(get_es_client)):
    try:
        result = es.search(
            index="final_texts",
            body={
                "query": {"match_all": {}},
                "sort": [{"timestamp": "desc"}],
                "size": 10000
            }
        )
        
        final_texts = [{
            "id": hit["_id"],
            **hit["_source"]
        } for hit in result["hits"]["hits"]]
        
        return {
            "final_texts": final_texts,
            "total": result["hits"]["total"]["value"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve final texts: {str(e)}")

@app.delete("/api/elastic/clear/{index_name}")
def ClearElasticIndex(
    index_name: str,
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        if index_name not in ["raw_texts", "suggestions", "final_texts"]:
            raise HTTPException(status_code=400, detail="Invalid index name")
            
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            
        mapping = {
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "text": {"type": "text"},
                    "text_type": {"type": "keyword"},
                    "suggestions": {"type": "object"},
                    "raw_text_id": {"type": "keyword"},
                    "suggestion_id": {"type": "keyword"}
                }
            }
        }
            
        es.indices.create(index=index_name, body=mapping)
        
        return {"message": f"Index {index_name} has been cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear index: {str(e)}")

@app.delete("/api/elastic/clear_all")
def ClearAllElasticIndices(
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        indices = ["raw_texts", "suggestions", "final_texts"]
        
        for index in indices:
            if es.indices.exists(index=index):
                es.indices.delete(index=index)
                
                mapping = {
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "date"},
                            "text": {"type": "text"},
                            "text_type": {"type": "keyword"},
                            "suggestions": {"type": "object"},
                            "raw_text_id": {"type": "keyword"},
                            "suggestion_id": {"type": "keyword"}
                        }
                    }
                }
                
                es.indices.create(index=index, body=mapping)
                
        return {"message": "All indices have been cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear indices: {str(e)}")
    
@app.get("/api/scraper/training_data")
def GetTrainingData(es: Elasticsearch = Depends(get_es_client)):
    try:
        # Query om alle documenten op te halen
        result = es.search(index="scraped_data", body={"query": {"match_all": {}}, "size": 10000})
        items = [{"_id": hit["_id"], "_source": hit["_source"]} for hit in result["hits"]["hits"]]
        return {"items": items, "total": result["hits"]["total"]["value"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scraped data: {str(e)}")

    
@app.post("/api/elastic/scraper_data")
async def PostScraperData(data: dict, es: Elasticsearch = Depends(get_es_client)):
    try:
        # Voeg alle JSON-data toe aan Elasticsearch in de "scraped_data" index
        result = es.index(index="scraped_data", document=data)
        
        # Controleer of het document succesvol is opgeslagen
        if result["result"] == "created":
            return {"message": "Data successfully stored in Elasticsearch", "result": result}
        else:
            raise HTTPException(status_code=500, detail="Failed to store data in Elasticsearch")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to communicate with Elasticsearch: {str(e)}")

# # Endpoint: Health check
# @app.get("/health")
# def health_check():
#     return {"status": "ok"}

# # Endpoint: Start scraping task
# @app.post("/scrape/")
# def start_scraping(url: str):
#     try:
#         task_id = str(uuid.uuid4())  # Generate a unique task ID
#         result = scraper_module.scrape(url)
#         # Store result in Elasticsearch
#         es.index(index="scraping_results", id=task_id, body=result)
#         return {"task_id": task_id, "status": "Scraping completed", "result": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
