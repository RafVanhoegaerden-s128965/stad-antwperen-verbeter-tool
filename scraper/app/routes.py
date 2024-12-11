import os
from jose import jwt
import time
import requests

USERNAME = os.getenv("AUTH_USERNAME")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


def generate_jwt_token(username: str):
    payload = {
        "sub": username,
        "iat": int(time.time()),
        "exp": int(time.time()) + int(60 * ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def post_data(data: dict):
    token = generate_jwt_token(USERNAME)
    api_url = "http://stad-antwerpen-backend:8000/api/elastic/scraper_data"

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(api_url, json=data, headers=headers)

    return response
