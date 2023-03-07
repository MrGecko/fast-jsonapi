from abc import abstractmethod, ABCMeta
from typing import Dict, List, Any, Sequence

from models import models
from db.database import get_db
from fastapi import Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy import select, Row, RowMapping
from sqlalchemy.orm import Session

from schemas import JSONAPIResponseSchema, JSONAPIResource, RelationshipInfo, JSONAPIRelationship, \
    JSONAPIResourceLinkage


class JSONAPIResponse:

    @classmethod
    def make(cls, factory, data=None, errors=None, pagination=None):
        result = {}

        if not data and not errors:
            errors = {"details": "[JSONAPIResponse] data and errors are both None."}

        if data:
            if isinstance(data, Sequence):
                result["data"] = frozenset({factory.as_resource(item) for item in data})
            else:
                result["data"] = factory.as_resource(data)

        if errors:
            result["errors"] = errors

        if pagination:
            result["links"] = pagination

        return JSONAPIResponseSchema(**result)


class AbstractResourceFactory(ABCMeta):
    name: str = None

    model: models.Base = None
    schema_in: BaseModel = None

    relationships: Dict[str, RelationshipInfo] = {

    }

    @classmethod
    @abstractmethod
    def as_resource(cls, obj: models.Base) -> JSONAPIResource:
        pass

    @classmethod
    def make_attributes(cls, input_item: type[schema_in]) -> Dict[str, any]:
        return input_item.dict()

    @classmethod
    def fetch_one_or_none(cls, item_id, session: Session = Depends(get_db)) -> JSONAPIResponseSchema:
        errors = None
        data = None
        try:
            data = session.scalar(select(cls.model).where(cls.model.id == item_id)).one_or_none()
        except Exception as e:
            errors = [f"{str(e)}"]
        finally:
            return JSONAPIResponse.make(cls, data, errors)

    @classmethod
    def fetch_all(cls, session: Session = Depends(get_db)) -> JSONAPIResponseSchema:
        errors = None
        data = None
        try:
            data = session.scalars(select(cls.model)).all()
        except Exception as e:
            errors = [f"{str(e)}"]
        finally:
            return JSONAPIResponse.make(cls, data, errors)

    # @classmethod
    # def fetch_all_ids(cls, session: Session = Depends(get_db)) -> List:
    #    return session.scalars(select(cls.model.id)).all()

    @classmethod
    def create(cls, input_item: type[schema_in], session: Session = Depends(get_db)) -> models.Base:
        # instantiate the new item and fill its attributes
        new_item = cls.model(**cls.make_attributes(input_item))
        session.add(new_item)

        session.flush()
        # fill the relations from the relationships present in the request
        for rel_name, info in cls.relationships.items():
            related_objects = cls.get_related_from_ids(info.model, getattr(input, info.api_input_ids, []), session)
            setattr(new_item, rel_name, related_objects)
        session.commit()
        return new_item


    @classmethod
    def get_related_from_ids(cls, related_model: models.Base, related_ids: List, session: Session) -> Sequence[
        Row | RowMapping | Any]:
        if not related_ids:
            return []
        else:
            return session.scalars(select(related_model).where(related_model.id.in_(related_ids))).all()

    @classmethod
    def make_relationship_object(cls, obj):
        relationships = {}
        for rel_name, info in cls.relationships.items():
            rel_objs = getattr(obj, rel_name)
            if isinstance(rel_objs, Sequence):
                data = [JSONAPIResourceLinkage(type=rel_obj.jsonapi_resource_factory.name, id=rel_obj.id) for rel_obj in rel_objs]
            else:
                data = JSONAPIResourceLinkage(type=rel_objs.jsonapi_resource_factory.name, id=rel_objs.id)
            relationships[rel_name] = JSONAPIRelationship(data=data)
        return relationships
    @classmethod
    def register_get_routes(cls, router: APIRouter):
        # fetch single
        # fetch all
        router.add_api_route(f"/{cls.name}/<item_id: int>", cls.fetch_one_or_none, methods=['GET'],
                             response_model=JSONAPIResponseSchema, response_model_exclude_none=True)
        router.add_api_route(f"/{cls.name}", cls.fetch_all, methods=['GET'], response_model=JSONAPIResponseSchema,
                             response_model_exclude_none=True)
        # fetch related ids
        # fetch related entities
        pass

    @classmethod
    def register_post_routes(cls, router: APIRouter):
        router.add_api_route(f"/{cls.name}", cls.create, methods=['POST'], response_model=None)
