from pydantic import BaseModel


class PickedDirectory(BaseModel):
    path: str | None
    method: str


class DirectoryEntry(BaseModel):
    name: str
    path: str


class DirectoryListing(BaseModel):
    path: str
    parent: str | None
    entries: list[DirectoryEntry]
    shortcuts: list[DirectoryEntry]


class CreateDirectory(BaseModel):
    parent: str
    name: str
