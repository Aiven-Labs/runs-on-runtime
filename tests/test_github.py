"""Tests for github.py's manifest enrichment, in particular the `branch`
field, since it's derived entirely from the manifest and never touches the
GitHub API.

Every test stubs ``httpx.Client.get`` so nothing hits the real network.
"""

import httpx

import github
import icons


def _stub_get(monkeypatch, payload: dict, status_code: int = 200):
    """Replace httpx.Client.get with one that returns `payload` and records
    every URL it was called with."""
    seen_urls = []

    def fake_get(self, url, headers=None):
        seen_urls.append(url)
        return httpx.Response(status_code, json=payload, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    return seen_urls


def test_repo_url_has_no_branch_by_default(monkeypatch):
    _stub_get(monkeypatch, {})
    entry = {"name": "Example", "owner": "octocat", "repo": "hello-world"}

    enriched = github.enrich_manifest([entry])[0]

    assert enriched["repo_url"] == "https://github.com/octocat/hello-world"
    assert enriched["fork_url"] == "https://github.com/octocat/hello-world/fork"


def test_branch_field_changes_repo_and_fork_urls(monkeypatch):
    _stub_get(monkeypatch, {})
    entry = {
        "name": "Example",
        "owner": "octocat",
        "repo": "hello-world",
        "branch": "aiven-runtime",
    }

    enriched = github.enrich_manifest([entry])[0]

    assert enriched["repo_url"] == (
        "https://github.com/octocat/hello-world/tree/aiven-runtime"
    )
    assert enriched["fork_url"] == (
        "https://github.com/octocat/hello-world/fork?ref=aiven-runtime"
    )


def test_branch_field_does_not_affect_github_lookup(monkeypatch, tmp_path):
    """The GitHub API is queried for the repo as a whole, not a specific
    ref -- description/topics/template status are branch-independent."""
    monkeypatch.setattr(icons, "DEVICON_CACHE_DIR", tmp_path / "devicon")
    seen_urls = _stub_get(
        monkeypatch,
        {
            "description": "from github",
            "owner": {"avatar_url": "https://example.com/avatar.png"},
            "is_template": True,
            "topics": ["python"],
            "homepage": "https://example.com",
        },
    )
    entry = {
        "name": "Example",
        "owner": "octocat",
        "repo": "hello-world",
        "branch": "aiven-runtime",
    }

    enriched = github.enrich_manifest([entry])[0]

    assert seen_urls == [
        "https://api.github.com/repos/octocat/hello-world",
        icons._devicon_url("python"),
    ]
    assert enriched["description"] == "from github"
    assert enriched["topics"] == ["python"]
    assert enriched["generate_url"] == "https://github.com/octocat/hello-world/generate"
    assert enriched["icons"] == ["/static/images/devicon/python.svg"]
    assert enriched["avatar"] == "https://example.com/avatar.png"


def test_manifest_values_win_over_github_data_regardless_of_branch(monkeypatch):
    _stub_get(monkeypatch, {"description": "from github"})
    entry = {
        "name": "Example",
        "owner": "octocat",
        "repo": "hello-world",
        "branch": "aiven-runtime",
        "description": "manifest wins",
    }

    enriched = github.enrich_manifest([entry])[0]

    assert enriched["description"] == "manifest wins"
    assert enriched["branch"] == "aiven-runtime"


def test_fetch_repo_info_falls_back_to_empty_dict_on_http_error(monkeypatch):
    def fake_get(self, url, headers=None):
        return httpx.Response(404, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)

    with httpx.Client() as client:
        info = github.fetch_repo_info("octocat", "does-not-exist", client=client)

    assert info == {}
