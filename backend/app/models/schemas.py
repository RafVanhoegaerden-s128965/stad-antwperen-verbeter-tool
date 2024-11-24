from pydantic import BaseModel

class RawTextBody(BaseModel):
    text: str
    text_type: str

class FinalTextBody(BaseModel):
    text: str
    raw_text_id: str
    suggestion_id: str 