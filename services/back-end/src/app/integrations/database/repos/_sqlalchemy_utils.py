from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.interfaces import ORMOption

from app.domain_models.common.exceptions import StorageUnavailableError


ModelT = TypeVar("ModelT")
ExceptionT = TypeVar("ExceptionT", bound=Exception)
ReturnT = TypeVar("ReturnT")


@dataclass(frozen=True)
class EntityLookup(Generic[ModelT, ExceptionT]):
    model_type: type[ModelT]
    entity_id: object
    options: tuple[ORMOption, ...] = ()
    not_found: Callable[[], ExceptionT] | None = None


def load_entity(
    session: Session,
    lookup: EntityLookup[ModelT, ExceptionT],
) -> ModelT | None:
    return session.get(lookup.model_type, lookup.entity_id, options=lookup.options)


def require_entity(
    session: Session,
    lookup: EntityLookup[ModelT, ExceptionT],
) -> ModelT:
    model = load_entity(session, lookup)
    if model is None:
        if lookup.not_found is None:
            raise ValueError("EntityLookup.not_found must be provided for required loads.")
        raise lookup.not_found()
    return model


def with_storage_error(operation: Callable[[], ReturnT], *, message: str) -> ReturnT:
    try:
        return operation()
    except SQLAlchemyError as exc:
        raise StorageUnavailableError(message) from exc
