"""Topic -> logo resolution for manifest entries.

Three tiers, checked in order for each of a repo's topics:

1. ``AIVEN_SERVICE_ICONS`` -- official colored Aiven service icons, already
   vendored under ``static/images/services/``. These take priority since
   they're the on-brand mark for services Aiven actually runs.
2. ``DEVICON_TOPICS`` -- colored icons from the Devicon project for
   languages, frameworks, and tools.
3. ``SIMPLEICONS_TOPICS`` -- brand icons from the Simple Icons project,
   covering everything Devicon doesn't (Simple Icons' catalog is much
   larger, especially for infra/cloud/vendor tools).

Tiers 2 and 3 are downloaded once from their respective CDNs and cached
under ``static/images/devicon/`` and ``static/images/simpleicons/`` so a
build never re-fetches an icon it already has on disk.

A repo can match more than one topic (e.g. both ``kafka`` and ``python``);
``resolve_logos`` returns every match, in tier order, so the caller can show
them as a row of icons. The repo owner's avatar is shown separately as a
thumbnail, regardless of whether any topic matched.

Official project marks missing from these catalogs are vendored under
``static/images/brands/`` and appended to the row.
"""

from __future__ import annotations

import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

SERVICES_DIR = Path("static/images/services")
DEVICON_CACHE_DIR = Path("static/images/devicon")
DEVICON_CDN = "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons"
SIMPLEICONS_CACHE_DIR = Path("static/images/simpleicons")
SIMPLEICONS_CDN = "https://cdn.simpleicons.org"

# topic (as it appears in GitHub/manifest topics) -> filename in SERVICES_DIR
AIVEN_SERVICE_ICONS = {
    "kafka": "kafka.svg",
    "apache-kafka": "kafka.svg",
    "postgresql": "postgresql.svg",
    "postgres": "postgresql.svg",
    "pg": "postgresql.svg",
    "valkey": "valkey.svg",
    "clickhouse": "clickhouse.svg",
    "mysql": "mysql.svg",
    "opensearch": "opensearch.svg",
    "grafana": "grafana.svg",
}

# Official project marks not available in the icon catalogs. See
# static/images/brands/README.md for sources.
PROJECT_ICONS = {
    "litellm": "/static/images/brands/litellm.webp",
    "langfuse": "/static/images/brands/langfuse.svg",
}

# topic -> devicon icon slug (uses the colored "-original" variant)
DEVICON_TOPICS = {
    "python": "python",
    "go": "go",
    "golang": "go",
    "nodejs": "nodejs",
    "node": "nodejs",
    "react": "react",
    "reactjs": "react",
    "redis": "redis",
    "airflow": "apacheairflow",
    "apache-airflow": "apacheairflow",
    "docker": "docker",
    "javascript": "javascript",
    "typescript": "typescript",
    "traefik": "traefikproxy",
}

# topic -> Simple Icons slug, for anything Devicon doesn't cover (infra,
# cloud, orchestration, vendor tools, etc.)
SIMPLEICONS_TOPICS = {
    "n8n": "n8n",
    "metabase": "metabase",
    "streamlit": "streamlit",
    "langgraph": "langgraph",
    "temporal": "temporal",
    "hasura": "hasura",
    "umami": "umami",
    "jaeger": "jaeger",
    "mcp": "modelcontextprotocol",
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "terraform": "terraform",
    "ansible": "ansible",
    "helm": "helm",
    "vault": "vault",
    "consul": "consul",
    "nomad": "nomad",
    "aws": "amazonwebservices",
    "gcp": "googlecloud",
    "google-cloud": "googlecloud",
    "azure": "microsoftazure",
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "cassandra": "apachecassandra",
    "mariadb": "mariadb",
    "sqlite": "sqlite",
    "rabbitmq": "rabbitmq",
    "prometheus": "prometheus",
    "elasticsearch": "elasticsearch",
    "graphql": "graphql",
    "grpc": "grpc",
    "vue": "vuedotjs",
    "vuejs": "vuedotjs",
    "svelte": "svelte",
    "sveltejs": "svelte",
    "rust": "rust",
    "java": "openjdk",
    "kotlin": "kotlin",
    "php": "php",
    "ruby": "ruby",
    "rails": "rubyonrails",
    "django": "django",
    "flask": "flask",
    "fastapi": "fastapi",
    "nginx": "nginx",
    "github-actions": "githubactions",
    "gitlab": "gitlab",
    "jenkins": "jenkins",
    "jupyter": "jupyter",
    "pandas": "pandas",
    "numpy": "numpy",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "argo": "argo",
    "argocd": "argo",
}


def _devicon_url(slug: str) -> str:
    return f"{DEVICON_CDN}/{slug}/{slug}-original.svg"


def _simpleicons_url(slug: str) -> str:
    return f"{SIMPLEICONS_CDN}/{slug}"


def _cached_icon_path(
    slug: str, *, cache_dir: Path, url: str, client: httpx.Client, source: str
) -> Path | None:
    """Return the on-disk cached SVG for ``slug``, downloading it once if needed."""
    cache_path = cache_dir / f"{slug}.svg"
    if cache_path.exists():
        return cache_path

    try:
        response = client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("%s lookup failed for %s: %s", source, slug, exc)
        return None

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(response.content)
    return cache_path


def resolve_logos(topics: list[str], *, client: httpx.Client) -> list[str]:
    """Return site-relative logo URLs for every topic that matches.

    Checks Aiven service icons first, then Devicon, then Simple Icons,
    across all of a repo's topics -- so topic order in the manifest doesn't
    matter, only which tier a match is found in. Results are deduplicated
    but keep tier order.
    """
    logos: list[str] = []

    for topic in topics:
        if filename := AIVEN_SERVICE_ICONS.get(topic):
            url = f"/static/images/services/{filename}"
            if url not in logos:
                logos.append(url)

    for topic in topics:
        if slug := DEVICON_TOPICS.get(topic):
            if _cached_icon_path(
                slug,
                cache_dir=DEVICON_CACHE_DIR,
                url=_devicon_url(slug),
                client=client,
                source="Devicon",
            ):
                url = f"/static/images/devicon/{slug}.svg"
                if url not in logos:
                    logos.append(url)

    for topic in topics:
        if slug := SIMPLEICONS_TOPICS.get(topic):
            if _cached_icon_path(
                slug,
                cache_dir=SIMPLEICONS_CACHE_DIR,
                url=_simpleicons_url(slug),
                client=client,
                source="Simple Icons",
            ):
                url = f"/static/images/simpleicons/{slug}.svg"
                if url not in logos:
                    logos.append(url)

    for topic in topics:
        if (url := PROJECT_ICONS.get(topic)) and url not in logos:
            logos.append(url)

    return logos
