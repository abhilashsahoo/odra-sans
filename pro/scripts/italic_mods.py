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

# ---- v1.2 additions ----
def _ly(P,Q,y):
    if Q.y==P.y: return (P.x,y)
    t=(y-P.y)/(Q.y-P.y); return (P.x+(Q.x-P.x)*t, y)
def flick(g, ci, i):
    """Generic cursive exit on a flat foot P[i]->P[i+1] whose sides may be diagonal (k leg)."""
    c=g.contours[ci]; P=c.points; n=len(P); j=(i+1)%n
    A,B,Pv,N=P[i],P[j],P[i-1],P[(j+1)%n]; S=B.x-A.x
    H=min(S+55,Pv.y-6); t=0.8*S; E=0.45*S+70
    A1=_ly(A,Pv,H); T1=(B.x+E,0.30*H+5); T2=(T1[0]-t*0.55,T1[1]+t*0.8)
    Jy=min(max(t+0.35*S,T2[1]),N.y-6); J=_ly(B,N,Jy); Jt=_ly(B,N,t)
    pts=[(A1[0],H,'line'),(A.x+(A1[0]-A.x)*0.42,H*0.42,None),(A.x+S*0.35,-10,None),(B.x,-10,'curve'),
         (B.x+E*0.5,-10,None),(T1[0]-E*0.12,T1[1]*0.45,None),(T1[0],T1[1],'curve'),
         (T2[0],T2[1],'line'),(T2[0]-E*0.22,T2[1]-(T2[1]-t)*0.75,None),(Jt[0],t,None),(J[0],J[1],'curve')]
    new=[Point(round(x),round(y),ty) for x,y,ty in pts]
    if j==0: c.points[i:]=new
    else: c.points[i:j+1]=new
    g.width+=round(E*0.55)
def round_vertex(c, i, r, down=True):
    """Replace sharp point P[i] (or flat foot P[i],P[i+1]) with a smooth curve -> cursive v/w."""
    P=c.points; n=len(P)
    flat = P[(i+1)%n].y==P[i].y
    A=P[i]; B=P[(i+1)%n] if flat else P[i]; Pv=P[i-1]; N=P[(i+2)%n] if flat else P[(i+1)%n]
    y0=A.y; s=1 if down else -1
    A1=_ly(A,Pv,y0+s*r); B1=_ly(B,N,y0+s*r); mx=(A.x+B.x)/2; yb=y0-s*(10 if flat else 4)
    pts=[(A1[0],A1[1],'line'),(A1[0]+(A.x-A1[0])*0.55,y0+s*r*0.45,None),(mx-(mx-A.x)*0.45-r*0.15,yb,None),(mx,yb,'curve'),
         (mx+(B.x-mx)*0.45+r*0.15,yb,None),(B1[0]+(B.x-B1[0])*0.55,y0+s*r*0.45,None),(B1[0],B1[1],'curve')]
    new=[Point(round(x),round(y),ty) for x,y,ty in pts]
    k=2 if flat else 1
    if i+k>n: c.points[i:]=new; del c.points[:(i+k)-n]
    else: c.points[i:i+k]=new
def italic_v(g):
    c=g.contours[0]
    # inner vertex first (higher index-safe ordering: process from highest index down)
    P=c.points; n=len(P)
    foot=[i for i in range(n) if P[i].y==min(p.y for p in P) and P[(i+1)%n].y==P[i].y]
    inner=[i for i in range(n) if P[i].type=='line' and 0<P[i].y<400 and P[i-1].y>P[i].y<P[(i+1)%n].y]
    S=P[foot[0]+1].x-P[foot[0]].x
    for i in sorted(foot+inner, reverse=True):
        round_vertex(c,i, round(S*1.6) if i in foot else round(S*1.1))
def italic_y(g):
    """Descender becomes a curved leftward hook, 25-degree cut, like f/g."""
    c=g.contours[0]; P=list(c.points); n=len(P); D=min(p.y for p in P)
    bot=[k for k in range(n) if P[k].y<=D+5]
    # rotate so list starts right after the bottom block
    s=[k for k in range(n) if P[k].y>D+5 and P[k-1].y<=D+5][0]; P=P[s:]+P[:s]
    bot=[k for k in range(n) if P[k].y<=D+5]; first=min(bot)
    L=P[first-1]; R=P[-1] if False else None
    x0=min(p.x for p in P if p.y<=D+5); x1=max(p.x for p in P if p.y<=D+5)
    top=P[0]  # first point after bottom = right edge top (e.g. 491,520)
    S=x1-x0; th=round(0.62*S); tip=x0-115
    Ry=D+th+45; R=_ly(Point(x1,D),top,Ry)
    tail=[(L.x-0.2*S,L.y-0.55*(L.y-D-th),None),(tip+60,D+th,None),(tip,D+th,'curve'),
          (tip-th*TA*0.6,D,'line'),(tip+50+S*0.6,D,None),(R[0]-8,D+15,None),(R[0],R[1],'curve')]
    body=P[:first]  # ends with L
    c.points[:]=body+[Point(round(x),round(y),ty) for x,y,ty in tail]
def angle_cut_r(g):
    """r arm: vertical terminal -> 25-degree cut."""
    c=g.contours[0]; P=c.points; xs=max(p.x for p in P)
    tt=[p for p in P if p.x==xs]
    if len(tt)==2:
        hi=max(tt,key=lambda p:p.y); lo=min(tt,key=lambda p:p.y); hi.x=round(xs+(hi.y-lo.y)*TA)
def italic_k(g):
    c=g.contours[0]; P=c.points; n=len(P)
    cand=[i for i in range(n) if P[i].y==0 and P[(i+1)%n].y==0 and P[(i+1)%n].x>P[i].x]
    flick(g,0,max(cand,key=lambda i:P[i].x))
def italic_t(g):
    """t: lengthen the existing foot hook into an exit with a 25-degree cut."""
    c=g.contours[0]; P=c.points
    xs=max(p.x for p in P if p.y<200); tt=[p for p in P if p.x>=xs-30 and p.y<200 and p.type in('line','curve')]
    for p in tt: p.x+=30
    hi=max(tt,key=lambda p:p.y); lo=min(tt,key=lambda p:p.y)
    g.width+=20
V12={'k':italic_k,'r':angle_cut_r,'v':italic_v,'w':italic_v,'y':italic_y,'t':italic_t}
def sync_composite_widths(layer, deltas):
    for g in layer:
        if g.contours or not g.components: continue
        b=g.components[0].baseGlyph
        if b in deltas and g.components[0].transformation[4]==0: g.width+=deltas[b]
