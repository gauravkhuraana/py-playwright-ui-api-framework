"""Secret resolution: Azure Key Vault with env-var fallback."""

from __future__ import annotations

from .keyvault import SecretProvider, get_secret_provider

__all__ = ["SecretProvider", "get_secret_provider"]
