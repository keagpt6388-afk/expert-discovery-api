from typing import Literal

from pydantic import BaseModel, Field


class ExpertDiscoveryRequest(BaseModel):
    field: str = Field(min_length=2, max_length=500)
    context: str | None = Field(default=None, max_length=2_000)
    max_candidates: int = Field(default=5, ge=1, le=10)


class Identity(BaseModel):
    full_name: str
    name_native: str | None
    name_variants: list[str]
    nationality: str | None
    current_affiliation: str | None
    current_affiliation_detail: str | None
    role_or_title: str | None
    country_of_affiliation: str | None


class SearchKey(BaseModel):
    query: str
    purpose: Literal["patent", "publication", "both"]


class ExpertCandidate(BaseModel):
    identity: Identity
    expertise_summary: str
    selection_rationale: str
    confidence: Literal["high", "medium", "low"]
    verification_notes: list[str]
    patent_search_keys: list[SearchKey]
    publication_search_keys: list[SearchKey]


class ExpertDiscoveryResponse(BaseModel):
    requested_field: str
    candidates: list[ExpertCandidate]
    warnings: list[str]
