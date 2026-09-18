"""
Render Engine app for the Aiven Runtime repo directory.

Build with:
    uv run python app.py
or:
    uv run render-engine build app:app
"""

import json
from collections import Counter
from pathlib import Path

from render_engine import Collection, Page, Site
from render_engine_markdown import MarkdownPageParser

from github import canonicalize_topic, enrich_manifest
from icons import AIVEN_SERVICE_ICONS
from schema import validate_manifest

AIVEN_SERVICE_TOPICS = {canonicalize_topic(topic) for topic in AIVEN_SERVICE_ICONS}

MANIFEST_PATH = Path("data/manifest.json")

app = Site(output_path="output", static_paths={"static"})
app.site_vars.update(
    {"SITE_TITLE": "Runs on Runtime", "SITE_URL": "https://templates.aiven.io"}
)


def load_repos() -> list[dict]:
    manifest = json.loads(MANIFEST_PATH.read_text())
    return enrich_manifest(validate_manifest(manifest))


def mark_source(repos: list[dict]) -> list[dict]:
    """Tag each repo as an Aiven-owned template vs a community contribution,
    based on whether its GitHub owner is one of the aiven-labs orgs."""
    for repo in repos:
        repo["source"] = "aiven" if repo["owner"].lower().startswith("aiven") else "community"
    return repos


def topic_counts(repos: list[dict]) -> list[dict]:
    """Distinct topics across all repos, with how many repos use each one --
    used to render the topics filter. Aiven-service topics (those with an
    official Aiven icon, see ``icons.AIVEN_SERVICE_ICONS``) are grouped
    first, everything else after; both groups are alphabetical."""
    counts = Counter(topic for repo in repos for topic in repo.get("topics", []))
    return [
        {"name": name, "count": count}
        for name, count in sorted(
            counts.items(), key=lambda item: (item[0] not in AIVEN_SERVICE_TOPICS, item[0])
        )
    ]


repos = mark_source(load_repos())


@app.page
class Index(Page):
    template = "index.html"
    template_vars = {"repos": repos, "topics": topic_counts(repos)}


@app.collection
class Pages(Collection):
    """Static informational pages, e.g. content/pages/contribute.md -> /contribute."""

    content_path = "content/pages"
    template = "page.html"
    Parser = MarkdownPageParser
    parser_extras = {"markdown_extras": ["fenced-code-blocks", "tables"]}
    routes = ["./"]


if __name__ == "__main__":
    app.render()
