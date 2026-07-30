from typing import Literal

from pydantic import BaseModel, Field


class ExpertDiscoveryRequest(BaseModel):
    field: str = Field(min_length=2, max_length=500)
    context: str | None = Field(default=None, max_length=2_000)
    country_codes: list[str] = Field(
        default_factory=lambda: ["KR"], min_length=1, max_length=10,
        description="ISO 3166-1 alpha-2 country scopes, e.g. KR, US, JP.",
    )
    max_candidates: int = Field(default=5, ge=1, le=10)


class Identity(BaseModel):
    full_name: str
    name_native: str | None
    name_variants: list[str]
    display_label: str
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
    matched_subfield: str
    country_code: str
    expertise_summary: str
    selection_rationale: str
    confidence: Literal["high", "medium", "low"]
    verification_notes: list[str]
    patent_search_keys: list[SearchKey]
    publication_search_keys: list[SearchKey]


class ExpertDiscoveryResponse(BaseModel):
    requested_field: str
    country_codes: list[str]
    interpreted_subfields: list[str]
    candidates: list[ExpertCandidate]
    warnings: list[str]
