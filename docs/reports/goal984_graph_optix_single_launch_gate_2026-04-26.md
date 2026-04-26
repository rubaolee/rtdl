# Goal984 Graph OptiX Single-Launch Gate

Date: 2026-04-26

Goal984 changes the next graph OptiX cloud gate from chunked visibility execution to a single visibility launch by default. It does not authorize public RTX speedup claims.

## Motivation

Goal982 showed the current graph RTX artifact is slower than the same-scale Embree baseline:

- A5000 graph RTX visibility phase: `1.5830601840279996` seconds.
- Same-scale local Embree graph baseline: `0.5672194170765579` seconds.
- Baseline / RTX ratio: `0.358305655589987`.

Inspection of the cloud artifact showed visibility was run as `200` chunks of `100` copies for a `copies=20000` gate. That likely inflated launch/setup overhead. The graph fixture already uses explicit candidate edges via `visibility_pair_rows`, so the old chunking is no longer needed to avoid an observer-target Cartesian product.

## Change

- `scripts/goal889_graph_visibility_optix_gate.py` now uses `--chunk-copies 0` as the default, meaning one visibility launch.
- Positive `--chunk-copies N` still runs chunked diagnostics.
- The Goal759 graph manifest command now passes `--chunk-copies 0`.
- The Goal914 targeted graph/Jaccard rerun driver now defaults `--graph-chunk-copies 0`.
- The Goal914 validation now allows `0` for graph chunking; positive Jaccard chunk sizes remain required.
- The RTX cloud runbook now documents the single-launch graph command.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal889_graph_visibility_optix_gate_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal914_rtx_targeted_graph_jaccard_rerun_test
```

Result:

```text
Ran 22 tests in 0.330s
OK
```

Additional focused tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal982_graph_same_scale_timing_repair_test \
  tests.goal978_rtx_speedup_claim_candidate_audit_test \
  tests.goal903_embree_graph_ray_traversal_test
```

Result:

```text
Ran 13 tests in 1.924s
OK
```

## Boundary

This is a pre-cloud optimization. It prepares the next pod run to measure a lower-overhead OptiX graph visibility path, but it does not prove a speedup. Goal978 continues to reject the current graph public speedup claim until a new cloud artifact proves otherwise and passes separate 2-AI claim review.
