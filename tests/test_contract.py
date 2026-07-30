from app.models import ExpertDiscoveryResponse
from app.service import EXPERT_DISCOVERY_SCHEMA


def test_response_contract_validates():
    value = ExpertDiscoveryResponse.model_validate({
        "experts": [{"full_name": "Example Researcher", "affiliation": "Example University Professor", "nationality": None}],
    })
    assert value.experts[0].full_name == "Example Researcher"


def test_strict_schema_closes_objects():
    assert EXPERT_DISCOVERY_SCHEMA["additionalProperties"] is False
    assert set(EXPERT_DISCOVERY_SCHEMA["required"]) == {
        "experts"
    }
