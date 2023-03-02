from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

import crud
import models
from schemas import Note, NoteIn, Document, DocumentIn
from database import metadata, engine, SessionLocal

metadata.create_all(engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@app.on_event("startup")
async def startup():
    pass


@app.on_event("shutdown")
async def shutdown():
    pass




class EntityFactory(ABC):

    model = None
    related_ids = {

    }

    @classmethod
    def make_attributes(cls, input: DocumentIn) -> Dict[str, any]:
        return input.dict()

    @classmethod
    def fetch_one_or_none(cls, item_id: any, session: Session = Depends(get_db)):
        return session.scalar(select(cls.model).where(cls.model.id == item_id)).one_or_none()
    
    @classmethod
    def fetch_all(cls, session: Session = Depends(get_db)) -> List[model]:
        return session.scalars(select(cls.model)).all()

    #@classmethod
    #def fetch_all_ids(cls, session: Session = Depends(get_db)) -> List:
    #    return session.scalars(select(cls.model.id)).all()

    @classmethod
    def create(cls, input: BaseModel, session: Session = Depends(get_db)) -> models.Base:
        # instantiate the new item and fill its attributes
        new_item = cls.model(**cls.make_attributes(input))
        session.add(new_item)
        session.flush()
        # fill the relations from the related_ids present in the request
        for ids_attr, related_model in cls.related_ids.items():
            new_item.notes = cls.get_related_from_ids(related_model, getattr(input, ids_attr, []), session)
        session.commit()
        return new_item 
    
    @classmethod
    def get_related_from_ids(cls, related_model: models.Base, related_ids: List, session: Session) -> List:
        if not related_ids:
            return []
        else:
            return session.scalars(select(related_model).where(related_model.id.in_(related_ids))).all()
        
    @classmethod
    def register_get_routes(cls, router: APIRouter):
        ##TODO: respose_model : c'est les schema pas les models
        # fetch single
        #router.add_api_route(f"/{cls.name}/<item_id: int>", cls.fetch_one_or_none, methods=['GET'], response_model=cls.model)
        # fetch all
        #router.add_api_route(f"/{cls.name}", cls.fetch_all, methods=['GET'], response_model=List[cls.model])
        # fetch related ids
        # fetch related entities
        pass


class DocumentFactory(EntityFactory):
    name = "documents"
    model = models.Document
    related_ids = {
        "notes_ids": models.Note
    }

    @classmethod
    def make_attributes(cls, input: DocumentIn) -> Dict[str, any]:
        return {
            "title": input.title
        }

class NoteFactory(EntityFactory):
    name = "notes"
    model = models.Note



dynamic_router = APIRouter()


#dynamic_router.add_api_route("/notes/", NoteFactory.fetch_all, methods=['GET'], response_model=List[Note])
NoteFactory.register_get_routes(dynamic_router)
dynamic_router.add_api_route("/notes/", NoteFactory.create, methods=['POST'], response_model=Note)

dynamic_router.add_api_route("/documents/", DocumentFactory.fetch_all, methods=['GET'], response_model=List[Document])
dynamic_router.add_api_route("/documents/", DocumentFactory.create, methods=['POST'], response_model=Document)


app.include_router(dynamic_router)