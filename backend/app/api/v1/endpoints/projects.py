from fastapi import APIRouter, status

from app.api.deps import Projects
from app.schemas.project import (
    ClassCreate,
    ClassOrder,
    ClassUpdate,
    FormatOut,
    ProjectCreate,
    ProjectDeleteResult,
    ProjectOut,
    ProjectUpdate,
)
from app.services.image_writer import FORMATS

router = APIRouter(tags=["projects"])


@router.get("/formats", response_model=list[FormatOut])
def list_formats() -> list[FormatOut]:
    return [
        FormatOut(key=f.key, label=f.label, kind=f.kind, folder=f.folder, ext=f.ext, description=f.description)
        for f in FORMATS.values()
    ]


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(service: Projects) -> list[ProjectOut]:
    return service.list_all()


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, service: Projects) -> ProjectOut:
    return service.create(data)


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, service: Projects) -> ProjectOut:
    return service.get(project_id)


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, data: ProjectUpdate, service: Projects) -> ProjectOut:
    return service.update(project_id, data)


@router.delete("/projects/{project_id}", response_model=ProjectDeleteResult)
def delete_project(project_id: int, service: Projects, delete_files: bool = False) -> ProjectDeleteResult:
    """Delete the project and its history; with ``delete_files`` also its image folders on disk."""
    return service.delete(project_id, delete_files)


@router.post("/projects/{project_id}/classes", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def add_class(project_id: int, data: ClassCreate, service: Projects) -> ProjectOut:
    return service.add_class(project_id, data.name)


@router.patch("/projects/{project_id}/classes/{class_id}", response_model=ProjectOut)
def rename_class(project_id: int, class_id: int, data: ClassUpdate, service: Projects) -> ProjectOut:
    return service.rename_class(project_id, class_id, data.name)


@router.delete("/projects/{project_id}/classes/{class_id}", response_model=ProjectOut)
def delete_class(project_id: int, class_id: int, service: Projects) -> ProjectOut:
    return service.delete_class(project_id, class_id)


@router.put("/projects/{project_id}/classes/order", response_model=ProjectOut)
def reorder_classes(project_id: int, data: ClassOrder, service: Projects) -> ProjectOut:
    return service.reorder_classes(project_id, data.class_ids)
