import json, hashlib, time
from pathlib import Path
from rtdsl.rayjoin_overlay import run_rayjoin_overlay_rtdl_from_cdb_paths
left='/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb'
right='/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb'
out=Path('/workspace/goal4875_section57_au_representative/rtdl_bundled_full/rtdl_overlay.txt')
out.parent.mkdir(parents=True, exist_ok=True)
start=time.perf_counter()
result=run_rayjoin_overlay_rtdl_from_cdb_paths(left,right,backend='optix',assemble_output=True,output_path=out)
elapsed=time.perf_counter()-start
h=hashlib.sha256(); lines=0
with out.open('rb') as f:
    for chunk in iter(lambda:f.read(1<<20), b''):
        h.update(chunk); lines += chunk.count(b'\n')
summary={'schema':'rtdl.goal4875.bundled_full_sanity.v1','elapsed_sec':elapsed,'output':str(out),'bytes':out.stat().st_size,'lines':lines,'sha256':h.hexdigest(),'result':result}
Path('/workspace/goal4875_section57_au_representative/rtdl_bundled_full/summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True,default=str),encoding='utf-8')
print(json.dumps(summary,indent=2,sort_keys=True,default=str))
