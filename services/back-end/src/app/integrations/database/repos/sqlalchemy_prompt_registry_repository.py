from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.domain_models.common.exceptions import StorageUnavailableError
from app.domain_models.prompt.exceptions import PromptAlreadyExistsError, PromptRegistryEntryNotFoundError
from app.domain_models.prompt.models import (
    PromptKey,
    PromptRegistration,
    PromptRegistryEntry,
    PromptVersion,
    PromptVersionId,
    PromptVersionRegistration,
)
from app.integrations.database.models.prompt_models import PromptRegistryEntryModel, PromptVersionModel
from app.integrations.database.repos._sqlalchemy_utils import EntityLookup, require_entity, with_storage_error
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


class SQLAlchemyPromptRegistryRepository:
    def __init__(self, database: SQLAlchemyDatabase) -> None:
        self._database = database

    def list_entries(self) -> tuple[PromptRegistryEntry, ...]:
        return with_storage_error(
            self._list_entries,
            message="Unable to list prompt registry entries.",
        )

    def find_by_key(self, key: PromptKey) -> PromptRegistryEntry:
        return with_storage_error(
            lambda: self._find_by_key(key),
            message="Unable to find prompt registry entry.",
        )

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
        return with_storage_error(
            lambda: self._create_version(registration),
            message="Unable to create prompt registry version.",
        )

    def activate_version(self, entry: PromptRegistryEntry) -> PromptRegistryEntry:
        return with_storage_error(
            lambda: self._activate_version(entry),
            message="Unable to activate prompt registry version.",
        )

    def _list_entries(self) -> tuple[PromptRegistryEntry, ...]:
        with self._database.session_scope() as session:
            rows = session.execute(
                select(PromptRegistryEntryModel)
                .options(selectinload(PromptRegistryEntryModel.versions))
                .order_by(PromptRegistryEntryModel.key.asc())
            ).scalars().all()
            return tuple(self._to_domain(row) for row in rows)

    def _find_by_key(self, key: PromptKey) -> PromptRegistryEntry:
        with self._database.session_scope() as session:
            row = require_entity(session, self._required_prompt_lookup(key))
            return self._to_domain(row)

    def _create_version(self, registration: PromptVersionRegistration) -> PromptRegistryEntry:
        with self._database.session_scope() as session:
            row = require_entity(session, self._required_prompt_lookup(registration.key))

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

    def _activate_version(self, entry: PromptRegistryEntry) -> PromptRegistryEntry:
        with self._database.session_scope() as session:
            row = require_entity(session, self._required_prompt_lookup(entry.key))

            for version_model in row.versions:
                version_model.is_active = any(
                    version.id.value == version_model.id and version.is_active for version in entry.versions
                )

            session.flush()
            session.refresh(row)
            return self._to_domain(row)

    def _required_prompt_lookup(
        self,
        key: PromptKey,
    ) -> EntityLookup[PromptRegistryEntryModel, PromptRegistryEntryNotFoundError]:
        return EntityLookup(
            model_type=PromptRegistryEntryModel,
            entity_id=key.value,
            options=(selectinload(PromptRegistryEntryModel.versions),),
            not_found=lambda: PromptRegistryEntryNotFoundError(f"Prompt {key} not found"),
        )

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
