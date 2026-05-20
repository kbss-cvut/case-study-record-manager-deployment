# MediaCMS deployment customisations

This directory layers two read-only file-lookup endpoints on top of the stock
`mediacms/mediacms:7.2` image, plus a few configuration tweaks. The
`Dockerfile` copies each Python file into `deploy/docker/` inside the image,
and `local_settings.py` decides which middleware classes are active per
profile (`dev` / `prod`).

The lookup endpoints both work by following the same pattern as the existing
`protected_media.py`: Django performs the auth check + DB lookup, then issues
an `X-Accel-Redirect` to `/protected-media/<rel_path>`, and nginx streams
the bytes from disk. There is no Django streaming overhead.

## `GET /by-md5/<md5>` — lookup by file hash

**Backed by**: `Media.md5sum` (populated automatically by MediaCMS during the
encoding/init phase of every upload — nothing you need to set).

**Middleware**: `by_md5.py` (registered in `prod_config()` of `local_settings.py`).

**How to use**:
```bash
curl -L -b "csrftoken=$CSRF; sessionid=$SID" \
     -o file.mp4 \
     "https://<host>/by-md5/759655317ae9dd06c56603a0bfb3156b"
```

The cookie pair is whatever a logged-in browser session has on
`<host>` — open DevTools → Application → Cookies after signing in.

**When to use it**: you already have the hash of a file on the client side
(via `md5sum somefile`) and want the bytes back without any prior knowledge of
MediaCMS's internal IDs. Useful for content-addressed pipelines.

**Limits**:
- `Media.md5sum` is not declared `unique=True`. If two media legitimately have
  the same hash, the middleware returns the oldest (`.first()`). This is a
  theoretical concern at the scale of dozens to thousands of uploads.
- `md5sum` has no DB index (it's "Not exposed, used internally" per the
  MediaCMS comment). For libraries growing past ~100k media you'd want an
  index, but that requires a Django migration and is out of scope here.
- The endpoint is only registered in **prod profile**. In dev mode it 404s,
  because `X-Accel-Redirect` requires nginx (the dev profile filters out the
  related `ProtectedMediaMiddleware` for the same reason).

## `GET /by-id/<friendly_token>` — lookup by persistent identifier

**Backed by**: `Media.friendly_token` (the same field MediaCMS uses for
`/view?m=...` and `/api/v1/media/<token>`).

**Middleware**: `by_id.py` (registered in `prod_config()` of `local_settings.py`).

### Default behaviour

If you upload a media and never touch its `friendly_token`, MediaCMS
auto-generates an 8-character token at save time (e.g. `9aP2SRmpL`). `/by-id/9aP2SRmpL` will work out of the box, but the slug is opaque and changes
on each upload — fine as a stable handle, useless as a deterministic key
derived from your own data.

### Assigning your own persistent identifier (PID)

This requires `ALLOW_CUSTOM_MEDIA_URLS=True` (set in both `dev_config()` and
`prod_config()` of `local_settings.py`). Without that setting, the
`friendly_token` field is silently stripped from MediaCMS's edit form and
your PID cannot be applied.

The `/fu/upload/` endpoint **does not** accept a custom PID — its form
fields are hard-coded to the Fine Uploader protocol. So the assignment is a
two-step flow:

1. Upload the file normally → MediaCMS returns the auto-generated
   `friendly_token` in the response (`{"success": true, "media_url":
   "/view?m=<auto-token>"}`).
2. POST to `/edit?m=<auto-token>` with `friendly_token=<your-pid>` plus
   the media's existing `title`, `description`, `add_date` (the form is a
   full-replace `ModelForm`; missing fields wipe the existing values).

```bash
curl -X POST "https://<host>/edit?m=<auto-token>" \
     -H "Cookie: csrftoken=$CSRF; sessionid=$SID" \
     -H "X-CSRFToken: $CSRF" \
     -H "Referer: https://<host>/edit?m=<auto-token>" \
     --data-urlencode "csrfmiddlewaretoken=$CSRF" \
     --data-urlencode "title=<keep existing>" \
     --data-urlencode "friendly_token=1glfZ_S5kX5XyyX7M-JtZIYtriP7aJHfZQA1oEmEiCUI" \
     -w "%{http_code}\n" -o /dev/null
```

`302` redirect = success. `200` with form HTML = validation failure (slug
illegal, or already in use).

After step 2 the media is reachable at `/by-id/<your-pid>`,
`/api/v1/media/<your-pid>` and `/view?m=<your-pid>`. The old auto-token
becomes a dead URL.

### Limits

- **Character set**: `[A-Za-z0-9_-]+`, max 150 chars. Enforced by
  `MediaMetadataForm.clean_friendly_token`. URIs containing `/`, `:`, `.`
  etc. cannot be stored verbatim — you'd have to encode (e.g. base32) on
  the client side. Google-Drive-style IDs (`1glfZ_S5kX5XyyX7M-JtZIYtriP7aJHfZQA1oEmEiCUI`) pass natively.
- **Uniqueness**: enforced by the DB unique constraint + the form. Reusing a
  PID returns HTTP 200 with the form re-rendered.
- **Public visibility**: `friendly_token` is also the slug rendered into
  `/view?m=<...>` URLs. Don't use a PID that contains anything sensitive.
- **No effect on uploads that don't opt in**: if you never run step 2 above,
  uploads keep getting MediaCMS's auto-generated 8-char tokens. Existing
  media are not migrated or renamed.

## Auth model

Both endpoints require `request.user.is_authenticated` and redirect
unauthenticated requests to login (mirrors `protected_media.py`). The
underlying file lives under `/media_files/...` and would normally be
inaccessible — nginx only serves it through the internal
`/protected-media/` alias declared in `nginx.conf`, which only Django can
trigger via `X-Accel-Redirect`. Drop the `is_authenticated` check in the
middleware if you want a public read.

## File map

| File | Purpose |
|---|---|
| `Dockerfile` | Extends `mediacms/mediacms:7.2`; COPYs the files below into the image's `deploy/docker/` |
| `local_settings.py` | Per-profile (`dev`/`prod`) overrides — registers middleware, sets `ALLOW_CUSTOM_MEDIA_URLS=True`, OIDC, RBAC, etc. |
| `nginx.conf` | Declares the internal `/protected-media/` alias that backs the lookup endpoints |
| `protected_media.py` | Middleware that auth-checks `/media/` and rewrites to `/protected-media/` |
| `by_md5.py` | Middleware backing `/by-md5/<md5>` |
| `by_id.py` | Middleware backing `/by-id/<friendly_token>` |
| `oidc_adapter.py`, `dev_auth.py` | Identity-provider plumbing (orthogonal to the lookup endpoints) |
