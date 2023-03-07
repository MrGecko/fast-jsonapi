from models import models
from schemas import NoteIn, JSONAPIResource, JSONAPIResourceLinkage, JSONAPIRelationship, RelationshipInfo

from .resources.abstract_resource_factory import AbstractResourceFactory


class NoteFactory(AbstractResourceFactory):
    name = "notes"
    model = models.Note
    schema_in = NoteIn

    relationships = {
        "document": RelationshipInfo(api_input_ids="document_id", model=models.Document, uselist=False)
    }

    @classmethod
    def as_resource(cls, obj: model) -> JSONAPIResource:

        return JSONAPIResource(id=obj.id,
                               type=cls.name,
                               attributes={
                                   "text": obj.text,
                                   "completed": obj.completed
                               },
                               relationships=cls.make_relationship_object(obj))
