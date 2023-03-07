from typing import Dict

from models import models
from schemas import JSONAPIResource, DocumentIn, JSONAPIResourceLinkage, JSONAPIRelationship, RelationshipInfo

from .resources.abstract_resource_factory import AbstractResourceFactory


class DocumentFactory(AbstractResourceFactory):
    name = "documents"

    model = models.Document
    schema_in = DocumentIn

    relationships = {
        "notes": RelationshipInfo(api_input_ids="notes_ids", model=models.Document, uselist=True)
    }


    @classmethod
    def make_attributes(cls, input_item: type[schema_in]) -> Dict[str, any]:
        return {
            "title": input_item.title
        }

    @classmethod
    def as_resource(cls, obj: model) -> JSONAPIResource:
        return JSONAPIResource(
            id=obj.id,
            type=cls.name,
            attributes={
                "id": obj.id,
                "title": obj.title
            },
            relationships=cls.make_relationship_object(obj)
        )
