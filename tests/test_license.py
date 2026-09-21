import httpx
import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

import github


@pytest.mark.parametrize('metadata,expected', [
    ({'spdx_id': 'MIT', 'name': 'MIT License'}, 'MIT License'),
    ({'spdx_id': 'NOASSERTION', 'name': 'Other'}, 'License present (type not identified)'),
    (None, ''),
])
def test_license_metadata_and_rendering(monkeypatch, metadata, expected):
    def fake_get(self, url, **kwargs):
        return httpx.Response(200, json={'license': metadata}, request=httpx.Request('GET', url))
    monkeypatch.setattr(httpx.Client, 'get', fake_get)
    repo = github.enrich_manifest([{'name': 'Example', 'owner': 'org', 'repo': 'app'}])[0]
    assert repo['license_name'] == expected
    html = Environment(loader=FileSystemLoader('templates'), autoescape=select_autoescape()).get_template('index.html').render(repos=[repo], topics=[])
    if expected:
        actions = html.split('<div class="repo-actions">', 1)[1].split('</div>', 1)[0]
        assert 'class="repo-license"' in actions
        assert 'class="repo-license"' not in html.split('<div class="repo-meta">', 1)[0]
        assert 'href="https://github.com/org/app#license"' in html
        assert f'aria-label="Repository license: {expected}"' in html
    else:
        assert 'class="repo-license"' not in html


def test_failed_lookup_does_not_claim_missing_license(monkeypatch):
    monkeypatch.setattr(github, 'fetch_repo_info', lambda *args, **kwargs: {})
    repo = github.enrich_manifest([{'name': 'Example', 'owner': 'org', 'repo': 'app'}])[0]
    assert repo['license_name'] == ''
