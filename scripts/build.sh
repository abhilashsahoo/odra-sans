#!/usr/bin/env bash
# Build Odra Sans: variable + static TTF + WOFF2
set -euo pipefail
cd "$(dirname "$0")/.."
FM="fontmake --filter DecomposeTransformedComponentsFilter --filter FlattenComponentsFilter"
rm -rf fonts/variable fonts/ttf fonts/webfonts sources/instance_ufos
mkdir -p fonts/variable fonts/ttf fonts/webfonts
$FM -m sources/OdraSans.designspace        -o variable --output-path "fonts/variable/OdraSans[wght].ttf"
$FM -m sources/OdraSans-Italic.designspace -o variable --output-path "fonts/variable/OdraSans-Italic[wght].ttf"
$FM -m sources/OdraSans.designspace        -i -o ttf --output-dir fonts/ttf
$FM -m sources/OdraSans-Italic.designspace -i -o ttf --output-dir fonts/ttf
rm -rf sources/instance_ufos
(cd fonts/variable && gftools gen-stat --inplace "OdraSans[wght].ttf" "OdraSans-Italic[wght].ttf")
for f in fonts/variable/*.ttf fonts/ttf/*.ttf; do gftools fix-font -o "$f" "$f"; done
for f in fonts/ttf/*.ttf; do python3 -m ttfautohint "$f" "$f.h" && mv "$f.h" "$f"; done
python3 scripts/postprocess.py
for f in fonts/variable/*.ttf fonts/ttf/*.ttf; do
  fonttools ttLib.woff2 compress -o "fonts/webfonts/$(basename "${f%.ttf}").woff2" "$f"
done
echo "Build complete."
