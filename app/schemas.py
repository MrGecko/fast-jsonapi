from typing import List, Optional
from pydantic import BaseModel


class NoteIn(BaseModel):
    text: str
    completed: bool
    class Config:
        orm_mode = True

class Note(BaseModel):
    id: int
    text: str
    completed: bool
    class Config:
        orm_mode = True


class DocumentIn(BaseModel):
    title: str
    notes_ids : Optional[List[int]]

    class Config:
        orm_mode = True

class Document(BaseModel):
    id: int
    title: str

    notes: List[Note]
    
    class Config:
        orm_mode = True