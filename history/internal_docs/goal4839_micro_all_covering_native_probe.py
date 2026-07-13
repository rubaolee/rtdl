import json, sys
from decimal import Decimal
import numpy as np
sys.path.insert(0, '/workspace/rtdl_goal4817_user_smoke_20260630_102224/src')
from rtdsl.embree_runtime import pack_rayjoin_cdb_segments, pack_rayjoin_cdb_scaled_points
from rtdsl.optix_runtime import prepare_rayjoin_cdb_point_location_2d_optix
from rtdsl.rayjoin_overlay import _rayjoin_cdb_point_location_env, _rayjoin_scaling_constants
with open('/workspace/goal4839_chunked_edge_probe_result.json') as f:
    data=json.load(f)
rows=data['rows']
bounds=(-179.148909,179.778465,-14.548692,71.390482)
*_, rrx, rry, ddeltax, ddeltay = _rayjoin_scaling_constants(bounds)
sx=-34601183442124; sy=6221994945795
x=sx*rrx+ddeltax; y=sy*rry+ddeltay
segments=pack_rayjoin_cdb_segments(
    ids=np.array([r['edge_id'] for r in rows], dtype=np.int64),
    x0=np.array([float(r['x0']) for r in rows], dtype=np.float64),
    y0=np.array([float(r['y0']) for r in rows], dtype=np.float64),
    x1=np.array([float(r['x1']) for r in rows], dtype=np.float64),
    y1=np.array([float(r['y1']) for r in rows], dtype=np.float64),
    left_face_ids=np.array([r['left'] for r in rows], dtype=np.uint32),
    right_face_ids=np.array([r['right'] for r in rows], dtype=np.uint32),
)
scaled_points=pack_rayjoin_cdb_scaled_points(
    ids=np.array([1], dtype=np.int64), x=np.array([x]), y=np.array([y]),
    sx=np.array([sx], dtype=np.int64), sy=np.array([sy], dtype=np.int64),
)
with _rayjoin_cdb_point_location_env(0, bounds):
    prepared=prepare_rayjoin_cdb_point_location_2d_optix(segments)
    try:
        rows_view=prepared.run_raw(scaled_points)
        try:
            cols=rows_view.to_numpy_columns(copy=True)
        finally:
            rows_view.close()
    finally:
        prepared.close()
print(json.dumps({'edge_count':len(rows),'native': {k: cols[k].tolist() for k in cols}, 'author_best': data['accepted_best']}, indent=2))
