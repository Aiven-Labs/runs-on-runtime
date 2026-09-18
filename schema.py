"""Validation for ``data/manifest.json`` entries.

Run at build time (see ``app.load_repos``) so a malformed or incomplete
manifest entry fails the build/test suite instead of silently rendering a
broken card -- e.g. a missing ``added`` date, which drives the "recently
added" sort/filter.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, TypeAdapter


class ManifestEntry(BaseModel):
    """Required and optional fields for one ``data/manifest.json`` entry.

    ``extra="forbid"`` so a typo'd key (e.g. ``discription``) fails the
    build loudly rather than being silently ignored.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    owner: str
    repo: str
    added: date
    branch: str | None = None
    description: str | None = None
    logo: str | None = None
    topics: list[str] = []
    website: str | None = None


_MANIFEST_ADAPTER = TypeAdapter(list[ManifestEntry])


def validate_manifest(manifest: list[dict]) -> list[dict]:
    """Validate raw manifest entries, returning them as plain dicts.

    Raises ``pydantic.ValidationError`` (with the offending entry's index
    and field) if any entry is missing a required field or has the wrong
    type -- e.g. a missing ``added`` date.
    """
    entries = _MANIFEST_ADAPTER.validate_python(manifest)
    return [entry.model_dump(mode="json", exclude_none=True) for entry in entries]
