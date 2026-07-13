from __future__ import annotations
import json, time
from decimal import Decimal, getcontext
from pathlib import Path
getcontext().prec=80
p=Path('/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb')
bounds=(-179.148909,179.778465,-14.548692,71.390482)
internal_max=(1<<46)-1; internal_min=-(1<<46); margin=Decimal(1)
box_min_x=Decimal(str(bounds[0]))-margin; box_max_x=Decimal(str(bounds[1]))+margin
box_min_y=Decimal(str(bounds[2]))-margin; box_max_y=Decimal(str(bounds[3]))+margin
internal_range=Decimal(internal_max-internal_min)
rx=internal_range/(box_max_x-box_min_x); ry=internal_range/(box_max_y-box_min_y)
deltax=(Decimal(internal_max+internal_min)-(box_max_x+box_min_x)*rx)/2
deltay=(Decimal(internal_max+internal_min)-(box_max_y+box_min_y)*ry)/2
point_sx=-34601183442124; point_sy=6221994945795; q=0
correct_y=Decimal('6268618052333.6867160778606595247852497482708163290790060698802484257702572462246')
def scx(s): return int(Decimal(s)*rx+deltax)
def scy(s): return int(Decimal(s)*ry+deltay)
def inspect(eid, header, p1, p2):
    h=header.split(); left=int(h[4]); right=int(h[5])
    x0,y0=p1.split(); x1,y1=p2.split()
    sx0=scx(x0); sx1=scx(x1); sy0=scy(y0); sy1=scy(y1)
    a=sy0-sy1; b=sx1-sx0; c=-(sx0*a)-(sy0*b)
    if b<0: a=-a; b=-b; c=-c
    lo=min(sx0,sx1); hi=max(sx0,sx1); excl=lo if q==0 else hi
    in_range=lo<=point_sx<=hi
    endpoint=point_sx==excl
    if not in_range: return None
    xsect_y=Decimal(-(a*point_sx)-c)/Decimal(b) if b else None
    diff=Decimal(point_sy)-xsect_y if xsect_y is not None else None
    diff2=diff
    if diff2==0: diff2=Decimal(-a if q==0 else a)
    if diff2==0: diff2=Decimal(-b if q==0 else b)
    skip_above=diff2>0 if diff2 is not None else True
    accepted=(not endpoint) and (not skip_above)
    slope=Decimal(a)/Decimal(b) if b else None
    face=right if sx0<sx1 else left
    return {'edge_id':eid,'header':header.strip(),'x0':x0,'y0':y0,'x1':x1,'y1':y1,'left':left,'right':right,'sx0':sx0,'sx1':sx1,'sy0':sy0,'sy1':sy1,'face':face,'endpoint':endpoint,'xsect_y':str(xsect_y),'diff2':str(diff2),'skip_above':skip_above,'accepted':accepted,'slope':str(slope),'beats_correct_y': bool(xsect_y is not None and xsect_y < correct_y)}
start=time.perf_counter()
rows=[]
accepted=[]
endpoint_or_above_before=[]
with p.open() as f:
    eid=0
    for header in f:
        eid += 1
        p1=next(f).strip(); p2=next(f).strip()
        r=inspect(eid, header, p1, p2)
        if r is not None:
            rows.append(r)
            if r['accepted']:
                accepted.append(r)
            elif r['beats_correct_y']:
                endpoint_or_above_before.append(r)
summary={'elapsed_sec':time.perf_counter()-start,'covering_count':len(rows),'accepted_count':len(accepted),'rejected_before_correct_count':len(endpoint_or_above_before),'accepted_best':min(accepted,key=lambda r: Decimal(r['xsect_y'])) if accepted else None,'rejected_before_correct_first20':endpoint_or_above_before[:20],'target_rows':[r for r in rows if r['edge_id'] in {9094414,9095647,9102784,10139644}], 'rows': rows}
Path('/workspace/goal4839_chunked_edge_probe_result.json').write_text(json.dumps(summary, indent=2))
print(json.dumps({k:v for k,v in summary.items() if k!='rows'}, indent=2))
