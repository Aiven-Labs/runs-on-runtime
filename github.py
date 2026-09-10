"""GitHub API lookups used to enrich manifest entries at build time.

For each ``{owner, repo}`` pair in ``data/manifest.json`` this calls the
GitHub REST API once to pull:

- ``description``      -- used when the manifest entry doesn't set one
- owner avatar          -- used as a logo fallback when the manifest entry
                            doesn't set ``logo``
- ``is_template``       -- the repo is itself usable as a GitHub template
- ``template_repository`` -- the repo was generated from a template repo
- ``topics``            -- the repo's GitHub topics, merged with any topics
                            already set on the manifest entry

An optional ``GITHUB_TOKEN`` environment variable is sent as a bearer token
to raise the rate limit from 60/hr to 5000/hr. Any failure for a single repo
(network error, 404, rate limit) is logged and that entry falls back to
whatever the manifest already had -- a bad/missing token must never break
the build.
"""

from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_repo_info(owner: str, repo: str, *, client: httpx.Client) -> dict:
    """Fetch template/description/avatar info for one repo.

    Returns an empty dict (rather than raising) if the lookup fails, so a
    single bad entry or rate limit doesn't break the whole build.
    """
    try:
        response = client.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=_headers())
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("GitHub lookup failed for %s/%s: %s", owner, repo, exc)
        return {}

    data = response.json()
    template_repository = data.get("template_repository")

    return {
        "github_description": data.get("description"),
        "avatar_url": data.get("owner", {}).get("avatar_url"),
        "is_template": data.get("is_template", False),
        "generate_url": f"https://github.com/{owner}/{repo}/generate"
        if data.get("is_template")
        else None,
        "template_repository": (
            {
                "full_name": template_repository["full_name"],
                "html_url": template_repository["html_url"],
            }
            if template_repository
            else None
        ),
        "topics": data.get("topics", []),
    }


def enrich_manifest(manifest: list[dict]) -> list[dict]:
    """Merge GitHub API data onto each manifest entry.

    Manifest values always win over GitHub-sourced values, except that a
    logo/description is only ever filled in when the manifest omitted one,
    and topics are the union of both sources.
    """
    enriched = []
    with httpx.Client(timeout=10) as client:
        for entry in manifest:
            info = fetch_repo_info(entry["owner"], entry["repo"], client=client)
            merged = {
                **entry,
                "repo_url": f"https://github.com/{entry['owner']}/{entry['repo']}",
                "description": entry.get("description")
                or info.get("github_description")
                or "",
                "logo": entry.get("logo") or info.get("avatar_url") or "",
                "is_template": info.get("is_template", False),
                "generate_url": info.get("generate_url"),
                "template_repository": info.get("template_repository"),
                "topics": sorted(
                    set(entry.get("topics", [])) | set(info.get("topics", []))
                ),
            }
            enriched.append(merged)
    return enriched
