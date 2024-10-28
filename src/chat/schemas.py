from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List

from sqlalchemy import String


class LiteratureReferenceData(BaseModel):
    id: UUID
    title: str
    author: str
    year: int

class MessageData(BaseModel):
    id: UUID
    content: str
    references: List[LiteratureReferenceData]  # optional

class ChatData(BaseModel):
    id: UUID | None = None
    name: str
    messages: List[MessageData] | None = None
