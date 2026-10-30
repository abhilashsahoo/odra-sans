import ufoLib2, glob, math, re
from italic_mods import exit_tail, rot_round, TAILS, ROUND, f_descender
T2=math.tan(math.radians(6.5))
T=math.tan(math.radians(9.5))
for p in glob.glob('ufo/OdraSans-*.ufo'):
    if 'Italic' in p: continue
    f=ufoLib2.Font.open(p)
    for L in f.layers:
        for g in L:
            t=T
            if L is f.layers.defaultLayer and g.name in TAILS: exit_tail(g)
            if L is f.layers.defaultLayer and g.name=='f': f_descender(g)
            if g.name in ROUND: rot_round(g); t=T2
            for c in g.contours:
                for q in c.points: q.x=round(q.x+q.y*t)
            for a in g.anchors: a.x=round(a.x+a.y*T)
            for c in g.components:
                t=c.transformation; c.transformation=t._replace(dx=round(t.dx+t.dy*T))
    f.info.italicAngle=-9.5; f.info.styleName=(f.info.styleName+' Italic').replace('Regular Italic','Italic')
    f.info.postscriptSlantAngle=-9.5; f.info.styleMapStyleName='bold italic' if f.info.styleName=='Bold Italic' else 'italic'
    f.save(p.replace('.ufo','Italic.ufo'),overwrite=True)
s=open('ufo/OdraSans.designspace').read()
s=re.sub(r'(OdraSans-\w+)\.ufo',r'\1Italic.ufo',s)
s=re.sub(r'stylename="(\w+)"',lambda m:'stylename="%s Italic"'%m.group(1) if m.group(1)!='Regular' else 'stylename="Italic"',s)
s=re.sub(r'name="Odra Sans (\w+)',lambda m:'name="Odra Sans %s Italic'%m.group(1),s)
s=s.replace('OdraSans-RegularItalic','OdraSans-Italic')
open('ufo/OdraSans-Italic.designspace','w').write(s)
