from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.domain_models.common.exceptions import StorageUnavailableError
from app.domain_models.prompt.exceptions import PromptAlreadyExistsError, PromptRegistryEntryNotFoundError
from app.domain_models.prompt.models import (
    PromptActivation,
    PromptKey,
    PromptRegistration,
    PromptRegistryEntry,
    PromptVersion,
    PromptVersionId,
    PromptVersionRegistration,
)
from app.engines.prompt.prompt_engine import PromptEngine
from app.integrations.database.models.prompt_models import PromptRegistryEntryModel, PromptVersionModel
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


class SQLAlchemyPromptRegistryRepository:
    def __init__(self, database: SQLAlchemyDatabase, prompt_engine: PromptEngine) -> None:
        self._database = database
        self._prompt_engine = prompt_engine

    def list_entries(self) -> tuple[PromptRegistryEntry, ...]:
        try:
            with self._database.session_scope() as session:
                rows = session.execute(
                    select(PromptRegistryEntryModel)
                    .options(selectinload(PromptRegistryEntryModel.versions))
                    .order_by(PromptRegistryEntryModel.key.asc())
                ).scalars().all()
                return tuple(self._to_domain(row) for row in rows)
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to list prompt registry entries.") from exc

    def find_by_key(self, key: PromptKey) -> PromptRegistryEntry:
        try:
            with self._database.session_scope() as session:
                row = session.get(
                    PromptRegistryEntryModel,
                    key.value,
                    options=(selectinload(PromptRegistryEntryModel.versions),),
                )
                if row is None:
                    raise PromptRegistryEntryNotFoundError(f"Prompt {key} not found")
                return self._to_domain(row)
        except PromptRegistryEntryNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to find prompt registry entry.") from exc

    def create_prompt(self, registration: PromptRegistration) -> PromptRegistryEntry:
        try:
            with self._database.session_scope() as session:
                row = PromptRegistryEntryModel(key=registration.key.value)
                row.versions.append(
                    PromptVersionModel(
                        id=PromptVersionId.new().value,
                        version_number=1,
                        template=registration.template,
                        description=registration.description,
                        is_active=True,
                    )
                )
                session.add(row)
                session.flush()
                session.refresh(row)
                return self._to_domain(row)
        except IntegrityError as exc:
            raise PromptAlreadyExistsError(f"Prompt {registration.key} already exists") from exc
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to create prompt registry entry.") from exc

    def create_version(self, registration: PromptVersionRegistration) -> PromptRegistryEntry:
        try:
            with self._database.session_scope() as session:
                row = session.get(
                    PromptRegistryEntryModel,
                    registration.key.value,
                    options=(selectinload(PromptRegistryEntryModel.versions),),
                )
                if row is None:
                    raise PromptRegistryEntryNotFoundError(f"Prompt {registration.key} not found")

                next_version_number = len(row.versions) + 1
                row.versions.append(
                    PromptVersionModel(
                        id=PromptVersionId.new().value,
                        version_number=next_version_number,
                        template=registration.template,
                        description=registration.description,
                        is_active=False,
                    )
                )
                session.flush()
                session.refresh(row)
                return self._to_domain(row)
        except PromptRegistryEntryNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to create prompt registry version.") from exc

    def activate_version(self, activation: PromptActivation) -> PromptRegistryEntry:
        try:
            with self._database.session_scope() as session:
                row = session.get(
                    PromptRegistryEntryModel,
                    activation.key.value,
                    options=(selectinload(PromptRegistryEntryModel.versions),),
                )
                if row is None:
                    raise PromptRegistryEntryNotFoundError(f"Prompt {activation.key} not found")

                domain_entry = self._to_domain(row)
                updated_entry = self._prompt_engine.activate_version(domain_entry, activation)

                for version_model in row.versions:
                    version_model.is_active = any(
                        version.id.value == version_model.id and version.is_active for version in updated_entry.versions
                    )

                session.flush()
                session.refresh(row)
                return self._to_domain(row)
        except PromptRegistryEntryNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to activate prompt registry version.") from exc

    def _to_domain(self, row: PromptRegistryEntryModel) -> PromptRegistryEntry:
        versions = tuple(
            PromptVersion(
                id=PromptVersionId(value=version.id),
                version_number=version.version_number,
                template=version.template,
                description=version.description,
                is_active=version.is_active,
            )
            for version in sorted(row.versions, key=lambda item: item.version_number)
        )
        return PromptRegistryEntry(
            key=PromptKey(value=row.key),
            versions=versions,
        )
