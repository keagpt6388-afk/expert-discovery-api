from fastapi import Depends, FastAPI, HTTPException

from app.config import Settings, get_settings
from app.models import ExpertDiscoveryRequest, ExpertDiscoveryResponse
from app.security import require_service_key
from app.service import ExpertDiscoveryService

app = FastAPI(title="Expert Discovery API", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/v1/expert-discovery/search",
    response_model=ExpertDiscoveryResponse,
    dependencies=[Depends(require_service_key)],
)
def search_experts(
    request: ExpertDiscoveryRequest,
    settings: Settings = Depends(get_settings),
) -> ExpertDiscoveryResponse:
    try:
        return ExpertDiscoveryService(settings).discover(request)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Expert discovery provider request failed") from exc
