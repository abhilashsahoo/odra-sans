# Generate italic masters from upright sources: true-italic redraws, optical correction, then shear.
import ufoLib2, glob, math, re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from italic_mods import exit_tail, rot_round, TAILS, ROUND, f_descender, V12, sync_composite_widths
T2=math.tan(math.radians(6.5)); T=math.tan(math.radians(9.5))
for p in sorted(glob.glob('sources/OdraSans-*.ufo')):
    if 'Italic' in p: continue
    f=ufoLib2.Font.open(p)
    for L in f.layers:
        deltas={}
        if L is f.layers.defaultLayer:
            for g in L:
                w0=g.width
                if g.name in TAILS: exit_tail(g)
                if g.name=='f': f_descender(g)
                if g.name in V12: V12[g.name](g)
                if g.width!=w0: deltas[g.name]=g.width-w0
            # propagate to composites (twice for nested: i -> iacute etc.)
            pending=deltas
            while pending:
                before={g.name:g.width for g in L}; sync_composite_widths(L,pending)
                pending={n:L[n].width-before[n] for n in before if L[n].width!=before[n]}
        for g in L:
            t=T
            if g.name in ROUND: rot_round(g); t=T2
            for c in g.contours:
                for q in c.points: q.x=round(q.x+q.y*t)
            for a in g.anchors: a.x=round(a.x+a.y*T)
            for c in g.components:
                tr=c.transformation; c.transformation=tr._replace(dx=round(tr.dx+tr.dy*T))
    f.info.italicAngle=-9.5; f.info.styleName=(f.info.styleName+' Italic').replace('Regular Italic','Italic')
    f.info.postscriptSlantAngle=-9.5; f.info.styleMapStyleName='bold italic' if f.info.styleName=='Bold Italic' else 'italic'
    w=f.info.styleName.replace(' Italic','').replace('Italic','')
    f.info.styleMapFamilyName='Odra Sans' if w in ('','Bold') else 'Odra Sans '+w
    f.save(p.replace('.ufo','Italic.ufo'),overwrite=True)
s=open('sources/OdraSans.designspace').read()
s=re.sub(r'(OdraSans-\w+)\.ufo',r'\1Italic.ufo',s)
s=re.sub(r'stylename="(\w+)"',lambda m:'stylename="%s Italic"'%m.group(1) if m.group(1)!='Regular' else 'stylename="Italic"',s)
s=re.sub(r'name="Odra Sans (\w+)',lambda m:'name="Odra Sans %s Italic'%m.group(1),s)
s=s.replace('OdraSans-RegularItalic','OdraSans-Italic')
open('sources/OdraSans-Italic.designspace','w').write(s)
