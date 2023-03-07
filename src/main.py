import sys

from fastapi import APIRouter, FastAPI


from factories.document_factory import DocumentFactory
from factories.note_factory import NoteFactory
from db.database import metadata, engine

metadata.create_all(engine)

api = FastAPI()


@api.on_event("startup")
async def startup():
    pass


@api.on_event("shutdown")
async def shutdown():
    pass


dynamic_router = APIRouter()

# dynamic_router.add_api_route("/notes/", NoteFactory.fetch_all, methods=['GET'], response_model=List[Note])
NoteFactory.register_get_routes(dynamic_router)
#NoteFactory.register_post_routes(dynamic_router)

DocumentFactory.register_get_routes(dynamic_router)
DocumentFactory.register_post_routes(dynamic_router)

api.include_router(dynamic_router)
