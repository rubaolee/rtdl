# Goal911: Graph Gate Cloud-Shape Fix

Date: 2026-04-24

## Problem

The Goal910 RTX A5000 grouped run showed that Group F was not a useful cloud
benchmark:

- the 20k-copy graph gate was stopped after `155.9s`;
- the process was CPU-bound before visible GPU execution;
- a smaller direct 1k-copy attempt also stayed CPU-bound;
- therefore the artifact was correctly recorded as blocked, not RTX evidence.

The local root cause was twofold:

1. `scripts/goal889_graph_visibility_optix_gate.py` ran all CPU reference
   scenarios before attempting OptiX, so cloud time could be spent before the
   RT path was even reached.
2. The `visibility_edges` fixture passed all copied observers and targets into
   `rt.visibility_rows`, which forms the global observer-target cross-product.
   That makes the copied fixture effectively `O(copies^2)` for visibility rows.

At `copies=20000`, this shape is not a valid cloud gate.

## Changes

- The graph gate now runs OptiX records first.
- Summary-mode strict validation defaults to `--validation-mode analytic_summary`
  rather than CPU-reference-first validation.
- Visibility summary execution is chunked with `--chunk-copies`; the manifest
  uses `--chunk-copies 100`.
- Full CPU-reference validation remains available with
  `--validation-mode full_reference`.
- Rows output rejects analytic validation because row digests require actual
  row materialization.
- `examples/rtdl_graph_bfs.py` and
  `examples/rtdl_graph_triangle_count.py` now expose `row_count` in summary
  payloads, so summary parity can be checked without retaining rows.
- Goal762 artifact extraction now understands analytic graph validation records
  and uses all graph record labels as contract phase sources, so future
  visibility/BFS/triangle artifacts are not falsely marked missing when the
  records are present.
- The Goal759 cloud manifest now records the safer graph command:

```text
python3 scripts/goal889_graph_visibility_optix_gate.py
  --copies 20000
  --output-mode summary
  --validation-mode analytic_summary
  --chunk-copies 100
  --strict
  --output-json docs/reports/goal889_graph_visibility_optix_gate_rtx.json
```

## Local Verification

Focused tests passed:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal889_graph_visibility_optix_gate_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal738_graph_app_scaled_summary_test \
  tests.goal904_optix_graph_ray_mode_test -v

Ran 36 tests in 0.443s
OK
```

Compile/checks passed:

```text
PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal889_graph_visibility_optix_gate.py \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  scripts/goal762_rtx_cloud_artifact_report.py \
  examples/rtdl_graph_bfs.py \
  examples/rtdl_graph_triangle_count.py

git diff --check
```

Local no-OptiX behavior was checked at the same 20k command shape. It fails
quickly with explicit missing-OptiX records, rather than spending minutes in
CPU reference work:

```text
status: fail
strict_failures:
- optix_visibility_anyhit did not run
- optix_native_graph_ray_bfs did not run
- optix_native_graph_ray_triangle_count did not run
```

## Claim Boundary

This is a pre-cloud shape fix. It does not prove graph RTX performance and does
not authorize a graph RT-core speedup claim. It only makes the next cloud run
more likely to reach the intended RT traversal path quickly and preserve a
phase-clean artifact.

## Review

Two-AI consensus is recorded in:

- `docs/reports/goal911_claude_review_2026-04-24.md`
- `docs/reports/goal911_gemini_review_2026-04-24.md`
- `docs/reports/goal911_two_ai_consensus_2026-04-24.md`

## Next

Run only the graph group on the next RTX pod using the regenerated manifest
command. If it passes, then run Goal762 artifact extraction and send the artifact
for 2+ AI review before promoting graph readiness.
