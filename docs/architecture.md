# Architecture

```
+----------------------------+        +-----------------------------+
|         tests/             |        |        config/              |
|  api/  ui/  e2e/           |<-------|  dev.yaml stage.yaml prod   |
|  (markers, fixtures)       |        +-----------------------------+
+-------------+--------------+                       |
              |                                      v
              |                          +-----------------------------+
              |                          |  src/framework/config       |
              |                          |  Settings (pydantic)        |
              |                          +-----------+-----------------+
              v                                      |
+----------------------------+        +--------------v--------------+
|  src/framework/api         |        |  src/framework/secrets      |
|  - AsyncApiClient          |        |  - SecretProvider           |
|  - AuthStrategy(s)         |        |    (Key Vault + env fallback)|
|  - BaseService             |        +-----------------------------+
|  - services/* (per tag)    |
|  - models/_generated.py    |
+-------------+--------------+
              |
              v
+----------------------------+        +-----------------------------+
|  src/framework/ui          |        |  src/framework/data         |
|  - BasePage                |        |  - UserFactory              |
|  - pages/*                 |        |  - BillerFactory            |
+----------------------------+        |  - BillFactory ...          |
                                      +-----------------------------+

           +----------------------+
           |  reports/            |
           |  - allure-results/   |
           |  - pytest-report.html|
           |  - videos/, traces/  |
           +----------------------+
```

## Adding a new API resource

1. Add a service module under `src/framework/api/services/` extending
   `BaseService` and exposing async methods that wrap the new endpoints.
2. Re-export from `services/__init__.py`.
3. Add a fixture in `conftest.py` that constructs the service from
   `api_client`.
4. (Optional) Re-run `make gen-api-models` if upstream spec changed and
   commit the regenerated `_generated.py`.
5. Author tests under `tests/api/`.

## Adding a new UI page

1. Create a class under `src/framework/ui/pages/` inheriting `BasePage`.
2. Expose locators as `@property` returning Playwright `Locator`s, and add
   high-level action methods (`login()`, `expect_loaded()`, ...).
3. Re-export from `pages/__init__.py`.
4. Author tests under `tests/ui/`.

## Why these choices?

* **httpx (async)** beats `requests` for parallel API tests; `pytest-xdist`
  workers each run an event loop, but inside a worker the async client lets
  one test fan out independent calls cheaply.
* **Service / Page objects** keep raw selectors and URLs out of test files.
* **Codegen models** mean the contract test layer evolves automatically with
  the upstream OpenAPI spec.
* **GitHub OIDC -> Key Vault** removes long-lived secrets from the repo.
* **Browser × shard matrix** keeps wall-clock low while exercising all three
  Playwright engines.
