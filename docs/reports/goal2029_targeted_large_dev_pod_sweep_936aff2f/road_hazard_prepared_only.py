import json, statistics, time, sys, pathlib
sys.path.insert(0,'src'); sys.path.insert(0,'.')
import rtdsl as rt
from scripts import goal1869_road_hazard_v2_partner_perf as g

def stats(xs): return {'min_s':min(xs),'median_s':statistics.median(xs),'max_s':max(xs)}
def run(count, iterations, output):
    roads,hazards,expected_counts=g._build_records(count)
    expected_rows=tuple({'segment_id': road.id, 'hit_count': c} for road,c in zip(roads,expected_counts))
    expected_flags=g._flags_from_counts(expected_rows,2)
    output_capacity=max(1,len(roads)*len(hazards))
    prepared=rt.prepare_optix_segment_polygon_hitcount_2d(hazards)
    v1=[]; last=None
    try:
        for i in range(iterations):
            t=time.perf_counter(); last=prepared.run(roads); v1.append(time.perf_counter()-t); print('v1_prepared', count, i+1, v1[-1], flush=True)
    finally:
        prepared.close()
    if g._canonical_counts(last)!=g._canonical_counts(expected_rows): raise RuntimeError('v1 mismatch')
    ray_columns, triangle_columns, triangle_aabbs, runtime, build_s = g._build_partner_columns(roads,hazards,'cupy')
    scene=rt.prepare_segment_polygon_anyhit_optix_partner_device_scene(triangle_columns, triangle_aabbs)
    witness=rt.allocate_segment_polygon_witness_partner_device_output_columns(output_capacity, partner='cupy')
    v2=[]; result=None
    try:
        for i in range(iterations):
            t=time.perf_counter(); result=rt.road_hazard_priority_flags_optix_prepared_partner_device_columns(scene, ray_columns, threshold=2, partner='cupy', output_capacity=output_capacity, witness_output_columns=witness, return_metadata=True); runtime['sync'](); v2.append(time.perf_counter()-t); print('v2_prepared', count, i+1, v2[-1], flush=True)
    finally:
        scene.close()
    flags=g._columns_to_flags(g._result_columns(result), runtime)
    payload={'goal':'Goal2029-road-prepared-only','count':count,'hazards':len(hazards),'output_capacity':output_capacity,'iterations':iterations,'column_build_s':build_s,'v1_prepared':stats(v1),'v2_prepared':stats(v2),'ratio':statistics.median(v2)/statistics.median(v1),'strict_priority_flags_match': flags==expected_flags, 'metadata': g._result_metadata(result)}
    pathlib.Path(output).write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
    print(json.dumps(payload, indent=2, sort_keys=True))
if __name__=='__main__': run(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
