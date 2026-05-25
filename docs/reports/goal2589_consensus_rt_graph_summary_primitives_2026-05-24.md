# Goal2589 Consensus: RT-Graph Summary Primitives

Date: 2026-05-24

Status: accepted for internal benchmark-app continuation. This consensus does
not authorize public speedup claims.

## Scope

Goal2589 added app-agnostic OptiX scalar summary paths for the RT-Graph
triangle-counting benchmark:

- `PREPARED_TRIANGLE_SCENE_3D_RAY_ANY_HIT_WEIGHTED_SUM_V1`
- `PREPARED_TRIANGLE_SCENE_3D_RAY_HIT_COUNT_SUM_V1`

The benchmark maps graph relations to generic 3-D rays, triangles, optional
ray weights, and scalar reductions in Python. The native engine does not
contain graph, vertex, edge, triangle-counting, 1A2, or 2A1 vocabulary.

## Evidence Reviewed

- Local focused contract tests passed:
  `PYTHONPATH=src:. python3 -m unittest tests.goal2589_rt_graph_triangle_contract_test tests.goal2586_triangle_counting_benchmark_boundary_test`
- Local syntax and diff checks passed:
  `python3 -m py_compile ...` and `git diff --check`
- Pod focused contract test passed on `fc75fca4648a` using the working key
  `~/.ssh/id_ed25519_rtdl_codex`.
- Pod OptiX library exported both new summary symbols:
  `rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum` and
  `rtdl_optix_static_triangle_scene_3d_ray_hit_count_sum`.
- The pod tree was a synced working tree, not a clean Git checkout; this is
  acceptable for internal engineering evidence but not release-grade clean
  commit evidence.

## Review Results

| Reviewer | File | Verdict | Key point |
| --- | --- | --- | --- |
| Codex | `docs/reports/goal2589_rt_graph_triangle_counting_pod_evidence_2026-05-24.md` | Accept | Correct same-input behavior and honest performance boundary. |
| Gemini | `docs/reports/goal2589_gemini_review_rt_graph_summary_primitives_2026-05-24.md` | ACCEPT | New APIs are app-agnostic and performance interpretation is bounded. |
| Claude | `docs/reports/goal2589_claude_review_rt_graph_summary_primitives_2026-05-24.md` | ACCEPT | Kernel semantics, host/device ABI, and claim boundaries are sound. |

## Consensus

The new summary primitives are acceptable as generic RTDL engine behavior. They
remove the row-materialization failure mode for triangle-counting summary
queries without introducing app-specific native semantics.

The benchmark can claim internally that RTDL expresses both RT-Graph paper
decompositions through generic ray/triangle summaries and matches authors/oracle
counts on deterministic same-input fixtures. It cannot claim public speedups,
paper dataset reproduction, or whole-app parity with the authors code.

## Remaining Work

The next optimization target is not RT traversal. Current pod evidence shows
native traversal is already in the same rough order as authors trace timings on
the controlled K4 workloads, while whole-app time remains dominated by Python
graph contract construction and Python-to-native lowering. Future work should
focus on prepared query buffers, lower-copy or zero-copy column inputs, and
partner-resident preprocessing.

## Follow-Up Note

A post-consensus optimization pass kept the accepted native primitive boundary
unchanged. The changes were limited to generic host `uint64` weight packing,
benchmark-owned vectorized 1A2 lowering, and skipping unused id-ascending
adapter materialization in RT summary modes. Pod tests and deterministic random
same-input probes passed after the change. The claim boundary remains the same:
this is internal benchmark evidence, not public speedup wording.

## Partner Follow-Up Note

A second follow-up added an optional CuPy partner path for the app-owned
RT-Graph summary contract. This path builds the directed CSR, duplicate-aware
2-hop summary rays, and oracle count in CuPy, then hands generic RTDL
ray/triangle inputs to the already accepted summary primitives. It does not add
graph, triangle-counting, 1A2, or 2A1 semantics to the native engine.

The pod CuPy test passed with no skips and compared the GPU-built contract
against the Python contract on both clean and cleanup-heavy fixtures. On K4 x
100,000, RTDL+CuPy reduced total app time from multi-second no-partner rows to
`162.544 ms` for 2A1 and `171.575 ms` for 1A2. This is recorded as internal
partner-design evidence, not as a new externally reviewed consensus result. Any
public performance wording still requires a fresh review focused on the CuPy
partner comparison and timing-contract boundary.
