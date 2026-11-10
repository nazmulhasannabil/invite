# Nabil & Risha

A single-file wedding invitation. Open `site/index.html` (with `site/img/` beside it).

## Run

```bash
cd site
python -m http.server 5180
```

Then open http://127.0.0.1:5180/

## Regenerate images

Source illustrations live in `public/photos/`. To rebuild the WebPs in `site/img/`:

```bash
python scripts/prep-images.py
```
