from typing import List, Optional, Dict, Sequence, Union

from pydantic import BaseModel

import models.models


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
    notes_ids: Optional[List[int]]

    class Config:
        orm_mode = True


class Document(BaseModel):
    id: int
    title: str

    notes: List[Note]

    class Config:
        orm_mode = True


class JSONAPILinksSection(BaseModel):
    pass


class JSONAPIMetaSection(BaseModel):
    pass


class JSONAPIResourceLinkage(BaseModel):
    id: str
    type: str

    def __hash__(self):
        return hash((self.id, self.type))


class JSONAPIRelationship(BaseModel):
    data: Union[JSONAPIResourceLinkage, frozenset[JSONAPIResourceLinkage], None]
    links: Union[JSONAPILinksSection, None]
    meta: Union[JSONAPIMetaSection, None]

    def dict(self, *args, **kwargs):
        #TODO improve perf if links.self exist
        return self.__dict__

class RelationshipInfo(BaseModel):
    api_input_ids: str
    model: object
    uselist: bool = True

class JSONAPIResource(BaseModel):
    id: str
    type: str
    attributes: Dict[str, object]

    relationships: Union[Dict[str, JSONAPIRelationship], None]
    links: Union[JSONAPILinksSection, None]
    meta: Union[JSONAPIMetaSection, None]

    def __hash__(self):
        return hash((self.id, self.type))


class JSONAPIResponseSchema(BaseModel):
    data: Union[frozenset[JSONAPIResource], JSONAPIResource, None]
    errors: Union[frozenset[object], None]

    class Config:
        orm_mode = True

    def dict(self, *args, **kwargs):
        #TODO improve perf if links.self exist
        return self.__dict__
