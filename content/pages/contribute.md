---
title: Contribute
---

## Add your project

This directory is generated from [`data/manifest.json`](https://github.com/aiven-labs/runs-on-runtime/blob/main/data/manifest.json).
Adding your repo means adding one entry to that JSON array and opening a PR.

### 1. Edit the manifest

Append your new template as the **last entry** in the `data/manifest.json` array,
just before the closing `]`. Add a comma after the previous entry and leave the
existing entries in their current order. This places your template at the bottom
of the site's default **Recommended** list. Propose any reordering separately.

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
- **branch** *(optional)* — points the card's links at a non-default branch,
  for example when your example needs Aiven Runtime-specific changes that
  haven't landed on the default branch yet:

  ```json
  {
    "name": "My Cool App",
    "owner": "my-github-username",
    "repo": "my-cool-app",
    "branch": "aiven-runtime"
  }
  ```

  This changes the card title link to
  `github.com/owner/repo/tree/<branch>`, and "Fork on GitHub" to
  `github.com/owner/repo/fork?ref=<branch>` so the fork starts from that
  branch. GitHub API-sourced data (description, topics, template detection)
  is unaffected, since that's always read from the repo as a whole.

There's no `template_url` field — if your repo is marked as a
[GitHub template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository),
that's detected automatically and a "Use this template" link is added to
your card.

### 3. Open the PR

That's it — once the PR merges, the next build will pick up your entry.
