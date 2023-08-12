from pydantic import BaseModel
from typing import List

class Translate(BaseModel):
    message:str
    from_language:str
    to_language:str

class Summerize(BaseModel):
    youtube_url:str

class BusinessName(BaseModel):
    keyword:List[str]
    industry:str
class PromptGenerator(BaseModel):
    detail:str
class SqlGenerator(BaseModel):
    detail:str

class Chat(BaseModel):
    message:str