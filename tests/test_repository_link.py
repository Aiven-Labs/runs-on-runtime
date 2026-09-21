import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape
import github


@pytest.mark.parametrize("branch", [None, "aiven-runtime"])
def test_attribution_links_to_the_same_repository_as_heading(monkeypatch, branch):
    monkeypatch.setattr(github, "fetch_repo_info", lambda *args, **kwargs: {})
    entry = {"name": "Example", "owner": "org", "repo": "app"}
    if branch:
        entry["branch"] = branch
    repo = github.enrich_manifest([entry])[0]
    html = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape()).get_template("index.html").render(repos=[repo], topics=[])
    url = "https://github.com/org/app" + ("/tree/aiven-runtime" if branch else "")
    assert f'class="name" href="{url}"' in html
    assert f'class="repo-footer" href="{url}" aria-label="View org/app on GitHub"' in html
