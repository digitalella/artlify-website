# Artlify Agency website

Live at https://artlifyagency.com, deployed by Cloudflare (Workers static assets) from this repository on every push to `main`.

- `site/`: the published website (static HTML, CSS, JS, images). Cloudflare serves this folder.
- `generator/`: the source the site is built from. Copy is in `generator/content.py`; run `python3 generator/build.py netlify` to rebuild, then copy `generator/dist/` into `site/`.
- `wrangler.jsonc`: tells Cloudflare to serve `site/` with the custom 404 page.
