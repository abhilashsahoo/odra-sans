import glob
from fontTools.ttLib import TTFont
LEG='grave dieresis macron acute cedilla circumflex caron breve dotaccent ring ogonek tilde hungarumlaut'.split()
for p in glob.glob('fonts/variable/*.ttf')+glob.glob('fonts/ttf/*.ttf'):
    f=TTFont(p); n=f['name']
    for r in n.names:
        s=r.toUnicode()
        if '\n' in s: r.string=s.replace('\n',' ')
    cd=f['GDEF'].table.GlyphClassDef.classDefs
    for g in LEG:
        if cd.get(g)==3: cd[g]=1
    if 'Italic[' in p:
        for i,v in ((1,'Odra Sans Light'),(2,'Italic'),(3,'1.000;UKWN;OdraSans-LightItalic'),(4,'Odra Sans Light Italic'),(6,'OdraSans-LightItalic'),(16,'Odra Sans'),(17,'Light Italic')):
            n.setName(v,i,3,1,0x409)
    f.save(p)
# static italics: fix style-linking bits and RIBBI names
import re
for p in glob.glob('fonts/ttf/*Italic.ttf'):
    f=TTFont(p); n=f['name']; st=re.search(r'-(\w*)Italic',p).group(1)
    os2=f['OS/2']; os2.fsSelection=(os2.fsSelection|1)&~(1<<6)
    bold=st=='Bold'; f['head'].macStyle=2|(1 if bold else 0)
    if bold: os2.fsSelection|=32
    else: os2.fsSelection&=~32
    fam='Odra Sans' if st in('','Bold') else f'Odra Sans {st}'
    n.setName(fam,1,3,1,0x409); n.setName('Bold Italic' if bold else 'Italic',2,3,1,0x409)
    if st in('','Bold'): n.removeNames(nameID=16); n.removeNames(nameID=17)
    else: n.setName('Odra Sans',16,3,1,0x409); n.setName(f'{st} Italic',17,3,1,0x409)
    f.save(p)
# STAT for statics + meta table everywhere
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import newTable
W={'Light':300,'':400,'Regular':400,'Medium':500,'SemiBold':600,'Bold':700,'ExtraBold':800,'Black':900}
for p in glob.glob('fonts/ttf/*.ttf'):
    f=TTFont(p); st=re.search(r'-(\w+)\.ttf',p).group(1); it=st.endswith('Italic'); wn=st.replace('Italic','')
    w=W[wn]
    buildStatTable(f,[{'tag':'wght','name':'Weight','values':[{'value':w,'name':wn or 'Regular','flags':2 if w==400 else 0}]},
        {'tag':'ital','name':'Italic','values':[{'value':1,'name':'Italic'} if it else {'value':0,'name':'Roman','flags':2,'linkedValue':1}]}],
        elidedFallbackName=2)
    f.save(p)
for p in glob.glob('fonts/variable/*.ttf')+glob.glob('fonts/ttf/*.ttf'):
    f=TTFont(p); m=newTable('meta'); m.data={'dlng':'Latn','slng':'Latn'}; f['meta']=m; f.save(p)
for p in glob.glob('fonts/ttf/*.ttf'):
    f=TTFont(p)
    if 'fpgm' in f: f['head'].flags|=1<<3; f.save(p)
