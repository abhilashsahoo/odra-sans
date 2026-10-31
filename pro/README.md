# Odra Sans Pro

**Version 0.100** (development / initial scaffold)

Odra Sans Pro is the expanded Pro line of [Odra Sans](../README.md). This
`pro/` tree is self-contained: sources, build scripts and outputs live here
and do **not** rebuild or replace the existing Odra Sans release under
`fonts/` / `sources/` at the repo root.

## Status (0.100)

| Item | Status |
|---|---|
| Family rename → Odra Sans Pro | Done |
| Weights 300–900 + matching italics | Done (from Odra Sans masters) |
| Thin (100) / ExtraLight (200) | **Design step** — not shipped (see below) |
| Variable font `wght` + ital pair | Done |
| Static TTF + WOFF2 | Done |
| ttfautohint + gasp | Done |
| Specimen HTML | `documentation/specimen.html` |

## Thin & ExtraLight

Figtree’s variable source (and Odra Sans) only covers **300–900**, with
masters at Light and Black. Extrapolating below Light is not reproducible
at release quality (distorted outlines / collapsing counters). Shipping
Thin and ExtraLight means:

1. Draw a Thin upright master (and ideally ExtraLight, or interpolate 200
   once 100 and 300 exist).
2. Run `scripts/oblique.py` to regenerate italics.
3. Set the designspace `wght` minimum to `100`, add maps/instances, rebuild.

Until that design work lands, the Pro axis stays **300–900**.

## Build

Python 3.10+. From this directory:

```bash
make build      # venv + scripts/build.sh → fonts/{variable,ttf,webfonts}
make test       # Font Bakery on variable fonts (optional)
```

Or:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
./scripts/build.sh
```

Outputs:

| Path | Contents |
|---|---|
| `fonts/variable/` | `OdraSansPro[wght].ttf`, `OdraSansPro-Italic[wght].ttf` |
| `fonts/ttf/` | Static hinted TTFs |
| `fonts/webfonts/` | WOFF2 (static + variable) |

### Hinting

Static TTFs are passed through **ttfautohint** (`--stem-width-mode=qsq`).
`scripts/postprocess.py` writes a **gasp** table:

- ≤8 ppem: symmetric gridfit + smoothing  
- ≤16 and above: gridfit + grayscale + symmetric modes  

Variable fonts are not autohinted (standard for VFs); gasp is still set.

### Italic / slant

Pro follows the Odra Sans approach: a **true italic** (italic mods + 9.5°
shear) as a second variable font, linked with a STAT **ital** axis (roman
`linkedValue` → italic). There is no `slnt` axis in 0.100; a slant axis
could be added later if a continuous oblique is desired alongside the
true italic.

## Web use

```css
@font-face {
  font-family: "Odra Sans Pro";
  src: url("fonts/webfonts/OdraSansPro[wght].woff2") format("woff2");
  font-weight: 300 900;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Odra Sans Pro";
  src: url("fonts/webfonts/OdraSansPro-Italic[wght].woff2") format("woff2");
  font-weight: 300 900;
  font-style: italic;
  font-display: swap;
}
```

Open `documentation/specimen.html` after a build to preview every weight.

## License

SIL Open Font License 1.1 — see [OFL.txt](OFL.txt). Copyright includes The
Figtree Project Authors (required credit) and The Odra Sans Pro Project
Authors. See [FONTLOG.txt](FONTLOG.txt).
