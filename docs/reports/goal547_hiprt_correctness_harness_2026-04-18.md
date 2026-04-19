# Goal 547: HIPRT Correctness Harness Across v0.9 Target Workloads

Date: 2026-04-18
Status: accepted with 2-AI consensus

## Purpose

Goal 547 adds the reusable HIPRT correctness matrix harness for the v0.9
backend line. The harness enumerates every target workload from the v0.9 plan
and records whether HIPRT:

- passes row-level parity against CPU Python reference;
- is explicitly `NOT_IMPLEMENTED` with no CPU fallback;
- is unavailable on the current host;
- fails.

This is the baseline harness that later v0.9 implementation goals must drive
from `NOT_IMPLEMENTED` to `PASS`.

## Files Added

- `/Users/rl2025/rtdl_python_only/scripts/goal547_hiprt_correctness_matrix.py`
- `/Users/rl2025/rtdl_python_only/tests/goal547_hiprt_correctness_matrix_test.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal547_hiprt_correctness_matrix_local_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal547_hiprt_correctness_matrix_linux_2026-04-18.json`

## Workload Coverage

The matrix covers 17 target entries:

- `segment_intersection`
- `point_in_polygon`
- `overlay_compose`
- `ray_triangle_hit_count_2d`
- `ray_triangle_hit_count_3d`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `point_nearest_segment`
- `fixed_radius_neighbors_2d`
- `fixed_radius_neighbors_3d`
- `knn_rows_2d`
- `knn_rows_3d`
- `bfs_discover`
- `triangle_match`
- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

## Current Matrix Results

Local macOS:

- `pass`: 0
- `not_implemented`: 16
- `hiprt_unavailable`: 1
- `fail`: 0

Linux with HIPRT:

- `pass`: 1
- `not_implemented`: 16
- `hiprt_unavailable`: 0
- `fail`: 0

The one Linux `PASS` is current Ray3D/Triangle3D
`ray_triangle_hit_count_3d`, with HIPRT row parity against CPU Python reference.

The 16 `NOT_IMPLEMENTED` entries are expected after Goal 546 and are not
failures. They prove the API skeleton is honest: unsupported peer workloads are
recognized and rejected with messages that include `No CPU fallback is used`.

## Validation

Local command:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal547_hiprt_correctness_matrix.py \
  --output docs/reports/goal547_hiprt_correctness_matrix_local_2026-04-18.json
PYTHONPATH=src:. python3 -m unittest \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test
```

Local result:

- matrix exit status: 0
- unit tests: `Ran 8 tests`, `OK`

Linux command:

```bash
cd /tmp/rtdl_goal547_hiprt_correctness_matrix
HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
make build-hiprt HIPRT_PREFIX=$HIPRT_PREFIX
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HIPRT_PREFIX/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 scripts/goal547_hiprt_correctness_matrix.py \
  --output docs/reports/goal547_hiprt_correctness_matrix_linux_2026-04-18.json
PYTHONPATH=src:. python3 -m unittest \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test
```

Linux result:

- matrix exit status: 0
- unit tests: `Ran 8 tests`, `OK`

## Consensus

- Codex: ACCEPT
- Claude: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal547_external_review_2026-04-18.md`

## Codex Review

Codex accepts this harness because:

- it covers every workload entry required by the v0.9 plan;
- it records row-level CPU Python reference counts for every entry;
- it distinguishes `NOT_IMPLEMENTED` from real failure;
- it distinguishes local HIPRT absence from real failure;
- it produces durable JSON artifacts for local and Linux runs;
- it gives later implementation goals a measurable target.

Claude noted one non-blocking issue: ordered tuple parity can false-fail if a
future workload returns rows nondeterministically. That is acceptable at the
skeleton stage and should be revisited when additional HIPRT workloads reach
`PASS`.
