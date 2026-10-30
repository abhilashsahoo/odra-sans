# True-italic changes applied to upright outlines BEFORE shearing.
import math
from ufoLib2.objects import Point
TA=math.tan(math.radians(25))
def exit_tail(g):
    """Replace the right stem's flat foot with a cursive exit stroke ending in an angled cut."""
    c=max(g.contours,key=lambda c:max(p.x for p in c.points)); P=c.points; n=len(P)
    cand=[i for i in range(n) if P[i].type=='line' and P[(i+1)%n].type=='line' and P[i].y==0 and P[(i+1)%n].y==0 and P[(i+1)%n].x>P[i].x]
    if not cand: return False
    i=max(cand,key=lambda i:P[i].x); j=(i+1)%n
    xl,xr=P[i].x,P[j].x; S=xr-xl; prev=P[i-1]
    H=min(S+55, prev.y-6) if prev.y>0 else S+55
    E=0.45*S+70; t=0.8*S; o=-10
    T1=(xr+E, 0.30*H+5); T2=(T1[0]-t*0.55, T1[1]+t*0.8)
    J=(xr, max(t+0.35*S, T2[1]))
    pts=[(xl,H,'line'),(xl,H*0.42,None),(xl+S*0.35,o,None),(xr,o,'curve'),
         (xr+E*0.5,o,None),(T1[0]-E*0.12,T1[1]*0.45,None),(T1[0],T1[1],'curve'),
         (T2[0],T2[1],'line'),(T2[0]-E*0.22,T2[1]-(T2[1]-t)*0.75,None),(xr,t,None),(J[0],J[1],'curve')]
    new=[Point(round(x),round(y),ty) for x,y,ty in pts]
    if j==0: c.points[i:]=new[:]; 
    else: c.points[i:j+1]=new
    g.width+=round(E*0.55)
    return True
def rot_round(g,r=3.0):
    """Optical correction: rotate clockwise by r so the later shear (9.5-r) skews the bowl less."""
    xs=[p.x for c in g.contours for p in c.points]; ys=[p.y for c in g.contours for p in c.points]
    if not xs: return
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2; a=math.radians(r); ca,sa=math.cos(a),math.sin(a)
    for c in g.contours:
        for p in c.points:
            dx,dy=p.x-cx,p.y-cy; p.x=round(cx+dx*ca+dy*sa); p.y=round(cy-dx*sa+dy*ca)
TAILS=['n','m','h','a','d','u']; ROUND=['o','O','Q','zero','c','C','oslash','degree']

def f_descender(g):
    """Italic f: extend stem below baseline into a leftward hook with a 25-degree cut."""
    c=g.contours[0]; P=c.points; n=len(P)
    cand=[i for i in range(n) if P[i].type=='line' and P[(i+1)%n].type=='line' and P[i].y==0 and P[(i+1)%n].y==0 and P[(i+1)%n].x>P[i].x]
    if not cand: return False
    i=cand[0]; j=(i+1)%n; xl,xr=P[i].x,P[j].x; S=xr-xl
    D=190; th=round(0.7*S); a=-D+th; tip=xl-60-60
    pts=[(xl,a+70,'line'),(xl,a+25,None),(xl-25,a,None),(xl-60,a,'curve'),(tip,a,'line'),
         (tip-th*TA*0.6,-D,'line'),(xr-60,-D,'line'),(xr-20,-D,None),(xr,-D+25,None),(xr,-D+70,'curve')]
    new=[Point(round(x),round(y),ty) for x,y,ty in pts]
    c.points[i:j+1]=new
    return True
TAILS=TAILS+['l','idotless']
ROUND=ROUND+['e','s','b','p','q','G','S','three','six','eight','nine','zero']
