import json

from openai import OpenAI

from app.config import Settings
from app.models import ExpertDiscoveryRequest, ExpertDiscoveryResponse

SYSTEM_INSTRUCTIONS = """Create public-identity resolution seed data for patent and scholarly publication searching.
Identify notable real experts in the requested field. Use only reliable public facts. For each person return full name, known name variants, and the most detailed current affiliation available.
Never infer nationality from a name, language, ethnicity, or affiliation: return null whenever it is not known. State uncertainty in verification_notes.
Generate conservative, precise search keys for patents and publications. Do not include private contact information, home addresses, birth dates, or unsupported claims."""


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
