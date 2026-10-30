from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import AppSetting

T = TypeVar("T", bound=BaseModel)


class SettingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def load(self, key: str, model: type[T]) -> T:
        row = self.db.get(AppSetting, key)
        if row is None:
            return model()
        try:
            return model.model_validate(row.value)
        except ValueError:
            return model()  # stored value from an older version; fall back to defaults

    def save(self, key: str, value: BaseModel) -> None:
        row = self.db.get(AppSetting, key)
        data = value.model_dump(mode="json")
        if row is None:
            self.db.add(AppSetting(key=key, value=data))
        else:
            row.value = data
        self.db.commit()
