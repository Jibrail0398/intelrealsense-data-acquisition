from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.image_writer import FORMATS
from app.utils.naming import validate_class_name


def _check_formats(value: list[str]) -> list[str]:
    unknown = [f for f in value if f not in FORMATS]
    if unknown:
        raise ValueError(f"Unknown format(s): {', '.join(unknown)}")
    if not value:
        raise ValueError("Choose at least one output format")
    # keep registry order, drop duplicates
    return [key for key in FORMATS if key in value]


def _check_classes(value: list[str]) -> list[str]:
    cleaned = [validate_class_name(v) for v in value]
    lowered = [c.lower() for c in cleaned]
    if len(set(lowered)) != len(lowered):
        raise ValueError("Class names must be unique")
    if not cleaned:
        raise ValueError("Add at least one class")
    return cleaned


class ClassOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    position: int
    count: int = 0


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    destination_dir: str
    formats: list[str]
    classes: list[ClassOut]
    total_captures: int = 0
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    destination_dir: str = Field(min_length=1)
    formats: list[str]
    classes: list[str]

    @field_validator("formats")
    @classmethod
    def _formats(cls, v: list[str]) -> list[str]:
        return _check_formats(v)

    @field_validator("classes")
    @classmethod
    def _classes(cls, v: list[str]) -> list[str]:
        return _check_classes(v)

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Project name cannot be empty")
        return v


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    destination_dir: str | None = Field(None, min_length=1)
    formats: list[str] | None = None

    @field_validator("formats")
    @classmethod
    def _formats(cls, v: list[str] | None) -> list[str] | None:
        return None if v is None else _check_formats(v)


class ClassCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        return validate_class_name(v)


class ClassUpdate(ClassCreate):
    pass


class ClassOrder(BaseModel):
    class_ids: list[int]


class ProjectDeleteResult(BaseModel):
    deleted_captures: int
    deleted_files: int
    deleted_folders: int
    errors: list[str]


class FormatOut(BaseModel):
    key: str
    label: str
    kind: str
    folder: str
    ext: str
    description: str
