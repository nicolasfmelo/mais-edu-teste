from __future__ import annotations

from fastapi import APIRouter

from app.delivery.schemas.prompt_registry_schemas import (
    ActivatePromptVersionRequestSchema,
    ActivePromptVersionResponseSchema,
    CreatePromptVersionRequestSchema,
    PromptRegistryEntryResponseSchema,
    PromptRegistryListResponseSchema,
    RegisterPromptRequestSchema,
)
from app.services.prompt.prompt_registry_service import PromptRegistryService


class PromptRegistryHandler:
    def __init__(self, prompt_registry_service: PromptRegistryService) -> None:
        self._prompt_registry_service = prompt_registry_service
        self.router = APIRouter(prefix="/api/prompt-registry", tags=["prompt-registry"])
        self.router.add_api_route("/prompts", self.list_prompts, methods=["GET"], response_model=PromptRegistryListResponseSchema)
        self.router.add_api_route("/prompts/{prompt_key}", self.get_prompt, methods=["GET"], response_model=PromptRegistryEntryResponseSchema)
        self.router.add_api_route("/prompts", self.register_prompt, methods=["POST"], response_model=PromptRegistryEntryResponseSchema)
        self.router.add_api_route(
            "/prompts/{prompt_key}/versions",
            self.create_version,
            methods=["POST"],
            response_model=PromptRegistryEntryResponseSchema,
        )
        self.router.add_api_route(
            "/prompts/{prompt_key}/active",
            self.get_active_version,
            methods=["GET"],
            response_model=ActivePromptVersionResponseSchema,
        )
        self.router.add_api_route(
            "/prompts/{prompt_key}/active",
            self.activate_version,
            methods=["POST"],
            response_model=PromptRegistryEntryResponseSchema,
        )

    async def list_prompts(self) -> PromptRegistryListResponseSchema:
        return PromptRegistryListResponseSchema.from_domain(self._prompt_registry_service.list_prompts())

    async def get_prompt(self, prompt_key: str) -> PromptRegistryEntryResponseSchema:
        return PromptRegistryEntryResponseSchema.from_domain(self._prompt_registry_service.get_prompt(prompt_key))

    async def register_prompt(self, body: RegisterPromptRequestSchema) -> PromptRegistryEntryResponseSchema:
        entry = self._prompt_registry_service.register_prompt(
            raw_key=body.key,
            template=body.template,
            description=body.description,
        )
        return PromptRegistryEntryResponseSchema.from_domain(entry)

    async def create_version(
        self,
        prompt_key: str,
        body: CreatePromptVersionRequestSchema,
    ) -> PromptRegistryEntryResponseSchema:
        entry = self._prompt_registry_service.create_version(
            raw_key=prompt_key,
            template=body.template,
            description=body.description,
        )
        return PromptRegistryEntryResponseSchema.from_domain(entry)

    async def get_active_version(self, prompt_key: str) -> ActivePromptVersionResponseSchema:
        version = self._prompt_registry_service.get_active_version(prompt_key)
        return ActivePromptVersionResponseSchema.from_domain(key=prompt_key, version=version)

    async def activate_version(
        self,
        prompt_key: str,
        body: ActivatePromptVersionRequestSchema,
    ) -> PromptRegistryEntryResponseSchema:
        entry = self._prompt_registry_service.activate_version(
            raw_key=prompt_key,
            raw_version_id=str(body.version_id),
        )
        return PromptRegistryEntryResponseSchema.from_domain(entry)
