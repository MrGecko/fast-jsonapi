from typing import List

from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship, as_declarative, Mapped

from db.database import metadata


@as_declarative(metadata=metadata)
class Base:
    __tablename__: str


class Note(Base):
    __tablename__ = "note"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String(200))
    completed: Mapped[bool] = mapped_column(Boolean)

    document_id: Mapped[int] = mapped_column(ForeignKey("document.id"), nullable=False)
    document: Mapped["Document"] = relationship("Document")

    @property
    def jsonapi_resource_factory(self):
        from factories.note_factory import NoteFactory
        return NoteFactory


class Document(Base):
    __tablename__ = "document"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))

    notes: Mapped[List[Note]] = relationship(primaryjoin="Document.id == Note.document_id", back_populates="document")

    @property
    def jsonapi_resource_factory(self):
        from factories.document_factory import DocumentFactory
        return DocumentFactory

