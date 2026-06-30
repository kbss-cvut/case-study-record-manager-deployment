# `.dev/` — optional development compose overrides

Small, single-purpose `docker compose` override files you opt into on top of the dev
stack. Each one does exactly one thing; combine the ones you need by stacking `-f` flags.
File naming: `dc-<service>--<purpose>.yml`.

Compose them after the base + dev files, e.g.:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  -f .dev/dc-media-asset-annotator--allow-external.yml \
  --env-file .env up -d
```

(Paths are relative to the repo root, so run `docker compose` from there.)

## Available overrides

| File | What it does |
|---|---|
| `dc-media-asset-annotator--allow-external.yml` | Adds the host Vite dev/preview origins (`localhost:5173`, `localhost:4173`) to `media-asset-annotator-server` CORS, so a host-run annotator frontend can call the dockerized backend. |
| `dc-media-asset-annotator-server--debug.yml` | Enables JVM remote debugging on `media-asset-annotator-server` (attach to `127.0.0.1:${JAVA_DEBUG_ANNOTATOR_SERVER_PORT:-5006}`). |
| `dc-media-asset-annotator-server--custom-image.yml` | Replaces the `media-asset-annotator-server` image with a custom one (e.g. a per-PR ghcr.io build, tag `pr-<N>`), taken from `$ANNOTATOR_SERVER_CUSTOM_IMAGE`. Aborts if that variable is blank, so it never silently falls back to `:latest`. Pass the variable on the command line — keep it out of `.env`. Run `make dev` to revert. |
| `dc-keycloak-config--minimal-lifespan.yml` | Sets the Keycloak access token lifespan to `1s` to test token expiry/refresh and role/group change propagation without waiting 5m. |

Overrides that need a variable (e.g. `dc-media-asset-annotator-server--custom-image.yml`) take
it as an inline prefix, scoped to that single command — no `export`, nothing added to `.env`:

```bash
ANNOTATOR_SERVER_CUSTOM_IMAGE=ghcr.io/kbss-cvut/media-asset-annotator-server:pr-5 \
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  -f .dev/dc-media-asset-annotator-server--custom-image.yml \
  --env-file .env up -d
```

## Candidate overrides (not yet created)

- `dc-record-manager-server--debug.yml` / `dc-record-manager-statistics-server--debug.yml` /
  `dc-s-pipes-engine--debug.yml` — same JVM remote-debug pattern for the other Spring services.
- `dc-record-manager-statistics--allow-external.yml` — host-run statistics frontend CORS
  (the statistics server already lists `localhost:5173` in `docker-compose.dev.yml`; this would
  formalize it as an opt-in like the annotator one).
- `dc-*-server--hot-reload.yml` — bind-mount/`develop.watch` live reload; requires a
  `Dockerfile.dev` and local checkout of the corresponding source repo.
- `dc-*-server--substitute.yml` — swap an upstream image for a locally built one
  (see record-manager-ui's `.dev/dc-record-manager-server--substitute` for the pattern).
