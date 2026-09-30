# MMA FILE SUMMARY
# Purpose: Owns portable, strict schemas for acquisition and library identity.
# Public interface: Scope, Rights, Item, Occurrence, Tool argument models.
# Invariants: Unknown descriptive values are null; a right grants access only when true.
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

class Rights(StrictModel):
    acquisition: bool | None = None
    storage: bool | None = None
    indexing: bool | None = None
    model_transmission: bool | None = None
    redistribution: bool | None = None
    analysis: bool | None = None

class Scope(StrictModel):
    entity_id: str | None = None
    platform: str | None = None
    manufacturer: str | None = None
    hardware_model: str | None = None
    hardware_revision: str | None = None
    region: str | None = None
    system_version: str | None = None
    component_id: str | None = None
    component_version: str | None = None
    game_id: str | None = None
    game_edition: str | None = None
    game_build: str | None = None
    language: str | None = None
    category: str | None = None
    related_entities: list[str] = Field(default_factory=list, max_length=50)

State = Literal["DISCOVERED", "METADATA_ONLY", "STORED_ONLY", "PARTIAL", "INDEXED", "QUARANTINED", "FAILED"]

class Item(StrictModel):
    schema_version: str = "1.0.0"
    item_id: str
    revision_id: str
    title: str
    original_filename: str | None
    media_type: str | None
    size: int | None
    sha256: str | None
    source_key: str
    source_authority_keys: list[str] = Field(default_factory=list)
    source_occurrence_ids: list[str]
    scope: Scope
    role: Literal["original", "extracted", "decompiled", "model-generated"] = "original"
    parent_objects: list[str] = Field(default_factory=list)
    license: str | None = None
    permissions_at_acquisition: Rights
    access_policy: str = "operator-only"
    state: State
    processing_run_id: str | None = None
    warnings: list[str] = Field(default_factory=list)
    first_acquired_at: str
    publication_date: str | None = None
    original_version: str | None = None
    release_key: str
    repository_revision: str | None = None
    repository_revision_verification: str | None = None

class Occurrence(StrictModel):
    schema_version: str = "1.0.0"
    occurrence_id: str
    item_id: str
    revision_id: str
    source_key: str
    requested_url: str | None = None
    resolved_url: str | None = None
    acquired_at: str
    publication_date: str | None = None
    repository_revision: str | None = None
    sha256: str | None = None

class TargetArgs(StrictModel):
    target: str = Field(min_length=1,max_length=300)
    manufacturer: str | None = None
    platform: str | None = None
    kind: Literal["game_console","game","software_project","online_service","peripheral"] = "game_console"
    console_class: Literal["home","handheld","hybrid"] | None = None

class DiscoveryReceipt(StrictModel):
    provider: str = Field(min_length=1,max_length=100)
    query: str | None = Field(default=None,max_length=500)
    searched_at: str | None = Field(default=None,max_length=100)
    returned_urls: list[str] = Field(default_factory=list,max_length=100)

class PlanArgs(StrictModel):
    target: str = Field(min_length=1,max_length=300)
    seeds: list[str] = Field(default_factory=list,max_length=100)
    discovery_receipts: list[DiscoveryReceipt] = Field(default_factory=list,max_length=100)
    scope: Scope = Field(default_factory=Scope)
    max_items: int = Field(default=20,ge=1,le=1000)
    max_bytes: int = Field(default=33554432,ge=1,le=1073741824)
    max_depth: int = Field(default=1,ge=0,le=5)

class RunArgs(StrictModel):
    job_id: str
    step_items: int = Field(default=1,ge=1,le=5)
    retry_failed: bool = False

class StatusArgs(StrictModel):
    job_id: str

class ImportArgs(StrictModel):
    relative_path: str
    import_root: str = "inbox"
    scope: Scope = Field(default_factory=Scope)
    kind: Literal["file","folder","repository"] = "file"
    title: str | None = Field(default=None,max_length=300)
    publication_date: str | None = Field(default=None,max_length=100)
    provenance_role: Literal["original","extracted","decompiled","model-generated"] = "original"
    repository_revision: str | None = Field(default=None,max_length=64)

class BrowseArgs(StrictModel):
    scope: Scope = Field(default_factory=Scope)
    offset: int = Field(default=0,ge=0)
    limit: int = Field(default=25,ge=1,le=100)
    include_history: bool = False

class SearchArgs(StrictModel):
    query: str = Field(min_length=1,max_length=500)
    scope: Scope = Field(default_factory=Scope)
    mode: Literal["lexical","exact"] = "lexical"
    limit: int = Field(default=10,ge=1,le=50)

class ReadArgs(StrictModel):
    item_id: str
    revision_id: str
    chunk_id: str

class CaptureArgs(ReadArgs):
    intake: str

class Ref(StrictModel):
    item_id: str
    revision_id: str

class ExportArgs(StrictModel):
    items: list[Ref] = Field(min_length=1,max_length=100)

class ValidateArgs(StrictModel):
    rebuild_index: bool = False