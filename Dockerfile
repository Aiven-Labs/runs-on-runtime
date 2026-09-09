# syntax=docker/dockerfile:1

# --- build stage: install deps with uv, build the static site with Render Engine ---
FROM python:3.14-slim AS build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install deps first so this layer is cached when only content/data changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .

# GITHUB_TOKEN is only needed at build time (to enrich manifest entries via
# the GitHub API) and is never baked into the final image. Pass it with
# `docker build --secret id=github_token,env=GITHUB_TOKEN ...` so it never
# lands in an image layer.
RUN --mount=type=secret,id=github_token \
  GITHUB_TOKEN="$(cat /run/secrets/github_token 2>/dev/null || true)" \
  uv run python app.py

# --- runtime stage: serve the built output/ with nginx ---
FROM nginx:alpine AS runtime

COPY --from=build /app/output /usr/share/nginx/html

EXPOSE 80
