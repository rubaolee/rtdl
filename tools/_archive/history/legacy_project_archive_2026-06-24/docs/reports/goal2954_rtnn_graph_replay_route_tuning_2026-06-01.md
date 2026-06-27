# Goal2954: RTNN Graph Replay Route Tuning

Date: 2026-06-01
Status: pod route sweep passed; clean canonical harness passed

## Purpose

The post-Goal2952 packet triage removed Hausdorff from the current weak-row
set, but exposed one remaining RTNN performance target: the uniform 65,536
point row was slower than the same-contract CuPy grid opponent.

Goal2954 checks whether this is a missing primitive/runtime feature or a route
selection problem. The answer is route selection: the existing generic prepared
query CUDA graph replay path is the right route for the repeated RTNN canonical
harness.

## Pod Evidence

Pod target: `root@69.30.85.171 -p 22167`

Source commit for sweeps: `3a5cc1ac6a65d9b18cc4ae325210bdc5c6503679`

Source commit for clean canonical harness confirmation:
`67b6dc3ea2dbc31efd944b6d6834845b0a48fe63`

Artifacts:

- `docs/reports/goal2954_rtnn_graph_replay_sweep_pod/goal2954_rtnn_uniform_mode_sweep.json`
- `docs/reports/goal2954_rtnn_graph_replay_sweep_pod/goal2954_rtnn_graph_all_distributions.json`
- `docs/reports/goal2954_rtnn_graph_replay_sweep_pod/goal2954_clean_rtnn_graph_harness.json`

Uniform route sweep, 65,536 query/search points, radius `0.02`, `k=50`,
repeat `13`:

| RTDL route | Median sec | CuPy/RTDL ratio |
| --- | ---: | ---: |
| prepared search aggregate f32 | `0.000591` | `0.233x` |
| prepared-query aggregate f32 | `0.000155` | `0.891x` |
| prepared-query batched aggregate f32 | `0.000165` | `0.834x` |
| prepared-query batch CUDA graph replay f32 | `0.000126` | `1.091x` |
| same-stream CuPy continuation | `0.000391` | `0.352x` |

The same graph replay route was then checked across the canonical RTNN
distributions:

| Distribution | RTDL graph replay sec | CuPy grid sec | CuPy/RTDL ratio |
| --- | ---: | ---: | ---: |
| uniform | `0.000116` | `0.000138` | `1.187x` |
| clustered | `0.017139` | `0.047067` | `2.746x` |
| shell | `0.000375` | `0.002715` | `7.241x` |

Clean canonical harness confirmation at commit `67b6dc3e`:

| Distribution | RTDL graph replay sec | CuPy grid sec | CuPy/RTDL ratio |
| --- | ---: | ---: | ---: |
| uniform | `0.000124` | `0.000137` | `1.104x` |
| clustered | `0.017253` | `0.046959` | `2.722x` |
| shell | `0.000354` | `0.002723` | `7.684x` |

All rows preserve the same ranked-summary aggregate contract:

- bounded neighbor count matches CuPy exactly;
- nearest and kth checksums match CuPy exactly;
- sum-distance differs only by expected float32 accumulation tolerance;
- `upload` remains `0.0` in the native phase timing;
- no neighbor row materialization is introduced.

## Change

`scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py` now uses:

```text
ranked-summary-aggregate-prepared-query-batch-graph-float32
```

and the harness version is:

```text
rtdl.goal2800.rtnn_v2_5_live_ranked_summary_harness.v8.scale65536_repeat9_graph_replay
```

This is a generic runtime route change over the fixed-radius ranked-summary
aggregate primitive family. It does not add RTNN-specific native code.

## Boundary

This goal does not authorize public speedup, whole-app speedup, broad RT-core,
RTNN-paper reproduction, or v2.5 release claims. It only records that, for the
current canonical RTNN same-contract CuPy comparison, the existing graph replay
route removes the remaining uniform weak row and improves all three measured
distributions.
