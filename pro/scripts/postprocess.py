"""Post-build name-table, GDEF, STAT, meta, and gasp fixes for Odra Sans Pro."""
import glob
import re
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont, newTable

FAMILY = 'Odra Sans Pro'
PS = 'OdraSansPro'
VERSION = '0.100'
VENDOR = 'INFY'

# Weights currently shipped (Thin/ExtraLight deferred — need masters).
W = {
    'Thin': 100,
    'ExtraLight': 200,
    'Light': 300,
    '': 400,
    'Regular': 400,
    'Medium': 500,
    'SemiBold': 600,
    'Bold': 700,
    'ExtraBold': 800,
    'Black': 900,
}

# gasp: enable gridfit + grayscale + symmetric modes for all ppem (screen TTFs).
# Values: bit0 GRIDFIT, bit1 DOGRAY, bit2 SYMMETRIC_GRIDFIT, bit3 SYMMETRIC_SMOOTHING.
GASP_RANGE = {
    8: 0x0A,      # ≤8 ppem: symmetric gridfit + smoothing (no classic gridfit)
    16: 0x0F,     # ≤16: all
    65535: 0x0F,  # larger: all
}

LEG = (
    'grave dieresis macron acute cedilla circumflex caron breve '
    'dotaccent ring ogonek tilde hungarumlaut'
).split()


def set_gasp(font):
    gasp = newTable('gasp')
    gasp.version = 1
    gasp.gaspRange = dict(GASP_RANGE)
    font['gasp'] = gasp


def fix_newlines(font):
    n = font['name']
    for r in n.names:
        s = r.toUnicode()
        if '\n' in s:
            r.string = s.replace('\n', ' ')


def fix_gdef(font):
    if 'GDEF' not in font:
        return
    cd = font['GDEF'].table.GlyphClassDef.classDefs
    for g in LEG:
        if cd.get(g) == 3:
            cd[g] = 1


def ensure_no_figtree_in_names(font):
    for r in font['name'].names:
        s = r.toUnicode()
        # Allow Figtree only in copyright / license notice strings (name IDs 0, 13).
        if r.nameID in (0, 13):
            continue
        if 'Figtree' in s or 'figtree' in s:
            raise SystemExit(f'Figtree leaked into name ID {r.nameID}: {s!r}')


paths = glob.glob('fonts/variable/*.ttf') + glob.glob('fonts/ttf/*.ttf')
for p in paths:
    f = TTFont(p)
    fix_newlines(f)
    fix_gdef(f)
    # Variable italic default-name quirk from fontmake (Light Italic as name ID 1/2).
    if 'Italic[' in p.replace('\\', '/'):
        n = f['name']
        for i, v in (
            (1, f'{FAMILY} Light'),
            (2, 'Italic'),
            (3, f'{VERSION};{VENDOR};{PS}-LightItalic'),
            (4, f'{FAMILY} Light Italic'),
            (6, f'{PS}-LightItalic'),
            (16, FAMILY),
            (17, 'Light Italic'),
        ):
            n.setName(v, i, 3, 1, 0x409)
    set_gasp(f)
    ensure_no_figtree_in_names(f)
    f.save(p)

# Static italics: style-linking bits and RIBBI names
for p in glob.glob('fonts/ttf/*Italic.ttf'):
    f = TTFont(p)
    n = f['name']
    st = re.search(r'-(\w*)Italic', p).group(1)
    os2 = f['OS/2']
    os2.fsSelection = (os2.fsSelection | 1) & ~(1 << 6)
    bold = st == 'Bold'
    f['head'].macStyle = 2 | (1 if bold else 0)
    if bold:
        os2.fsSelection |= 32
    else:
        os2.fsSelection &= ~32
    fam = FAMILY if st in ('', 'Bold') else f'{FAMILY} {st}'
    n.setName(fam, 1, 3, 1, 0x409)
    n.setName('Bold Italic' if bold else 'Italic', 2, 3, 1, 0x409)
    if st in ('', 'Bold'):
        n.removeNames(nameID=16)
        n.removeNames(nameID=17)
    else:
        n.setName(FAMILY, 16, 3, 1, 0x409)
        n.setName(f'{st} Italic', 17, 3, 1, 0x409)
    set_gasp(f)
    ensure_no_figtree_in_names(f)
    f.save(p)

# STAT for statics
for p in glob.glob('fonts/ttf/*.ttf'):
    f = TTFont(p)
    st = re.search(r'-(\w+)\.ttf', p).group(1)
    it = st.endswith('Italic')
    wn = st.replace('Italic', '')
    w = W[wn]
    buildStatTable(
        f,
        [
            {
                'tag': 'wght',
                'name': 'Weight',
                'values': [
                    {
                        'value': w,
                        'name': wn or 'Regular',
                        'flags': 2 if w == 400 else 0,
                    }
                ],
            },
            {
                'tag': 'ital',
                'name': 'Italic',
                'values': [
                    {'value': 1, 'name': 'Italic'}
                    if it
                    else {'value': 0, 'name': 'Roman', 'flags': 2, 'linkedValue': 1}
                ],
            },
        ],
        elidedFallbackName=2,
    )
    f.save(p)

# meta + gasp + force ppem-to-integer bit when instructed
for p in glob.glob('fonts/variable/*.ttf') + glob.glob('fonts/ttf/*.ttf'):
    f = TTFont(p)
    m = newTable('meta')
    m.data = {'dlng': 'Latn', 'slng': 'Latn'}
    f['meta'] = m
    set_gasp(f)
    if p.startswith('fonts/ttf') and 'fpgm' in f:
        f['head'].flags |= 1 << 3
    ensure_no_figtree_in_names(f)
    # Unique ID / version strings should say OdraSansPro and 0.100 where present
    n = f['name']
    for r in list(n.names):
        if r.platformID != 3 or r.langID != 0x409:
            continue
        s = r.toUnicode()
        if r.nameID == 5 and '0.100' not in s and 'Version' in s:
            n.setName(f'Version {VERSION}', 5, 3, 1, 0x409)
        if r.nameID == 3 and 'OdraSans;' in s:
            n.setName(s.replace('OdraSans;', f'{PS};'), 3, 3, 1, 0x409)
        if r.nameID in (1, 4, 16) and s == 'Odra Sans':
            n.setName(FAMILY if r.nameID != 4 else f'{FAMILY} Regular', r.nameID, 3, 1, 0x409)
    f.save(p)

print('postprocess complete')
