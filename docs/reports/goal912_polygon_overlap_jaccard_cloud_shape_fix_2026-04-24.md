# Goal912: Polygon Overlap/Jaccard Cloud-Shape Fix

Date: 2026-04-24

## Problem

Goal910 showed that the polygon overlap/Jaccard group was not ready for a
large 20k-copy cloud run:

- `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` passed at reduced
  1k scale;
- the 20k path hit CUDA driver OOM / `needs_optix_runtime`;
- the profiler still built CPU reference payloads and full row digests before
  the large OptiX path could be judged cleanly.

That shape wastes paid RTX time and can exhaust memory before producing useful
candidate-discovery evidence.

## Changes

- `scripts/goal877_polygon_overlap_optix_phase_profiler.py` now supports:
  - `--output-mode rows|summary`
  - `--validation-mode full_reference|analytic_summary|none`
  - `--chunk-copies N`
- The old exact row/full-reference behavior remains the default.
- The cloud-safe mode is:

```text
--output-mode summary --validation-mode analytic_summary --chunk-copies 100
```

- In analytic summary mode, the profiler skips the large CPU reference and uses
  deterministic copied-fixture expectations:
  - pair overlap: `2 * copies` overlap rows, intersection area `5 * copies`,
    union area `19 * copies`;
  - Jaccard: intersection area `5 * copies`, left area `13 * copies`, right
    area `11 * copies`, union area `19 * copies`, Jaccard `5 / 19`.
- Summary-mode OptiX candidate discovery is chunked, so future cloud runs do
  not materialize one global 20k-copy row payload.
- Goal759 now sends both deferred polygon entries to the summary/analytic
  command shape.
- Goal762 extracts `output_mode`, `validation_mode`, and `chunk_copies` for
  polygon artifacts and checks those fields in the cloud contract.

## Local Verification

Focused tests passed:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal877_polygon_overlap_optix_phase_profiler_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal762_rtx_cloud_artifact_report_test -v

Ran 29 tests in 0.419s
OK
```

Compile check passed:

```text
PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal877_polygon_overlap_optix_phase_profiler.py \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  scripts/goal762_rtx_cloud_artifact_report.py
```

Local no-OptiX 20k command-shape checks fail fast with `FileNotFoundError`
because macOS has no local OptiX runtime:

```text
PYTHONPATH=src:. python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py \
  --app pair_overlap --mode optix --copies 20000 \
  --output-mode summary --validation-mode analytic_summary --chunk-copies 100 \
  --output-json build/goal912_pair_overlap_local_no_optix.json

PYTHONPATH=src:. python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py \
  --app jaccard --mode optix --copies 20000 \
  --output-mode summary --validation-mode analytic_summary --chunk-copies 100 \
  --output-json build/goal912_jaccard_local_no_optix.json
```

Both artifacts record:

- `status: needs_optix_runtime`
- `validation_mode: analytic_summary`
- `output_mode: summary`
- `cpu_reference_sec: null`
- `optix_candidate_discovery_sec: null`
- `error.type: FileNotFoundError`

## Claim Boundary

This is a pre-cloud shape fix. It does not prove polygon overlap/Jaccard RTX
performance and does not authorize full-app speedup claims. It only makes the
next RTX cloud run target the RT candidate-discovery phase without large CPU
reference or row-payload materialization first.

The allowed claim scope remains:

- OptiX native-assisted LSI/PIP candidate discovery for bounded polygon-pair
  overlap;
- OptiX native-assisted LSI/PIP candidate discovery for bounded polygon-set
  Jaccard.

Exact area/Jaccard refinement remains CPU/Python-owned.

## Review

Two-AI consensus is recorded in:

- `docs/reports/goal912_claude_review_2026-04-24.md`
- `docs/reports/goal912_gemini_review_2026-04-24.md`
- `docs/reports/goal912_two_ai_consensus_2026-04-24.md`

## Next

On the next RTX pod, rerun only the regenerated Goal759 deferred polygon
commands first. Then run Goal762 artifact extraction and send the artifacts for
2+ AI review before promoting readiness.
