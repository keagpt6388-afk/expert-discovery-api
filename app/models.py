from pydantic import BaseModel, Field


class ExpertDiscoveryRequest(BaseModel):
    field: str = Field(min_length=2, max_length=500)
    context: str | None = Field(default=None, max_length=2_000)
    country_codes: list[str] = Field(default_factory=lambda: ["KR"], min_length=1, max_length=10)
    max_candidates: int = Field(default=5, ge=1, le=10)


class Expert(BaseModel):
    full_name: str
    affiliation: str | None
    nationality: str | None


class ExpertDiscoveryResponse(BaseModel):
    experts: list[Expert]
