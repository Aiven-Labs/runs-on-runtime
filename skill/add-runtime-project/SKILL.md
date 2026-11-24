---
name: add-runtime-project
description: |
  Add a project entry to the Runs on Runtime directory at
  ~/projects/runs-on-runtime (data/manifest.json). Use when asked to "add a
  project to runs on runtime", "add my repo to the runtime directory", "list
  this on runs-on-runtime", or similar. Validates the entry against the
  manifest schema, appends it to data/manifest.json, and builds the site
  locally to confirm it renders before committing.
allowed-tools:
  - Read
  - Edit
  - Bash
  - AskUserQuestion
---

# Add a Project to Runs on Runtime

Adds one entry to `data/manifest.json` in
`~/projects/runs-on-runtime`, per that repo's `CONTRIBUTING.md`.

## 1. Gather the fields

Required:

- `name` — display name for the card.
- `owner` — GitHub owner/org.
- `repo` — GitHub repo name.
- `added` — the date the entry was added, as `YYYY-MM-DD`. Use today's date;
  the build (`schema.py`'s `validate_manifest`) rejects entries missing this
  field.

Optional:

- `description` — overrides the GitHub repo description.
- `logo` — path or URL. If it's a local image, it must be added under
  `static/images/` in that repo.
- branch - sets the branch that is meant to be used for deploying with aiven runtime - main by default

If the user gives a bare GitHub URL or `owner/repo`, derive `owner`/`repo`
from it and use the repo name (title-cased) as a default `name` — confirm the
name with the user rather than guessing silently if it's ambiguous.

Ask with AskUserQuestion only for what's actually missing or ambiguous
(e.g. `name` when only a URL was given); don't ask about fields the user
already supplied.

## 2. Sanity-check the repo (optional but preferred)

If `GITHUB_TOKEN` is available, or unauthenticated rate limits allow it, a
quick check that `owner/repo` exists is worthwhile:

```bash
curl -s -o /dev/null -w "%{http_code}" "https://api.github.com/repos/$OWNER/$REPO"
```

A `404` means the repo/owner is wrong — surface that to the user instead of
adding a dead entry. Don't block on this if the API is unreachable; just note
it wasn't verified.

## 3. Edit the manifest

Read `runs-on-runtime/data/manifest.json` from the local repo. use Edit to append
a new object to the JSON array, matching this shape (only include the
optional keys that were actually given):

```json
{
  "name": "My Cool App",
  "owner": "my-github-username",
  "repo": "my-cool-app",
  "added": "2026-09-18",
  "description": "Optional — overrides the GitHub repo description",
  "logo": "/static/images/my-cool-app.png"
}
```

Keep existing entries and formatting untouched — this is a pure append.
After editing, confirm the file still parses as valid JSON:

```bash
python3 -c "import json; json.load(open('/PATH/TO/PROJECT/runs-on-runtime/data/manifest.json'))"
```

## 4. Build locally to confirm it renders

```bash
cd /Users/kjaymiller/projects/runs-on-runtime && uv run python app.py
```

This enriches the manifest via the GitHub API and builds into `output/`. A
build error usually means a typo in `owner`/`repo` or malformed JSON — fix and
re-run before moving on.

## 5. Commit

This repo's default branch is `main`; branch before committing, per the
CONTRIBUTING flow:

```bash
cd /Users/kjaymiller/projects/runs-on-runtime
git checkout -b add-<repo-slug>
git commit -am "Add <name> to the directory"
```

Don't push or open the PR unless the user asks — confirm the branch/commit
with them first since this touches a repo other than the one the session
started in.

## Notes

- There's no `template_url` field — template-repo status is detected
  automatically at build time via the GitHub API.
- Never fabricate a `description` or `logo` if the user didn't give one and
  you can't verify it — leave the key out and let it fall back (GitHub
  description / owner avatar).
