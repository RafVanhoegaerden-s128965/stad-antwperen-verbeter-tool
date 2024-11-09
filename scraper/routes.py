from fastapi import APIRouter, HTTPException
import requests

router = APIRouter()


def post_data(data: dict):
    url = data.get("url")
    text = data.get("text")

    if not url or not text:
        raise HTTPException(status_code=400, detail="Missing required fields: url and text")

    # The API endpoint for the backend service
    api_url = "http://stad-antwerpen-backend:8000/api/scraper"
    payload = {
        'url': url,
        'text': text
    }

    # Send the data to the backend
    response = requests.post(api_url, json=payload)

    if response.status_code == 200:
        print(f"Successfully forwarded data for {url}")
    else:
        print(f"Failed to forward data for {url}, status code {response.status_code}")
        raise HTTPException(status_code=500, detail="Failed to forward data to destination API")

    return response
