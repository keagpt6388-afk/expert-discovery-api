import json
import hashlib
import time

from openai import OpenAI

from app.config import Settings
from app.models import ExpertDiscoveryRequest, ExpertDiscoveryResponse

SYSTEM_INSTRUCTIONS = """Create a broad expert-candidate list for a later patent and publication verification workflow.
This is a DISCOVERY stage, not an evidence-verification or patent/publication search stage. The output identifies people that a generally informed member of society would reasonably call experts in the requested field: professors, clinicians, senior researchers, technical leaders, founders, or other publicly recognized contributors. Do not require a person to have a directly verified patent or paper at this stage.
You MUST use the web search tool for currency. First decompose every natural-language request into 3 to 6 generic retrieval facets: exact terminology, broader parent concepts, adjacent technical approaches, synonyms, and useful English/Korean translations. Search every facet, merge and deduplicate people, and preserve coverage across facets so one narrow wording does not hide adjacent-domain experts. This is domain-neutral and applies to every field.
Use official institution, government, conference, ORCID, publisher, or reputable professional-news sources to identify current affiliation and public prominence. Prefer official sources when available, but do not omit a plainly relevant public expert solely because a later-stage patent or paper validation has not yet occurred. Apply a stable ranking: public field relevance, recognized role or contribution, current affiliation, then normalized full name.
The output is PERSON-ONLY: every candidate must be an identifiable individual researcher, professor, clinician, or inventor. Never return a laboratory, hospital, department, center, university, company, or an anonymous research team as a candidate.
Infer the country scope from the natural-language query. When multiple countries are named, return candidates for every requested country. Select people currently affiliated with institutions in the named country; do not use nationality as a proxy for country scope.
Return exactly max_candidates distinct people whenever the web search establishes that many suitable people; return fewer only when fewer suitable people can be verified. For each person return only full_name, affiliation, and nationality. Affiliation should include institution and role when known, such as 'OO대학교 교수'. For this API, nationality is an operational country label derived from the current affiliation, not a claim about legal citizenship: use 'Republic of Korea' for Korean institutions, 'United States' for US institutions, and 'Japan' for Japanese institutions. Use null only when the affiliation country cannot be established. Do not include explanations, search keys, sources, scores, subfields, contact details, home addresses, birth dates, or anonymous groups."""


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
CACHE: dict[str, tuple[float, ExpertDiscoveryResponse]] = {}
SEARCH_POLICY_VERSION = "expert-discovery-v4"


class ExpertDiscoveryService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key, timeout=settings.request_timeout_seconds)

    def discover(self, request: ExpertDiscoveryRequest) -> ExpertDiscoveryResponse:
        normalized = " ".join(request.query.casefold().split())
        cache_key = hashlib.sha256(f"{SEARCH_POLICY_VERSION}|{normalized}|{request.max_candidates}".encode()).hexdigest()
        cached = CACHE.get(cache_key)
        if cached and cached[0] > time.time():
            return cached[1]
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
        result = ExpertDiscoveryResponse.model_validate_json(response.output_text)
        CACHE[cache_key] = (time.time() + self.settings.result_cache_ttl_seconds, result)
        return result
