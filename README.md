# Expert Discovery API

New, standalone FastAPI service that turns a research-field request into strict JSON expert identity and search seed data for a downstream patent/publication orchestrator.

## Endpoints

- `GET /health` - unauthenticated health check
- `POST /v1/expert-discovery/search` - Bearer-authenticated expert discovery
- `GET /docs` - Swagger UI

## Run locally

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Call the API:

```powershell
$headers = @{ Authorization = "Bearer <SERVICE_API_KEY>" }
$body = @{ query = "전고체 배터리 소재 중 리튬 금속 음극 전문가를 한국과 미국에서 찾아줘"; max_candidates = 5 } | ConvertTo-Json
Invoke-RestMethod http://localhost:8000/v1/expert-discovery/search -Method Post -Headers $headers -ContentType application/json -Body $body
```

`query` is the single natural-language input. Include countries, field, and any constraints in the sentence. The response returns only `full_name`, `affiliation`, and `nationality` for each individual.

Every request invokes the Responses API web-search tool before candidates are selected. This improves currency of affiliation and research-area information, but each web-search call is separately billed by OpenAI and still requires downstream patent/publication DB validation for final identity matching.

## Security and deployment

`OPENAI_API_KEY` and `SERVICE_API_KEYS` must be configured only as environment secrets. They are excluded from Git by `.gitignore`.

`render.yaml` deploys this as an independent Render Web Service. Create the Render service from the repository, then fill the two secret values in the Render dashboard. `main` pushes can trigger automatic deployment.

## Test

```powershell
python -m pytest -q
```
