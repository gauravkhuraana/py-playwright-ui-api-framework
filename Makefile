# Enterprise UI + API Automation Framework
#
# Use `make help` to list targets. On Windows, run via `make` from a Git Bash /
# WSL shell, or invoke the equivalent commands directly with PowerShell.

PYTHON ?= python
UV     ?= uv
MARKERS ?= smoke
BROWSER ?= chromium
APP_ENV ?= dev

OPENAPI_URL = https://gauravkhurana.com/practise-api/openapi.yaml
GENERATED_MODELS = src/framework/api/models/_generated.py

.PHONY: help
help:
	@echo "Targets:"
	@echo "  install            Sync dependencies via uv and install Playwright browsers"
	@echo "  gen-api-models     Regenerate Pydantic models from the OpenAPI spec"
	@echo "  lint               Run ruff + black --check + mypy"
	@echo "  format             Auto-format with ruff and black"
	@echo "  test               Run all tests (markers via MARKERS=...)"
	@echo "  test-smoke         Run smoke suite in parallel"
	@echo "  test-api           Run API tests"
	@echo "  test-ui            Run UI tests"
	@echo "  test-e2e           Run E2E tests"
	@echo "  test-visual        Run visual regression tests"
	@echo "  update-snapshots   Update visual baselines"
	@echo "  report             Generate and open Allure report"
	@echo "  docker-build       Build the test Docker image"
	@echo "  docker-test        Run the smoke suite inside Docker"
	@echo "  clean              Remove caches and reports"

.PHONY: install
install:
	$(UV) sync --all-groups
	$(UV) run playwright install --with-deps

.PHONY: gen-api-models
gen-api-models:
	$(UV) run datamodel-codegen \
		--url $(OPENAPI_URL) \
		--input-file-type openapi \
		--output $(GENERATED_MODELS) \
		--output-model-type pydantic_v2.BaseModel \
		--target-python-version 3.12 \
		--use-standard-collections \
		--use-union-operator \
		--use-schema-description \
		--field-constraints \
		--snake-case-field \
		--use-double-quotes

.PHONY: lint
lint:
	$(UV) run ruff check .
	$(UV) run black --check .
	$(UV) run mypy src

.PHONY: format
format:
	$(UV) run ruff check --fix .
	$(UV) run ruff format .
	$(UV) run black .

.PHONY: test
test:
	APP_ENV=$(APP_ENV) $(UV) run pytest -m "$(MARKERS)" --browser=$(BROWSER) -n auto

.PHONY: test-smoke
test-smoke:
	APP_ENV=$(APP_ENV) $(UV) run pytest -m smoke --browser=$(BROWSER) -n auto

.PHONY: test-api
test-api:
	APP_ENV=$(APP_ENV) $(UV) run pytest -m api -n auto

.PHONY: test-ui
test-ui:
	APP_ENV=$(APP_ENV) $(UV) run pytest -m ui --browser=$(BROWSER)

.PHONY: test-e2e
test-e2e:
	APP_ENV=$(APP_ENV) $(UV) run pytest -m e2e --browser=$(BROWSER)

.PHONY: test-visual
test-visual:
	APP_ENV=$(APP_ENV) $(UV) run pytest -m visual --browser=$(BROWSER)

.PHONY: update-snapshots
update-snapshots:
	APP_ENV=$(APP_ENV) $(UV) run pytest -m visual --browser=$(BROWSER) --update-snapshots

.PHONY: report
report:
	allure generate reports/allure-results -o reports/allure-report --clean
	allure open reports/allure-report

.PHONY: docker-build
docker-build:
	docker build -t automation-framework:latest -f docker/Dockerfile .

.PHONY: docker-test
docker-test:
	docker compose -f docker/docker-compose.yml run --rm tests pytest -m smoke

.PHONY: clean
clean:
	rm -rf reports/ .pytest_cache/ .mypy_cache/ .ruff_cache/ test-results/ playwright-report/
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
