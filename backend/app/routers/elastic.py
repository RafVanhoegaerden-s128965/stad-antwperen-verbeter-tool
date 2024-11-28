from fastapi import APIRouter, HTTPException, Depends
from elasticsearch import Elasticsearch
from dependencies.elasticsearch import get_es_client
from dependencies.auth import get_current_user

router = APIRouter()

@router.delete("/elastic/clear/{index_name}")
def clear_elastic_index(
    index_name: str,
    current_user: str = Depends(get_current_user),
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

@router.delete("/elastic/clear_all")
def clear_all_elastic_indices(
    current_user: str = Depends(get_current_user),
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