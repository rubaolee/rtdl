# Goal1159: Graph RTX Gate Phase Metadata

Date: 2026-04-30

## Scope

Goal1159 updates the existing graph RTX gate packet so the next cloud artifact
captures the phase evidence needed after Goal1158. It does not run OptiX locally
and does not authorize public RTX wording.

## Problem

The graph gate (`scripts/goal889_graph_visibility_optix_gate.py`) previously
recorded total elapsed seconds and output digests for:

- `optix_visibility_anyhit`
- `optix_native_graph_ray_bfs`
- `optix_native_graph_ray_triangle_count`

That was enough for parity, but too coarse for the current v1.0 app-performance
work. After Goal1158, the key question is whether the OptiX graph summary path
uses the raw-view contract and avoids Python dict-row materialization. The old
artifact schema did not preserve section-level phase fields.

## Implementation

The gate now records, for each successful OptiX graph record:

- `section_run_phases`
- `native_continuation_active`
- `native_continuation_backend`
- `row_count`
- `row_materialization_sec`
- `query_raw_view_sec`

For chunked visibility runs, the script aggregates per-chunk phase totals and
native-continuation metadata across all chunks.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal889_graph_visibility_optix_gate_test \
  tests.goal1158_graph_raw_summary_contract_test \
  tests.goal1129_graph_phase_split_contract_test -q

Ran 16 tests in 0.164s
OK
```

Local no-OptiX execution remains conservative:

```text
PYTHONPATH=src:. python3 scripts/goal889_graph_visibility_optix_gate.py \
  --copies 2 \
  --output-mode summary \
  --validation-mode analytic_summary \
  --chunk-copies 1 \
  --output-json /tmp/goal889_graph_phase_packet.json

status: non_strict_recorded_gaps
strict_pass: false
```

Because macOS has no OptiX runtime, unavailable OptiX records correctly do not
contain phase metadata. Mocked tests verify the metadata exists on successful
records.

## Boundaries

- This is an artifact-schema and local test update.
- It is not an RTX performance result.
- It does not promote `graph_analytics` public wording.
- It prepares the next consolidated pod run to answer whether BFS/triangle
  graph-ray summary paths avoid Python dict-row materialization on real OptiX.

## Changed Files

- `scripts/goal889_graph_visibility_optix_gate.py`
- `tests/goal889_graph_visibility_optix_gate_test.py`

## Codex Verdict

ACCEPT. The graph RTX gate now preserves the phase metadata needed for a serious
cloud rerun, while keeping missing-OptiX and public-claim boundaries intact.
