---
title: Contribute
---

## Add your project

This directory is generated from [`data/manifest.json`](https://github.com/aiven-labs/runs-on-runtime/blob/main/data/manifest.json).
Adding your repo means adding one entry to that JSON array and opening a PR.

### 1. Edit the manifest

The fastest way is to use GitHub's web editor, which will fork the repo and
open a PR for you automatically:

[Edit `data/manifest.json` on GitHub](https://github.com/aiven-labs/runs-on-runtime/edit/main/data/manifest.json)

Or, working locally:

```bash
git clone https://github.com/aiven-labs/runs-on-runtime
cd runs-on-runtime
$EDITOR data/manifest.json
git checkout -b add-my-project
git commit -am "Add my-project to the directory"
git push origin add-my-project
```
Then open a PR from your branch.

### 2. The schema

Each entry only needs `name`, `owner`, and `repo` — everything else is
optional and falls back to data pulled from the GitHub API at build time
(description, owner avatar as logo, and whether the repo is a template).

```json
{
  "name": "My Cool App",
  "owner": "my-github-username",
  "repo": "my-cool-app",
  "description": "Optional — overrides the GitHub repo description",
  "logo": "/static/images/my-cool-app.png"
}
```

- **name** — display name for the card.
- **owner** / **repo** — the GitHub owner and repo name (used to build the
  link and to look up the repo via the GitHub API).
- **description** *(optional)* — overrides the repo's GitHub description.
- **logo** *(optional)* — path or URL to a logo image. If omitted, the
  owner's GitHub avatar is used instead. To add a local image, drop it in
  `static/images/` and reference it as `/static/images/your-file.png`.

There's no `template_url` field — if your repo is marked as a
[GitHub template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository),
that's detected automatically and a "Use this template" link is added to
your card.

### 3. Open the PR

That's it — once the PR merges, the next build will pick up your entry.
