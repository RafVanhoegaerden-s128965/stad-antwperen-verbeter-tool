from fastapi import APIRouter, HTTPException, Depends
from fastapi.params import Query
from elasticsearch import Elasticsearch, NotFoundError
from dependencies.elasticsearch import get_es_client
from dependencies.auth import get_current_user
import datetime
import json
import re
from api.cohere_llm import CohereLLM
from api.openai_llm import OpenAILLM
import os

router = APIRouter()

# LLM configuration
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
cohere_model = CohereLLM(api_key=COHERE_API_KEY)
openai_model = OpenAILLM(api_key=OPENAI_API_KEY)
DEFAULT_MODEL = "cohere"

@router.get("/suggestions")
def get_all_suggestions(
    current_user: str = Depends(get_current_user),
    es: Elasticsearch = Depends(get_es_client)
):
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

@router.get("/suggestion/{suggestion_id}")
def get_suggestion_by_id(
    suggestion_id: str,
    current_user: str = Depends(get_current_user),
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        result = es.get(index="suggestions", id=suggestion_id)
        return {
            "id": result["_id"],
            **result["_source"]
        }
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve suggestion: {str(e)}")

@router.get("/suggestions/by-raw-text/{raw_text_id}")
def get_suggestions_by_raw_text_id(
    raw_text_id: str,
    current_user: str = Depends(get_current_user),
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        result = es.search(
            index="suggestions",
            body={
                "query": {
                    "term": {
                        "raw_text_id": raw_text_id
                    }
                },
                "sort": [{"timestamp": "desc"}]
            }
        )
        
        suggestions = [{
            "id": hit["_id"],
            **hit["_source"]
        } for hit in result["hits"]["hits"]]
        
        return {
            "suggestions": suggestions,
            "total": result["hits"]["total"]["value"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve suggestions: {str(e)}")

@router.post("/suggestions/{raw_text_id}")
def create_suggestions(
    raw_text_id: str,
    current_user: str = Depends(get_current_user),
    model: str = DEFAULT_MODEL,
    temperature: float = Query(0.65, ge=0, le=1),
    frequency_penalty: float = Query(0.0, ge=0, le=1),
    presence_penalty: float = Query(0.0, ge=0, le=1),
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        raw_text_doc = es.get(index="raw_texts", id=raw_text_id, refresh=True)
        text = raw_text_doc["_source"]["text"]
        text_type = raw_text_doc["_source"]["text_type"]

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
            raise HTTPException(status_code=400, detail="Invalid model specified")

        result_dict = result if isinstance(result, dict) else json.loads(result)
        
        for correction in result_dict.get("corrections", []):
            incorrect_part = correction.get("incorrect_part", "")
            match = re.search(re.escape(incorrect_part), text)
            correction["info"] = {
                "startPos": match.start() if match else 0,
                "endPos": match.end() if match else 0
            }

        suggestions_data = {
            "raw_text_id": raw_text_id,
            "text": text,
            "suggestions": result_dict,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Always create new suggestions
        result = es.index(
            index="suggestions",
            document=suggestions_data,
            refresh=True
        )
        
        return {
            "message": "Suggestions created successfully",
            "id": result["_id"],
            "data": suggestions_data
        }

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Raw text not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process suggestions: {str(e)}")

@router.put("/suggestions/{suggestion_id}")
def update_suggestion(
    suggestion_id: str,
    current_user: str = Depends(get_current_user),
    model: str = DEFAULT_MODEL,
    temperature: float = Query(0.65, ge=0, le=1),
    frequency_penalty: float = Query(0.0, ge=0, le=1),
    presence_penalty: float = Query(0.0, ge=0, le=1),
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        existing_suggestion = es.get(index="suggestions", id=suggestion_id, refresh=True)
        raw_text_id = existing_suggestion["_source"]["raw_text_id"]

        raw_text_doc = es.get(index="raw_texts", id=raw_text_id, refresh=True)
        text = raw_text_doc["_source"]["text"]
        text_type = raw_text_doc["_source"]["text_type"]

        if model.lower() == "cohere":
            result = cohere_model.get_suggestions(
                text,
                text_type,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid model specified")

        result_dict = result if isinstance(result, dict) else json.loads(result)
        
        for correction in result_dict.get("corrections", []):
            incorrect_part = correction.get("incorrect_part", "")
            match = re.search(re.escape(incorrect_part), text)
            correction["info"] = {
                "startPos": match.start() if match else 0,
                "endPos": match.end() if match else 0
            }

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
        
        return {
            "message": "Suggestions updated successfully",
            "suggestion_id": suggestion_id,
            "data": update_data
        }

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Suggestion or raw text not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update suggestion: {str(e)}")