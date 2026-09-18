"""GitHub API lookups used to enrich manifest entries at build time.

For each ``{owner, repo}`` pair in ``data/manifest.json`` this calls the
GitHub REST API once to pull:

- ``description``      -- used when the manifest entry doesn't set one
- icons                 -- topic-matched icons (see ``icons.py``), shown as a
                            row; a manifest ``logo`` override takes the place
                            of topic matching entirely
- avatar                -- the owner's GitHub avatar, shown as a thumbnail
                            regardless of whether any topic icon matched
- ``is_template``       -- the repo is itself usable as a GitHub template
- ``template_repository`` -- the repo was generated from a template repo
- ``topics``            -- the repo's GitHub topics, merged with any topics
                            already set on the manifest entry
- ``homepage``          -- the repo's configured website, used when the
                            manifest entry doesn't set ``website``

A manifest entry may also set ``branch`` to point ``repo_url``/``fork_url``
at a non-default branch, e.g. when an example needed Aiven Runtime-specific
changes that only live on a branch.

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

from icons import resolve_logos

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
MAX_DESCRIPTION_LENGTH = 350


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
        "generate_url": (
            f"https://github.com/{owner}/{repo}/generate"
            if data.get("is_template")
            else None
        ),
        "template_repository": (
            {
                "full_name": template_repository["full_name"],
                "html_url": template_repository["html_url"],
            }
            if template_repository
            else None
        ),
        "topics": data.get("topics", []),
        "homepage": data.get("homepage") or None,
    }


def enrich_manifest(manifest: list[dict]) -> list[dict]:
    """Merge GitHub API data onto each manifest entry.

    Manifest values always win over GitHub-sourced values, except that a
    description/website is only ever filled in when the manifest omitted
    one, and topics are the union of both sources. ``icons`` is the row of
    topic-matched icons, unless the manifest sets a ``logo`` override, in
    which case that's the only icon shown. ``avatar`` is always the owner's
    GitHub avatar, independent of ``icons``.

    An entry may set ``branch`` when its example lives on a non-default
    branch (e.g. a repo that needed Aiven Runtime-specific changes that
    haven't landed on the default branch yet). This only changes the
    generated URLs -- GitHub's repo/topics/template API data is branch-
    independent.
    """
    enriched = []
    with httpx.Client(timeout=10) as client:
        for entry in manifest:
            info = fetch_repo_info(entry["owner"], entry["repo"], client=client)
            base_url = f"https://github.com/{entry['owner']}/{entry['repo']}"
            branch = entry.get("branch")
            description = (
                entry.get("description") or info.get("github_description") or ""
            )
            if len(description) > MAX_DESCRIPTION_LENGTH:
                raise ValueError(
                    f"{entry['name']!r} description is {len(description)} chars, "
                    f"over the {MAX_DESCRIPTION_LENGTH} char limit"
                )
            topics = sorted(set(entry.get("topics", [])) | set(info.get("topics", [])))
            icons = [entry["logo"]] if entry.get("logo") else resolve_logos(topics, client=client)
            merged = {
                **entry,
                "repo_url": f"{base_url}/tree/{branch}" if branch else base_url,
                "fork_url": f"{base_url}/fork?ref={branch}" if branch else f"{base_url}/fork",
                "description": description,
                "icons": icons,
                "avatar": info.get("avatar_url") or "",
                "is_template": info.get("is_template", False),
                "generate_url": info.get("generate_url"),
                "template_repository": info.get("template_repository"),
                "topics": topics,
                "website": entry.get("website") or info.get("homepage") or "",
            }
            enriched.append(merged)
    return enriched
