# Goal2147 RayJoin v2 Scale/Perf Harness

Date: 2026-05-16

Status: local CPU/Embree scale harness complete; OptiX pod evidence pending.

## Purpose

Goal2145 proved that a learner can write RayJoin-style PIP, LSI, and overlay-seed workloads as a Python+RTDL v2 user program. Goal2147 turns that slice into a repeatable scale/perf harness so we can run meaningful local checks now and reuse the exact same workload generator on an OptiX pod later.

New script:

- `scripts/goal2147_rayjoin_v2_scale_perf.py`

Committed local artifact:

- `docs/reports/goal2147_rayjoin_v2_scale_perf_quick_local_2026-05-16.json`

## Harness Design

The harness creates deterministic synthetic cases that exercise row contracts rather than tiny fixture coincidences:

| Workload | Synthetic case | Contract stressed |
| --- | --- | --- |
| `pip` | Disjoint square polygons, fixed number of interior points per polygon | Sparse `point_to_polygon_positive_hit_rows` |
| `lsi` | Horizontal segments crossed with vertical segments | Dense `segment_segment_intersection_rows` |
| `overlay_seed` | Shifted square pairs on a grid | `overlay_pair_dependency_rows_with_lsi_pip_flags` plus active seed counts |

The script supports:

- scales: `quick`, `medium`, `large`
- backends: `cpu_python_reference`, `cpu`, `embree`, `optix`
- repeat/warmup controls
- JSON output
- progress logging before each reference, warmup, and timed repeat

The progress logging is important. A medium overlay Python truth run can take roughly two minutes on this Windows host, so the harness must never sit silently during pod or local runs.

## Contract Correction From Goal2145

The first Goal2145 wording described overlay output as `overlay_seed_rows_requiring_lsi_and_pip_continuation`. Running synthetic overlay cases made that imprecise: the current overlay primitive emits pair-dependency rows with `requires_lsi` / `requires_pip` flags. Active continuation seeds are a summary derived from those rows.

Updated user-facing contract:

- `overlay_pair_dependency_rows_with_lsi_pip_flags`

Updated summary fields:

- `pair_dependency_row_count`
- `active_seed_count`
- `active_seed_pairs`

This keeps the app precise and avoids teaching learners that overlay currently emits only active pairs.

## Local Quick Evidence

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 scripts\goal2147_rayjoin_v2_scale_perf.py --scale quick --backends cpu,embree --repeats 2 --warmups 0 --output docs\reports\goal2147_rayjoin_v2_scale_perf_quick_local_2026-05-16.json
```

Quick artifact summary:

| Workload | Inputs | Reference rows | CPU parity | Embree parity | Contract |
| --- | ---: | ---: | --- | --- | --- |
| `pip` | 64 points / 32 polygons | 64 | true | true | `point_to_polygon_positive_hit_rows` |
| `lsi` | 32 left / 32 right segments | 1,024 | true | true | `segment_segment_intersection_rows` |
| `overlay_seed` | 32 left / 32 right polygons | 1,024 pair rows, 32 active seeds | true | true | `overlay_pair_dependency_rows_with_lsi_pip_flags` |

This quick artifact is a harness smoke test, not performance evidence.

## Local Medium Observation

An exploratory local medium run was also executed to stress the shape:

| Workload | Inputs | Rows | Local observation |
| --- | ---: | ---: | --- |
| `pip` | 1,024 points / 256 polygons | 1,024 positive rows | CPU and Embree parity held. |
| `lsi` | 128 left / 128 right segments | 16,384 intersections | CPU and Embree parity held. |
| `overlay_seed` | 128 left / 128 right polygons | 16,384 pair rows / 128 active seeds | CPU and Embree parity held, but Python truth generation was slow enough to require progress logs for future runs. |

The medium observation is local development evidence only. It does not authorize a paper-scale RayJoin claim.

## Claim Boundary

This goal does not authorize:

- full RayJoin paper reproduction
- paper-scale performance
- RT-core speedup claims
- v2.0 release authorization
- conservative high-precision RayJoin correctness

This goal does authorize:

- using the harness for future pod runs
- treating the corrected overlay contract as the current RTDL v2 user-facing description
- using the quick artifact as local harness smoke evidence

## Next Work

1. Run the harness on an OptiX pod with `--scale medium` and then bounded `--scale large`.
2. Capture the pod environment, OptiX SDK/CUDA setup, `RTDL_OPTIX_LIBRARY`, commit hash, and JSON artifacts.
3. Add CUDA/CuPy non-RT baselines for the same synthetic cases.
4. Add RayJoin repository dataset adapters outside the native engine.
5. After pod runs, decide whether RTDL v2 needs a generic closest-owner/point-location contract beyond sparse positive-hit rows.

## Verdict

Goal2147 is accepted as a local scale/perf harness and contract cleanup. Serious RT-core evidence starts at the next pod run.
