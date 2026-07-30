import json

from openai import OpenAI

from app.config import Settings
from app.models import ExpertDiscoveryRequest, ExpertDiscoveryResponse

SYSTEM_INSTRUCTIONS = """Create public-identity resolution seed data for patent and scholarly publication searching.
You MUST use the web search tool before selecting candidates. Prefer official university, hospital, laboratory, government research, ORCID, publisher, patent-office, or conference sources. Use current web evidence to verify the person's affiliation and technical relevance; do not rely only on pretraining knowledge.
The output is PERSON-ONLY: every candidate must be an identifiable individual researcher, professor, clinician, or inventor. Never return a laboratory, hospital, department, center, university, company, or an anonymous research team as a candidate.
Infer the country scope from the natural-language query. When multiple countries are named, return candidates for every requested country. Select people currently affiliated with institutions in the named country; do not use nationality as a proxy for country scope.
For each person return only full_name, affiliation, and nationality. Affiliation should include institution and role when known, such as 'OO대학교 교수'. Never infer nationality from a name, language, ethnicity, or affiliation: return null whenever it is not known. Do not include explanations, search keys, sources, scores, subfields, contact details, home addresses, birth dates, or anonymous groups."""


def _make_strict(schema: dict) -> dict:
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            schema["additionalProperties"] = False
            schema["required"] = list(properties)
        for value in schema.values():
            _make_strict(value)
    elif isinstance(schema, list):
        for value in schema:
            _make_strict(value)
    return schema


EXPERT_DISCOVERY_SCHEMA = _make_strict(ExpertDiscoveryResponse.model_json_schema())


class ExpertDiscoveryService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key, timeout=settings.request_timeout_seconds)

    def discover(self, request: ExpertDiscoveryRequest) -> ExpertDiscoveryResponse:
        response = self.client.responses.create(
            model=self.settings.openai_model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=json.dumps(request.model_dump(), ensure_ascii=False),
            tools=[{"type": "web_search"}],
            tool_choice="required",
            text={
                "format": {
                    "type": "json_schema",
                    "name": "expert_discovery_response",
                    "strict": True,
                    "schema": EXPERT_DISCOVERY_SCHEMA,
                }
            },
        )
        if not response.output_text:
            raise RuntimeError("Responses API returned no output_text")
        return ExpertDiscoveryResponse.model_validate_json(response.output_text)
