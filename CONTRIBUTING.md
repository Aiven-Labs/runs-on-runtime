# Contributing

This site lists GitHub repos that run on [Aiven Runtime](https://aiven.io/runtime).
The list is generated from [`data/manifest.json`](data/manifest.json) — adding
your repo means adding one entry to that file and opening a PR. (The same
instructions are also on the site's [`/contribute`](content/pages/contribute.md) page.)

## 1. Edit the manifest

Quickest path — use GitHub's web editor, which forks the repo and opens a PR
form for you:

https://github.com/aiven-labs/runs-on-runtime/edit/main/data/manifest.json

Or locally:

```bash
git clone https://github.com/aiven-labs/runs-on-runtime
cd runs-on-runtime
$EDITOR data/manifest.json
git checkout -b add-my-project
git commit -am "Add my-project to the directory"
git push origin add-my-project
```

The manifest order controls the default **Recommended** order on the site. Preserve
existing entries' relative order when adding a repo; propose curated reordering in
a separate change. Visitors can also sort by name or date.

## 2. The schema

```json
{
  "name": "My Cool App",
  "owner": "my-github-username",
  "repo": "my-cool-app",
  "description": "Optional — overrides the GitHub repo description",
  "logo": "/static/images/my-cool-app.png"
}
```

| Field | Required | Notes |
|---|---|---|
| `name` | yes | Display name for the card. |
| `owner` | yes | GitHub owner/org of the repo. |
| `repo` | yes | GitHub repo name. |
| `description` | no | Falls back to the repo's GitHub description. |
| `logo` | no | Path or URL. Falls back to the owner's GitHub avatar. Local images go in `static/images/`. |
| `branch` | no | Points the card's links at a non-default branch instead of the repo's default branch. |

Set `branch` when your example only works from a branch other than the
default — e.g. it needs Aiven Runtime-specific changes that haven't landed
on `main` yet:

```json
{
  "name": "My Cool App",
  "owner": "my-github-username",
  "repo": "my-cool-app",
  "branch": "aiven-runtime"
}
```

This changes the card title link to
`github.com/owner/repo/tree/<branch>`, and the "Fork on GitHub" link to
`github.com/owner/repo/fork?ref=<branch>` so the fork starts from that
branch. It does not affect the GitHub API lookups (description, topics,
template detection) — those are always read from the repo as a whole,
regardless of branch.

There's no `template_url` field. If your repo is a
[GitHub template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository),
that's detected automatically at build time via the GitHub API (`is_template`
/ `template_repository`) and reflected on the card.

## 3. Open the PR

Once merged, the next build picks up your entry automatically.

## Local development

```bash
uv sync
uv run python app.py   # builds the static site into output/
```

Optionally set `GITHUB_TOKEN` in your environment to raise the GitHub API
rate limit used for the template/description lookups.
