"""Secret provider that prefers Azure Key Vault and falls back to env vars.

When ``USE_KEYVAULT=true`` and ``KEYVAULT_NAME`` is set, secrets are pulled
from a single shared vault. Secret names are prefixed with the active
environment, e.g. ``dev-api-key``. Locally, ``DefaultAzureCredential`` picks
up ``az login`` credentials; in CI, GitHub OIDC federated credentials are used.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache

from ..config import get_settings

logger = logging.getLogger(__name__)


class SecretProvider:
    """Unified read interface for secrets."""

    def __init__(self, env: str, vault_name: str | None, use_keyvault: bool) -> None:
        self._env = env
        self._vault_name = vault_name
        self._use_keyvault = use_keyvault and bool(vault_name)
        self._client = None
        if self._use_keyvault:
            self._client = self._build_client(vault_name)  # type: ignore[arg-type]

    @staticmethod
    def _build_client(vault_name: str):  # pragma: no cover - exercised via integration tests
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        url = f"https://{vault_name}.vault.azure.net"
        return SecretClient(vault_url=url, credential=DefaultAzureCredential())

    def get(self, name: str, default: str | None = None) -> str | None:
        """Return the secret value for ``name`` or ``default`` if absent.

        Local lookup order: Key Vault (if enabled) -> env var (uppercased,
        dashes -> underscores) -> ``default``.
        """
        if self._use_keyvault and self._client is not None:
            full_name = f"{self._env}-{name}"
            try:
                return self._client.get_secret(full_name).value
            except Exception as exc:  # pragma: no cover
                logger.warning("Key Vault lookup failed for %s: %s", full_name, exc)

        env_name = name.upper().replace("-", "_")
        return os.getenv(env_name, default)


@lru_cache(maxsize=1)
def get_secret_provider() -> SecretProvider:
    settings = get_settings()
    return SecretProvider(
        env=settings.app_env,
        vault_name=settings.keyvault_name,
        use_keyvault=settings.use_keyvault,
    )
