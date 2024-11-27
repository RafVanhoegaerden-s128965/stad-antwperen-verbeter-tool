from fastapi import APIRouter
import requests

router = APIRouter()


def post_data(data: dict):
    url = data.get("url")
    text = data.get("text")

    # The API endpoint for the backend service
    api_url = "http://stad-antwerpen-backend:8000/api/scraper"
    payload = {
        'url': url,
        'text': text
    }

    # Send the data to the backend
    response = requests.post(api_url, json=payload)

    return response
