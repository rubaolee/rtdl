# Goal1158: Graph Raw Summary Contract

Date: 2026-04-30

## Scope

Goal1158 is a local pre-cloud optimization for `graph_analytics`. It does not
change RTDL language syntax and does not authorize public RTX speedup wording.

The change targets graph summary mode for:

- `examples/rtdl_graph_bfs.py`
- `examples/rtdl_graph_triangle_count.py`
- the unified `examples/rtdl_graph_analytics_app.py`

## Problem

Before this change, `output_mode="summary"` suppressed JSON row output but still
asked Embree/OptiX to return rows as Python dictionaries before calling the
oracle summarizer. That made the app-level phase contract less clean:

- RT traversal and row production were mixed with Python dict materialization.
- The summary path still paid row materialization overhead even when users only
requested compact counts.
- The RTX cloud gate could not cleanly separate graph RT traversal work from
host-side postprocessing.

## Implementation

The BFS and triangle-count examples now use raw native row views in summary mode:

- Embree summary mode calls `rt.run_embree(..., result_mode="raw")`.
- OptiX summary mode calls `rt.run_optix(..., result_mode="raw")`.
- Native row views are summarized with new oracle helpers:
  - `rt.summarize_bfs_row_view(...)`
  - `rt.summarize_triangle_row_view(...)`
- Raw row views are closed immediately after summarization.
- Existing row mode remains unchanged.
- CPU reference mode remains unchanged.

This is not yet a fully fused graph native reducer. The backend still produces a
native row buffer; the improvement is that Python dict-row materialization is
removed from summary mode.

## Local Evidence

Focused regression suite:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1158_graph_raw_summary_contract_test \
  tests.goal1129_graph_phase_split_contract_test \
  tests.goal903_embree_graph_ray_traversal_test \
  tests.goal904_optix_graph_ray_mode_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test -q

Ran 28 tests in 0.819s
OK
```

Local Embree summary profile for unified graph app:

| Copies | BFS rows | Triangle rows | Raw-view query total | Row materialization | Visibility query |
|---:|---:|---:|---:|---:|---:|
| 2,000 | 4,000 | 2,000 | 0.048744 s | 0.000000 s | 0.018211 s |
| 20,000 | 40,000 | 20,000 | 0.245884 s | 0.000000 s | 0.235541 s |

Prior local observation for `copies=20000` before this change:

- BFS + triangle `query_and_materialize_sec`: approximately `0.307505 s`
- BFS + triangle `native_summary_postprocess_sec`: approximately `0.037143 s`
- Python dict-row materialization was not separated from query timing.

After this change:

- BFS + triangle `query_raw_view_sec`: `0.245884 s`
- BFS + triangle `row_materialization_sec`: `0.0 s`
- Summary postprocess is folded into the raw-view path and no Python dict rows
  are built for BFS/triangle summary mode.

## Boundaries

- This is local macOS Embree evidence plus mocked OptiX contract evidence.
- It does not prove RTX performance.
- It does not promote `graph_analytics` to `public_wording_reviewed`.
- It does not claim whole-app graph acceleration, shortest path acceleration,
  graph database acceleration, or distributed graph analytics acceleration.
- The next RTX pod run should test the native OptiX graph-ray summary path with
  the same raw-view contract.

## Changed Files

- `src/rtdsl/oracle_runtime.py`
- `src/rtdsl/__init__.py`
- `examples/rtdl_graph_bfs.py`
- `examples/rtdl_graph_triangle_count.py`
- `tests/goal1158_graph_raw_summary_contract_test.py`

## Codex Verdict

ACCEPT. Goal1158 is a bounded local graph-app improvement. It removes Python
dict-row materialization from BFS/triangle graph summary mode for Embree and
OptiX raw-view paths, preserves existing correctness tests, and keeps public
RTX wording blocked pending real cloud evidence.
