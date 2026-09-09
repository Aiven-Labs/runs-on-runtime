# Runs on Runtime

A directory of GitHub repos that run on [Aiven Runtime](https://aiven.io/runtime) —
built with [Render Engine](https://render-engine.readthedocs.io/), a Python
static site generator.

Each entry lives in [`data/manifest.json`](data/manifest.json). At build time,
`app.py` enriches every entry with data from the GitHub API: description and
owner avatar as fallbacks, and whether the repo is (or was generated from) a
[GitHub template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository).

## Want to add your project?

See [CONTRIBUTING.md](CONTRIBUTING.md), or visit the `/contribute` page on
the deployed site.

## Local development

```bash
uv sync
uv run python app.py   # builds the static site into output/
```

Set `GITHUB_TOKEN` in your environment to raise the GitHub API rate limit
used for the enrichment lookups (optional).

## Docker

```bash
docker build -t runs-on-runtime --secret id=github_token,env=GITHUB_TOKEN .
docker run -p 8080:80 runs-on-runtime
```

`GITHUB_TOKEN` is only used at build time and is never baked into the image.
