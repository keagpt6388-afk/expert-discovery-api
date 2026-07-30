from pydantic import BaseModel, Field


class ExpertDiscoveryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2_000)
    max_candidates: int = Field(default=10, ge=1, le=10)


class Expert(BaseModel):
    full_name: str
    affiliation: str | None
    nationality: str | None


class ExpertDiscoveryResponse(BaseModel):
    experts: list[Expert]
