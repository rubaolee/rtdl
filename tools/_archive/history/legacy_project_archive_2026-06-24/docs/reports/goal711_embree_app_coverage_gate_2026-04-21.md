# Goal 711: Embree App Coverage Gate

Date: 2026-04-21

Status: ACCEPT

## Purpose

Goal 711 checks the pre-v1.0 Embree app baseline after the Goal 709 thread
configuration contract and Goal 710 point-query parallelization work.

The question is narrow: every public app that currently advertises
`direct_cli_native` Embree support in `docs/app_engine_support_matrix.md`
should run through its public CLI with both the CPU/Python oracle backend and
the Embree backend, return valid JSON, and preserve backend-normalized
application semantics.

This is not a whole-app speedup claim. These are small public app fixtures and
the measured times are dominated by Python process startup, JSON production,
and app orchestration. Kernel-level performance evidence remains in Goal 710.

## Evidence

Script:

`/Users/rl2025/rtdl_python_only/scripts/goal711_embree_app_coverage_gate.py`

Machine result:

`/Users/rl2025/rtdl_python_only/docs/reports/goal711_embree_app_coverage_gate_macos_2026-04-21.json`

Command:

```sh
PYTHONPATH=src:. python3 scripts/goal711_embree_app_coverage_gate.py \
  --output docs/reports/goal711_embree_app_coverage_gate_macos_2026-04-21.json
```

Result:

- Apps checked: 14
- Runs checked: 28
- CPU/Python oracle runs: 14/14 OK
- Embree runs: 14/14 OK
- JSON validity: 28/28 OK
- Backend-normalized semantic payload comparison: 14/14 match
- Overall gate validity: true

## App Coverage

The gate covers every app with `direct_cli_native` Embree support in the public
app matrix, excluding Apple-specific or non-Embree app rows.

| App | CPU/Python | Embree | Semantic match |
| --- | --- | --- | --- |
| `database_analytics` | OK | OK | yes |
| `graph_analytics` | OK | OK | yes |
| `service_coverage_gaps` | OK | OK | yes |
| `event_hotspot_screening` | OK | OK | yes |
| `facility_knn_assignment` | OK | OK | yes |
| `road_hazard_screening` | OK | OK | yes |
| `segment_polygon_hitcount` | OK | OK | yes |
| `segment_polygon_anyhit_rows` | OK | OK | yes |
| `hausdorff_distance` | OK | OK | yes |
| `ann_candidate_search` | OK | OK | yes |
| `outlier_detection` | OK | OK | yes |
| `dbscan_clustering` | OK | OK | yes |
| `robot_collision_screening` | OK | OK | yes |
| `barnes_hut_force` | OK | OK | yes |

## Comparison Method

The script compares app JSON after removing backend-identification and
backend-execution metadata:

- `backend`
- `requested_backend`
- `data_flow`
- `prepared_dataset`

The script also rounds floating-point values to 12 decimal places before
hashing, because CPU and Embree paths can differ at last-bit precision while
returning the same app result.

Lists are canonicalized by content before hashing. This catches real semantic
drift while avoiding false mismatches from row-order or metadata differences.

## Performance Boundary

The JSON records elapsed wall-clock time for each public CLI invocation, but
Goal 711 does not claim Embree whole-app speedup from these numbers. The
fixtures are intentionally small public examples. Most runs are about 0.10 to
0.15 seconds on this macOS host, so process startup and Python orchestration
are large parts of the measurement.

Goal 710 remains the stronger local evidence for Embree kernel-level
parallelization:

- `knn_rows`: 1 thread 1.221234 s, auto 0.224760 s, 5.43x speedup on the
  macOS Goal 710 point-query perf script.
- `fixed_radius_neighbors`: 1 thread 0.011468 s, auto 0.009231 s, 1.24x
  speedup at smoke scale.

## Honest Interpretation

This gate proves:

- The public Embree app surface is runnable.
- The public Embree app surface preserves CPU/Python oracle semantics on the
  checked fixtures.
- The app support matrix is not advertising dead Embree CLI paths for these
  apps.

This gate does not prove:

- Embree is faster for every whole app.
- Every app has been scaled to large Windows 32-thread or Linux multicore
  performance sizes.
- Graph, DB, ray-query, and segment/polygon paths have received the same native
  multithreading work as Goal 710 point-query kernels.

## Remaining Work

- Run larger Embree app-performance workloads on the Windows 32-thread host.
- Extend explicit native multithreading beyond point-query kernels where the
  backend implementation and Embree API shape make that safe.
- Keep app docs clear that Embree is CPU BVH/ray/point-query acceleration, not
  GPU RT-core acceleration.

## Consensus

- Codex: ACCEPT
- Claude: ACCEPT after the gate exit-code fix
- Gemini Flash: ACCEPT

The consensus closure is recorded in
`/Users/rl2025/rtdl_python_only/docs/reports/goal711_codex_consensus_closure_2026-04-21.md`.

## Verdict

Goal 711 is a valid pre-v1.0 Embree app coverage gate, with bounded performance
claims and no release-level speedup overstatement.
