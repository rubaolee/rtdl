# Goal2851 Barnes-Hut Harness Progress Logging

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

During Goal2847, the Barnes-Hut canonical harness spent about 342 seconds in
the 8,192-body case before printing another line. The process was active, but
the harness looked stuck from the outside. Goal2851 fixes that operational
problem by adding backend/repeat progress messages around the expensive
Embree/OptiX sub-runs.

## Implementation

Updated:

- `scripts/goal2642_barnes_hut_embree_vs_optix_lowering_perf.py`
- `scripts/goal2803_barnes_hut_v25_consolidated_harness.py`

The underlying `run_case(...)` now accepts an optional `progress_callback`.
Goal2803 passes a callback that prints to `sys.__stdout__` with a `stderr`
fallback, which means progress remains visible even while `stdout` is
redirected around the suppressed per-case JSON.

The new messages are shaped like:

```text
[goal2803] membership case 3/3 progress: backend=embree repeat=1/3 start
[goal2803] membership case 3/3 progress: backend=embree repeat=1/3 done sec=...
```

## Boundary

This is not a performance change, not a public speedup claim, and not a release
authorization. It only improves observability for long-running pod harnesses.
The harness output and JSON payload semantics remain unchanged.

## Validation

Local static guard:

```text
py -3 -m unittest tests.goal2851_barnes_hut_harness_progress_logging_test

Ran 3 tests in 0.017s
OK
```

The pod smoke validation ran a tiny Barnes-Hut case and confirmed that the
progress lines appear before completion while the per-case JSON remains
suppressed:

```text
commit: 80d4c561b900d75398414662dc66ee0a3c9a02b8
command:
python3 -u scripts/goal2803_barnes_hut_v25_consolidated_harness.py \
  --case 64:8 \
  --repeats 1 \
  --vector-group-count 16 \
  --vector-rows-per-group 2 \
  --vector-warmups 0 \
  --output /tmp/goal2851_barnes_hut_progress_smoke_v2.json

observed progress:
[goal2803] membership case 1/1 progress: backend=embree repeat=1/1 start
[goal2803] membership case 1/1 progress: backend=embree repeat=1/1 done sec=0.046
[goal2803] membership case 1/1 progress: backend=optix repeat=1/1 start
[goal2803] membership case 1/1 progress: backend=optix repeat=1/1 done sec=0.801

result:
[pod2851b] status pass rows 1 vector pass
source_commit 80d4c561b900d75398414662dc66ee0a3c9a02b8
source_dirty []
```

Post-review full canonical validation also ran on the real default Goal2803
case set:

```text
commit: c12fae04d28aeb21b7f81d2b36356bfefa7fe521
command:
timeout 900s python3 -u scripts/goal2803_barnes_hut_v25_consolidated_harness.py \
  --output /tmp/goal2851_barnes_hut_full_progress_validation.json

large-case progress:
[goal2803] membership case 3/3 progress: backend=embree repeat=1/3 start
[goal2803] membership case 3/3 progress: backend=embree repeat=1/3 done sec=97.702
[goal2803] membership case 3/3 progress: backend=embree repeat=2/3 start
[goal2803] membership case 3/3 progress: backend=embree repeat=2/3 done sec=97.141
[goal2803] membership case 3/3 progress: backend=embree repeat=3/3 start
[goal2803] membership case 3/3 progress: backend=embree repeat=3/3 done sec=94.271
[goal2803] membership case 3/3 progress: backend=optix repeat=1/3 start
[goal2803] membership case 3/3 progress: backend=optix repeat=1/3 done sec=22.111
[goal2803] membership case 3/3 progress: backend=optix repeat=2/3 start
[goal2803] membership case 3/3 progress: backend=optix repeat=2/3 done sec=19.001
[goal2803] membership case 3/3 progress: backend=optix repeat=3/3 start
[goal2803] membership case 3/3 progress: backend=optix repeat=3/3 done sec=18.594

result:
[pod2851full] status pass rows 3
min_speedup 8.550645619613132
max_speedup 157.219054168451
source_commit c12fae04d28aeb21b7f81d2b36356bfefa7fe521
source_dirty []
```

## Codex Verdict

`accept-with-boundary`
