from fastapi import APIRouter, HTTPException, Depends
from elasticsearch import Elasticsearch
from dependencies.elasticsearch import get_es_client
from models.schemas import FinalTextBody
import datetime

router = APIRouter()

@router.get("/final_texts")
def get_all_final_texts(es: Elasticsearch = Depends(get_es_client)):
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

@router.get("/final_text/{final_text_id}")
def get_final_text_by_id(
    final_text_id: str,
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        result = es.get(index="final_texts", id=final_text_id)
        return {
            "id": result["_id"],
            **result["_source"]
        }
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Final text not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve final text: {str(e)}")

@router.get("/final_texts/by-raw-text/{raw_text_id}")
def get_final_texts_by_raw_text_id(
    raw_text_id: str,
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        result = es.search(
            index="final_texts",
            body={
                "query": {
                    "term": {
                        "raw_text_id": raw_text_id
                    }
                },
                "sort": [{"timestamp": "desc"}]
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

@router.get("/final_texts/by-suggestion/{suggestion_id}")
def get_final_texts_by_suggestion_id(
    suggestion_id: str,
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        result = es.search(
            index="final_texts",
            body={
                "query": {
                    "term": {
                        "suggestion_id": suggestion_id
                    }
                },
                "sort": [{"timestamp": "desc"}]
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

@router.post("/final_text")
def create_final_text(
    request: FinalTextBody,
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        if not es.exists(index="raw_texts", id=request.raw_text_id):
            raise HTTPException(status_code=404, detail="Raw text not found")
            
        if not es.exists(index="suggestions", id=request.suggestion_id):
            raise HTTPException(status_code=404, detail="Suggestion not found")

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