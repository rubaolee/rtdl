# Goal593 Public Examples Smoke

Date: 2026-04-19

Status: ACCEPTED with Claude + Gemini review consensus

## Scope

This goal smoke-runs the public top-level examples after the Goal590/591/592
documentation and backend-maturity refresh. It excludes `examples/internal/`,
`examples/generated/`, and `examples/visual_demo/` because those are not the
normal first-run public examples.

## Command

```bash
PYTHONPATH=src:. python3 - <<'PY'
from pathlib import Path
import json, os, subprocess, sys, time
examples = sorted(Path('examples').glob('rtdl_*.py'))
results = []
base_env = os.environ.copy()
base_env['PYTHONPATH'] = 'src:.'
for path in examples:
    start = time.perf_counter()
    try:
        proc = subprocess.run([sys.executable, str(path)], cwd='.', env=base_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        status = 'pass' if proc.returncode == 0 else 'fail'
    except subprocess.TimeoutExpired as exc:
        proc = None
        status = 'timeout'
        stdout = exc.stdout or ''
        stderr = exc.stderr or ''
    else:
        stdout = proc.stdout
        stderr = proc.stderr
    elapsed = time.perf_counter() - start
    results.append({
        'path': str(path),
        'status': status,
        'returncode': None if proc is None else proc.returncode,
        'seconds': elapsed,
        'stdout_tail': stdout[-1200:],
        'stderr_tail': stderr[-1200:],
    })
    print(f'{status:7} {elapsed:8.3f}s {path}')
Path('docs/reports').mkdir(parents=True, exist_ok=True)
out = Path('docs/reports/goal593_public_examples_smoke_macos_2026-04-19.json')
out.write_text(json.dumps({'date':'2026-04-19','examples':[r for r in results]}, indent=2) + '\\n')
failed = [r for r in results if r['status'] != 'pass']
print('\\nfailed_count', len(failed), 'artifact', out)
raise SystemExit(1 if failed else 0)
PY
```

## Result

Artifact:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal593_public_examples_smoke_macos_2026-04-19.json
```

Summary:

- public top-level examples discovered: 29
- passed: 29
- failed: 0
- timed out: 0

Passing examples:

- `examples/rtdl_ann_candidate_app.py`
- `examples/rtdl_apple_rt_closest_hit.py`
- `examples/rtdl_barnes_hut_force_app.py`
- `examples/rtdl_db_conjunctive_scan.py`
- `examples/rtdl_db_grouped_count.py`
- `examples/rtdl_db_grouped_sum.py`
- `examples/rtdl_dbscan_clustering_app.py`
- `examples/rtdl_event_hotspot_screening.py`
- `examples/rtdl_facility_knn_assignment.py`
- `examples/rtdl_feature_quickstart_cookbook.py`
- `examples/rtdl_fixed_radius_neighbors.py`
- `examples/rtdl_graph_bfs.py`
- `examples/rtdl_graph_triangle_count.py`
- `examples/rtdl_hausdorff_distance_app.py`
- `examples/rtdl_hello_world.py`
- `examples/rtdl_hello_world_backends.py`
- `examples/rtdl_hiprt_ray_triangle_hitcount.py`
- `examples/rtdl_knn_rows.py`
- `examples/rtdl_outlier_detection_app.py`
- `examples/rtdl_polygon_pair_overlap_area_rows.py`
- `examples/rtdl_polygon_set_jaccard.py`
- `examples/rtdl_road_hazard_screening.py`
- `examples/rtdl_robot_collision_screening_app.py`
- `examples/rtdl_sales_risk_screening.py`
- `examples/rtdl_segment_polygon_anyhit_rows.py`
- `examples/rtdl_segment_polygon_hitcount.py`
- `examples/rtdl_service_coverage_gaps.py`
- `examples/rtdl_v0_7_db_app_demo.py`
- `examples/rtdl_v0_7_db_kernel_app_demo.py`

## Interpretation

The public examples are runnable on the local Mac with `PYTHONPATH=src:.`.
Backend-specific examples use their existing bounded behavior: they either run
the available local backend path or report backend availability clearly without
failing the first-run user experience.

This is a macOS local smoke, not Linux/Windows full release validation.

## Review Consensus

External review artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal593_claude_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal593_gemini_flash_review_2026-04-19.md`

Both reviews returned `ACCEPT`. They confirmed the 29 reported files match the
public top-level examples on disk, all smoke executions exited successfully, and
the macOS-only scope is honestly bounded.
