from typing import List
from sqlalchemy import CHAR, Column, String, Integer, ForeignKey, Float, func, DateTime, Boolean

from sqlalchemy.orm import relationship, as_declarative, Mapped
from sqlalchemy.orm import mapped_column

from database import metadata


@as_declarative(metadata=metadata)
class Base:
    __tablename__: str


class Note(Base):
    __tablename__ = "note"
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text : Mapped[str] = mapped_column(String(200))
    completed : Mapped[bool] = mapped_column(Boolean)



class Document(Base):
    __tablename__ = "document"
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title : Mapped[str] = mapped_column(String(200))

    notes: Mapped[List[Note]] = relationship(secondary="document_has_note")


class DocumentHasNote(Base):
    __tablename__ = "document_has_note"

    doc_id = mapped_column(ForeignKey("document.id"), primary_key=True)
    note_id = mapped_column(ForeignKey("note.id"), primary_key=True)

    

