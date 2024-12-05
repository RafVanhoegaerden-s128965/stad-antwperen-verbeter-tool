from fastapi import APIRouter, HTTPException, Depends
from elasticsearch import Elasticsearch, NotFoundError
from dependencies.elasticsearch import get_es_client
from models.schemas import RawTextBody
import datetime
import hashlib
from dependencies.auth import get_current_user

router = APIRouter()

@router.get("/raw_texts")
def get_all_raw_texts(
    current_user: str = Depends(get_current_user),
    es: Elasticsearch = Depends(get_es_client)
):
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


@router.get("/raw_text/{raw_text_id}")
def get_raw_text_by_id(
    raw_text_id: str,
    current_user: str = Depends(get_current_user),
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        result = es.get(index="raw_texts", id=raw_text_id)
        return {
            "id": result["_id"],
            **result["_source"]
        }
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Raw text not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve raw text: {str(e)}")

@router.post("/raw_text")
def create_raw_text(
    request: RawTextBody,
    current_user: str = Depends(get_current_user),
    es: Elasticsearch = Depends(get_es_client)
):
    text = request.text
    text_type = request.text_type.strip().lower().capitalize()
    hashed_id = hashlib.sha256(text.encode()).hexdigest()

    storage_data = {
        "text": text,
        "text_type": text_type,
        "timestamp": datetime.datetime.now().isoformat()
    }

    try:
        # Check if a document with this text already exists
        search_result = es.search(
            index="raw_texts",
            body={
                "query": {
                    "match": {
                        "text": text
                    }
                }
            }
        )

        # If we found an exact match
        if search_result["hits"]["total"]["value"] > 0:
            existing_doc = search_result["hits"]["hits"][0]
            existing_id = existing_doc["_id"]
            
            # Update the existing document
            es.update(
                index="raw_texts",
                id=existing_id,
                doc=storage_data,
                refresh=True
            )
            
            return {
                "message": "Raw text updated successfully (duplicate found)",
                "id": existing_id,
                "data": storage_data
            }
        else:
            # No duplicate found, create new document
            es.index(index="raw_texts", id=hashed_id, document=storage_data, refresh=True)
            return {
                "message": "Raw text created successfully",
                "id": hashed_id,
                "data": storage_data
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store text: {str(e)}")

@router.put("/raw_text/{raw_text_id}")
def update_raw_text(
    raw_text_id: str, 
    request: RawTextBody,
    current_user: str = Depends(get_current_user),
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