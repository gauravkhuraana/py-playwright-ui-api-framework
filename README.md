# Enterprise UI + API Automation Framework

Async-first Python automation framework for the **Bill Payment API** and the
companion practice UIs at [gauravkhurana.com](https://gauravkhurana.com).

| Layer | Tooling |
| ----- | ------- |
| Runner | `pytest` + `pytest-asyncio` + `pytest-xdist` |
| UI | `pytest-playwright` (chromium / firefox / webkit) |
| API | `httpx` async client + service objects |
| Models | `datamodel-code-generator` -> Pydantic v2 (from upstream OpenAPI) |
| Config | `pydantic-settings` + per-env YAML + `.env` |
| Secrets | Azure Key Vault (`DefaultAzureCredential` / GitHub OIDC) |
| Reporting | Allure + `pytest-html`, traces / videos / screenshots on failure |
| CI | GitHub Actions matrix (browser × shard) + nightly + Pages publish |
| Container | `mcr.microsoft.com/playwright/python` + uv |

---

## Quickstart (local)

```powershell
# 1. Install uv  (https://docs.astral.sh/uv/)
winget install --id Astral.uv

# 2. Sync deps and Playwright browsers
uv sync --all-groups
uv run playwright install --with-deps

# 3. Copy env template and edit values
copy .env.example .env

# 4. Generate API models from the upstream OpenAPI doc
make gen-api-models   # or run the equivalent uv run datamodel-codegen command

# 5. Smoke run (parallel)
uv run pytest -m smoke -n auto
```

Open `reports/pytest-report.html` for the HTML report or run
`make report` to view Allure locally.

## Layout

```
src/framework/
  api/           AsyncApiClient, auth strategies, service objects, models/
  ui/            BasePage and page objects
  config/        pydantic-settings + YAML loader
  secrets/       Key Vault provider (env-var fallback)
  data/          Faker-driven request factories
  logging.py     structlog setup
config/          dev.yaml, stage.yaml, prod.yaml
tests/
  api/           service-object tests (httpx)
  ui/            Playwright page tests
  e2e/           UI + API combined flows
docker/          Dockerfile + docker-compose.yml
.github/workflows/  ci.yml, nightly-regression.yml, publish-allure.yml
```

## Markers (tags)

Registered in `pyproject.toml` and enforced by `--strict-markers`:

| Marker | Meaning |
| ------ | ------- |
| `smoke` | Critical-path subset run on every PR |
| `regression` | Full regression suite |
| `api` | API-layer tests (auto-applied to `tests/api/`) |
| `ui` | UI tests (auto-applied to `tests/ui/`) |
| `e2e` | UI+API end-to-end flows (auto-applied to `tests/e2e/`) |
| `slow` | Long-running tests |
| `flaky` | Known-flaky tests, auto-retried |
| `visual` | Playwright snapshot / visual regression tests |

Run subsets:

```bash
uv run pytest -m smoke
uv run pytest -m "regression and not flaky"
uv run pytest -m api -n auto
uv run pytest -m ui --browser=firefox
uv run pytest -m visual --update-snapshots   # to refresh baselines
```

## Environments

`APP_ENV` selects the YAML file under `config/`. Settings precedence (highest
first):

1. Process env / `.env` (`API_BASE_URL`, `API_KEY`, ...)
2. `config/<APP_ENV>.yaml`
3. Defaults on `Settings`

```bash
APP_ENV=stage uv run pytest -m smoke
```

## Secrets

When `USE_KEYVAULT=true` and `KEYVAULT_NAME` is set, the framework reads
secrets from Azure Key Vault using `DefaultAzureCredential`. Locally that
means `az login`; in CI it means a GitHub OIDC federated credential. Secret
names are prefixed by env, e.g. `dev-api-key`, `stage-api-key`.

Otherwise plain env vars are used (e.g. `API_KEY=...`).

## Docker

```bash
make docker-build
make docker-test                # smoke run inside container
docker compose -f docker/docker-compose.yml up allure   # Allure live UI on :5050
```

## CI

* `.github/workflows/ci.yml` - lint -> matrix test (browser × shard); accepts
  `markers`, `app_env`, and `update_snapshots` via `workflow_dispatch`.
* `.github/workflows/nightly-regression.yml` - daily regression on all
  browsers.
* `.github/workflows/publish-allure.yml` - on successful CI runs against
  `main`, generates the Allure report and pushes it to the `gh-pages` branch.
  Enable Pages: **Settings -> Pages -> Source: gh-pages branch / root**.

For OIDC -> Azure, set repo variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `KEYVAULT_NAME`.

## Adding new tests

* **API**: subclass `BaseService` if a new resource is added; otherwise call
  the existing service objects from a test under `tests/api/`.
* **UI**: subclass `BasePage`, expose locators as `@property`, then write a
  test under `tests/ui/`. Apply `@pytest.mark.visual` for snapshot coverage.
* **E2E**: place under `tests/e2e/`. The framework auto-tags by directory.

See [docs/architecture.md](docs/architecture.md) for the layered diagram.
