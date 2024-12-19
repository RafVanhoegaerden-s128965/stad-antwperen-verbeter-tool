from fastapi import APIRouter, HTTPException, Depends
from elasticsearch import Elasticsearch
from dependencies.elasticsearch import get_es_client
from dependencies.auth import get_current_user

router = APIRouter()

@router.get("/scraper/training_data")
def get_training_data(
    current_user: str = Depends(get_current_user),
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        result = es.search(index="scraped_data", body={"query": {"match_all": {}}, "size": 10000})
        items = [{"_id": hit["_id"], "_source": hit["_source"]} for hit in result["hits"]["hits"]]
        return {"items": items, "total": result["hits"]["total"]["value"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scraped data: {str(e)}")

@router.post("/elastic/scraper_data")
async def post_scraper_data(
    data: dict,
    current_user: str = Depends(get_current_user),
    es: Elasticsearch = Depends(get_es_client)
):
    try:
        result = es.index(index="scraped_data", document=data)
        
        if result["result"] == "created":
            return {"message": "Data successfully stored in Elasticsearch", "result": result}
        else:
            raise HTTPException(status_code=500, detail="Failed to store data in Elasticsearch")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to communicate with Elasticsearch: {str(e)}")

@router.delete("/scraper/training_data")
def delete_all_scraped_data(
        current_user: str = Depends(get_current_user),
        es: Elasticsearch = Depends(get_es_client)
):
    try:
        # Perform delete_by_query to remove all documents
        result = es.delete_by_query(index="scraped_data", body={"query": {"match_all": {}}})

        return {
            "message": "All scraped data has been deleted successfully",
            "deleted": result["deleted"],
            "total": result["total"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete scraped data: {str(e)}")

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