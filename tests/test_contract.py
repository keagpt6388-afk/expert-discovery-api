from app.models import ExpertDiscoveryResponse
from app.service import EXPERT_DISCOVERY_SCHEMA


def test_response_contract_validates():
    value = ExpertDiscoveryResponse.model_validate({
        "requested_field": "robotics",
        "candidates": [],
        "warnings": ["No candidates were returned in this synthetic test."],
    })
    assert value.requested_field == "robotics"


def test_strict_schema_closes_objects():
    assert EXPERT_DISCOVERY_SCHEMA["additionalProperties"] is False
    assert set(EXPERT_DISCOVERY_SCHEMA["required"]) == {"requested_field", "candidates", "warnings"}
