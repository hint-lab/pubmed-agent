from pydantic import BaseModel
from typing import List, Dict, Optional

class MeshTerm(BaseModel):
    descriptor_name: str
    major_topic: bool = False
    qualifier_name: Optional[str] = None
    qualifier_ui: Optional[str] = None

class Article(BaseModel):
    title: str
    first_author: str = ""
    last_author: str = ""
    authors: List[str] = []
    abstract: str = ""
    mesh_terms: Dict[str, MeshTerm] = {}
    keywords: List[str] = []
    year: str = ""
    journal: str = ""
    pmid: str = ""

class SearchQuery(BaseModel):
    query: Optional[str] = None
    journal: Optional[str] = None
    author: Optional[str] = None
    year: Optional[str] = None
    keyword: Optional[str] = None
    topk: int = 10