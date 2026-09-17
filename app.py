"""
Render Engine app for the Aiven Runtime repo directory.

Build with:
    uv run python app.py
or:
    uv run render-engine build app:app
"""

import json
from pathlib import Path

from render_engine import Collection, Page, Site
from render_engine_markdown import MarkdownPageParser

from github import enrich_manifest

MANIFEST_PATH = Path("data/manifest.json")

app = Site(output_path="output", static_paths={"static"})
app.site_vars.update(
    {"SITE_TITLE": "Runs on Runtime", "SITE_URL": "https://templates.aiven.io"}
)


def load_repos() -> list[dict]:
    manifest = json.loads(MANIFEST_PATH.read_text())
    return enrich_manifest(manifest)


@app.page
class Index(Page):
    template = "index.html"
    template_vars = {"repos": load_repos()}


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
