# Artlify Agency website

Live at https://artlifyagency.com, deployed by Netlify from this repository.

- `site/`: the published website (static HTML, CSS, JS, images). Netlify serves this folder.
- `generator/`: the source the site is built from. Copy is in `generator/content.py`; run `python3 generator/build.py netlify` to rebuild, then copy `generator/dist/` into `site/`.
- `netlify.toml`: tells Netlify to publish `site/` with no build step.
