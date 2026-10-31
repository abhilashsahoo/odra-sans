#!/usr/bin/env bash
# Build Odra Sans Pro: variable + static TTF (ttfautohint + gasp) + WOFF2
set -euo pipefail
cd "$(dirname "$0")/.."
FM="fontmake --filter DecomposeTransformedComponentsFilter --filter FlattenComponentsFilter"

rm -rf fonts/variable fonts/ttf fonts/webfonts sources/instance_ufos
mkdir -p fonts/variable fonts/ttf fonts/webfonts

echo "==> Generating italic masters from upright UFOs"
python3 scripts/oblique.py

echo "==> Variable fonts (wght axis; ital via paired roman/italic files + STAT)"
$FM -m sources/OdraSansPro.designspace        -o variable \
  --output-path "fonts/variable/OdraSansPro[wght].ttf"
$FM -m sources/OdraSansPro-Italic.designspace -o variable \
  --output-path "fonts/variable/OdraSansPro-Italic[wght].ttf"

echo "==> Static instances"
$FM -m sources/OdraSansPro.designspace        -i -o ttf --output-dir fonts/ttf
$FM -m sources/OdraSansPro-Italic.designspace -i -o ttf --output-dir fonts/ttf
rm -rf sources/instance_ufos

echo "==> STAT for variable pair (ital linked)"
(cd fonts/variable && gftools gen-stat --inplace \
  "OdraSansPro[wght].ttf" "OdraSansPro-Italic[wght].ttf")

echo "==> gftools fix-font"
for f in fonts/variable/*.ttf fonts/ttf/*.ttf; do
  gftools fix-font -o "$f" "$f"
done

echo "==> ttfautohint (static TTFs only; improves screen rendering)"
# qsq = quality stem-width mode for horizontal/vertical/diagonal
for f in fonts/ttf/*.ttf; do
  python3 -m ttfautohint \
    --stem-width-mode=qsq \
    --hinting-limit=50 \
    --hinting-range-min=8 \
    --hinting-range-max=50 \
    --increase-x-height=14 \
    "$f" "$f.h"
  mv "$f.h" "$f"
done

echo "==> Name tables, GDEF, STAT (statics), meta, gasp"
python3 scripts/postprocess.py

echo "==> WOFF2"
for f in fonts/variable/*.ttf fonts/ttf/*.ttf; do
  fonttools ttLib.woff2 compress \
    -o "fonts/webfonts/$(basename "${f%.ttf}").woff2" "$f"
done

echo "==> Sanity: no Figtree in style names; files present"
python3 - <<'PY'
from fontTools.ttLib import TTFont
import glob, sys
bad = []
for p in glob.glob('fonts/**/*.ttf', recursive=True):
    f = TTFont(p)
    for r in f['name'].names:
        if r.nameID in (0, 13):
            continue
        s = r.toUnicode()
        if 'Figtree' in s or 'figtree' in s:
            bad.append((p, r.nameID, s))
    if 'gasp' not in f:
        bad.append((p, 'gasp', 'missing'))
if bad:
    print('FAIL', bad); sys.exit(1)
print('ok:', len(glob.glob('fonts/ttf/*.ttf')), 'static TTFs,',
      len(glob.glob('fonts/variable/*.ttf')), 'variable,',
      len(glob.glob('fonts/webfonts/*.woff2')), 'woff2')
PY

echo "Build complete (Odra Sans Pro ${ODRA_PRO_VERSION:-0.100})."
