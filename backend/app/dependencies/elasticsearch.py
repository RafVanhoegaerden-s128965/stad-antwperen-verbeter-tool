from elasticsearch import Elasticsearch
import os

ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD', 'elastic')
ELASTIC_URL = os.getenv('ELASTIC_URL', 'http://elasticsearch:9200')

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