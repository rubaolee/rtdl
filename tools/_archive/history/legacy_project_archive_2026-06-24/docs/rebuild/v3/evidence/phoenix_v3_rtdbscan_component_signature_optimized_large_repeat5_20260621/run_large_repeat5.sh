#!/usr/bin/env bash
set -euo pipefail
ROOT=/root/rtdl_v3_rebuild_20260620/current
ART=/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_rtdbscan_component_signature_optimized_large_repeat5_20260621
mkdir -p "$ART"
: > "$ART/run.log"
cd "$ROOT"
. ../.venv/bin/activate
export PYTHONPATH=src:.
APP=examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py
EMBREE=embree_core_flags_numba_prepared_grid_column_signature_3d
OPTIX=optix_rt_core_flags_numba_prepared_grid_column_signature_3d
run_case() {
  backend="$1"
  mode="$2"
  points="$3"
  case_id="rtdbscan_${backend}_optimized_large_repeat5_clustered3d_${points}_r5"
  echo "[large-repeat5] ${case_id}" | tee -a "$ART/run.log"
  python "$APP" \
    --mode "$mode" \
    --dataset clustered3d \
    --point-count "$points" \
    --seed 20260519 \
    --partner numba \
    --repeat 5 \
    --warmup 1 \
    --no-validation \
    > "$ART/${case_id}.stdout.json" \
    2> "$ART/${case_id}.stderr.txt"
}
run_case embree "$EMBREE" 262144
run_case optix "$OPTIX" 262144
run_case embree "$EMBREE" 524288
run_case optix "$OPTIX" 524288
python - <<'PY'
import json, time
from pathlib import Path
ART=Path('/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_rtdbscan_component_signature_optimized_large_repeat5_20260621')
rows=[]
for path in sorted(ART.glob('*.stdout.json')):
    data=json.loads(path.read_text())
    meta=data.get('metadata', {})
    protocol=meta.get('prepared_query_repeat_protocol', {})
    timing=meta.get('timing_breakdown_sec', {})
    case_id=path.name.replace('.stdout.json','')
    backend='optix' if '_optix_' in case_id else 'embree'
    rows.append({
        'case_id': case_id,
        'backend': backend,
        'point_count': data.get('point_count'),
        'elapsed_sec': data.get('elapsed_sec'),
        'matches_reference': data.get('matches_reference'),
        'signature': data.get('signature'),
        'reference_signature_present': bool(data.get('reference_signature')),
        'repeat': protocol.get('repeat'),
        'warmup': protocol.get('warmup'),
        'measured_iterations': protocol.get('measured_iterations'),
        'median_elapsed_sec': protocol.get('median_elapsed_sec'),
        'signatures_stable': protocol.get('signatures_stable'),
        'column_signature_strategy': meta.get('column_signature_strategy'),
        'column_signature_materializes_point_ids': meta.get('column_signature_materializes_point_ids'),
        'column_signature_materializes_core_flags': meta.get('column_signature_materializes_core_flags'),
        'column_signature_uses_numba_label_count_and_flag_count': meta.get('column_signature_uses_numba_label_count_and_flag_count'),
        'numba_component_continuation_sec': meta.get('numba_component_continuation_sec'),
        'optix_rt_count_threshold_sec': meta.get('optix_rt_count_threshold_sec'),
        'embree_threshold_compact_rows_sec': meta.get('embree_threshold_compact_rows_sec'),
        'timing_breakdown_sec': timing,
    })

def canon(sig):
    if not isinstance(sig, dict) or not isinstance(sig.get('cluster_sizes'), dict):
        return None
    return {
        'cluster_sizes': sorted(int(v) for v in sig['cluster_sizes'].values() if int(v) > 0),
        'core_count': int(sig.get('core_count', -1)),
        'noise_count': int(sig.get('noise_count', -1)),
    }

def ratio(a,b):
    return (float(a)/float(b)) if isinstance(a,(int,float)) and isinstance(b,(int,float)) and float(b)>0 else None
pairs=[]
for points in sorted({r['point_count'] for r in rows}):
    embree=next(r for r in rows if r['point_count']==points and r['backend']=='embree')
    optix=next(r for r in rows if r['point_count']==points and r['backend']=='optix')
    pairs.append({
        'point_count': points,
        'repeat': optix['repeat'],
        'warmup': optix['warmup'],
        'measured_iterations': optix['measured_iterations'],
        'same_canonical_component_signature': canon(embree['signature']) == canon(optix['signature']) and canon(embree['signature']) is not None,
        'embree_sec': embree['elapsed_sec'],
        'optix_sec': optix['elapsed_sec'],
        'optix_speedup_vs_embree': ratio(embree['elapsed_sec'], optix['elapsed_sec']),
        'rt_threshold_speedup_vs_embree_compact_rows': ratio(embree['embree_threshold_compact_rows_sec'], optix['optix_rt_count_threshold_sec']),
        'embree_numba_component_continuation_sec': embree['numba_component_continuation_sec'],
        'optix_numba_component_continuation_sec': optix['numba_component_continuation_sec'],
        'optix_rt_count_threshold_sec': optix['optix_rt_count_threshold_sec'],
        'continuation_dominates_optix': isinstance(optix['numba_component_continuation_sec'], (int,float)) and isinstance(optix['optix_rt_count_threshold_sec'], (int,float)) and optix['numba_component_continuation_sec'] > optix['optix_rt_count_threshold_sec'],
    })
speedups=[p['optix_speedup_vs_embree'] for p in pairs if isinstance(p.get('optix_speedup_vs_embree'), (int,float))]
payload={
    'status': 'rtdbscan_component_signature_optimized_large_repeat5_evidence',
    'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
    'artifact_dir': str(ART),
    'rows': rows,
    'pairs': pairs,
    'summary': {
        'row_count': len(rows),
        'pair_count': len(pairs),
        'all_pairs_repeat5_warmup1': all(p['repeat']==5 and p['warmup']==1 and p['measured_iterations']==4 for p in pairs),
        'all_large_signatures_match': all(p['same_canonical_component_signature'] for p in pairs),
        'strongest_optix_speedup_vs_embree': max(speedups) if speedups else None,
        'weakest_optix_speedup_vs_embree': min(speedups) if speedups else None,
        'release_authorized': False,
        'public_speedup_claim_authorized': False,
        'm7_promotion_authorized': False,
    },
    'claim_boundary': {
        'large_scale_correctness_basis': 'OptiX/Embree intra-run canonical component-signature agreement, not independent CPU reference validation',
        'release_authorized': False,
        'public_speedup_claim_authorized': False,
        'm7_promotion_authorized': False,
    }
}
(ART/'summary.json').write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
lines=['# Phoenix V3 RTDBSCAN Optimized Large Repeat5 Evidence','',f"status: {payload['status']}",'','| Point count | Repeat | Measured iterations | Embree sec | OptiX sec | Speedup | Same signature | Continuation dominates OptiX |','| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |']
for p in pairs:
    lines.append(f"| {p['point_count']} | {p['repeat']} | {p['measured_iterations']} | {p['embree_sec']:.6g} | {p['optix_sec']:.6g} | {p['optix_speedup_vs_embree']:.6g}x | `{p['same_canonical_component_signature']}` | `{p['continuation_dominates_optix']}` |")
lines += ['', 'Claim boundary: large-scale correctness is OptiX/Embree intra-run canonical component-signature agreement, not independent CPU reference validation.', 'No release, public speedup, paper, broad V3, or V2 claim is authorized by this artifact alone.', '']
(ART/'summary.md').write_text('\n'.join(lines))
print(json.dumps(payload['summary'], indent=2, sort_keys=True))
PY
