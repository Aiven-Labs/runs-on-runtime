from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent.parent


def render_index(*, repos=None, topics=None):
    environment = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(),
    )
    return environment.get_template("index.html").render(
        repos=repos or [],
        topics=topics or [],
    )


def test_tracking_scripts_are_loaded_on_every_page():
    html = render_index()

    tracking_script = 'src="/static/js/tracking-setup.js"'
    site_tracking_script = 'src="/static/js/site-tracking.js"'

    assert html.index(tracking_script) < html.index(site_tracking_script)
    assert "cdn.cookielaw.org" not in html


def test_tracking_defaults_to_cookieless_anonymous_events():
    tracking = (ROOT / "static/js/tracking-setup.js").read_text()

    assert 'window.location.hostname !== "templates.aiven.io"' in tracking
    assert 'var COLLECTOR_URL = "https://dc.aiven.io"' in tracking
    assert 'var SNOWPLOW_APP_ID = "templates-aiven-io"' in tracking
    assert (
        'var ONETRUST_DOMAIN_SCRIPT = "01a11528-d2ee-7a99-9a30-01ce237f392b-test"'
        in tracking
    )
    assert "withServerAnonymisation: true" in tracking
    assert (
        'stateStorageStrategy: storedConsent ? "cookieAndLocalStorage" : "none"'
        in tracking
    )
    assert 'schema: "iglu:io.aiven/search/jsonschema/1-0-0"' in tracking
    assert 'window.snowplow("trackPageView")' in tracking

    site_tracking = (ROOT / "static/js/site-tracking.js").read_text()
    assert "window.aivenTracking.trackSearchTerm(query)" in site_tracking
    assert "window.aivenTracking.trackFilters(filters)" in site_tracking
    assert "var SEARCH_DEBOUNCE_MS = 500" in site_tracking


def test_catalog_controls_expose_tracking_metadata():
    template = {
        "name": "Example template",
        "owner": "aiven-labs",
        "repo": "example-template",
        "repo_url": "https://github.com/aiven-labs/example-template",
        "generate_url": "https://github.com/aiven-labs/example-template/generate",
        "fork_url": "https://github.com/aiven-labs/example-template/fork",
        "is_template": True,
        "description": "An example",
        "icons": [],
        "topics": ["kafka"],
        "avatar": None,
        "updated_at": "2026-10-01",
        "added_at": "2026-10-01",
        "source": "aiven",
    }
    repository = {
        **template,
        "name": "Example repository",
        "repo": "example-repository",
        "repo_url": "https://github.com/community/example-repository",
        "fork_url": "https://github.com/community/example-repository/fork",
        "is_template": False,
        "source": "community",
    }

    html = render_index(
        repos=[template, repository],
        topics=[{"name": "kafka", "count": 2}],
    )

    assert 'data-track-click="use template button"' in html
    assert 'data-track-click="fork button"' in html
    assert 'data-track-click="repository title"' in html
    assert 'data-track-click="repository attribution"' in html
    assert "data-track-filter" in html
    assert "data-track-filter-update" in html
    assert 'data-track-change="sort"' in html
    assert "data-track-search" in html
