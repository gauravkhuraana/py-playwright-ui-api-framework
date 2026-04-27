"""Pydantic models for the Bill Payment API.

The ``_generated`` module is produced by ``make gen-api-models`` from the
upstream OpenAPI document. Do not hand-edit it. Add wrappers/extensions
here in ``__init__.py`` if you need to enrich generated models.
"""

from __future__ import annotations

try:  # pragma: no cover - generated module is optional until first build
    from . import _generated
except ImportError:
    _generated = None  # type: ignore[assignment]

__all__ = ["_generated"]
