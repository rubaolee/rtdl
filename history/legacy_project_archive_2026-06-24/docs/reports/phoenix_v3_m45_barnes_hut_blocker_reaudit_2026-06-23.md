# Phoenix V3 M45 Barnes-Hut Blocker Re-Audit

Date: 2026-06-23

Status: `m45_barnes_hut_focused_fix_covered_pending_full_suite_validation_not_release`

This is a read-only re-audit started from the M44 recommendation. It does not
authorize V3 release, all-app benchmarking, paid POD spend, public speedup
wording, broad V3-over-V2 claims, V4 work, embedding, C ABI, or true-zero-copy
claims.

## Bottom Line

Barnes-Hut should not be treated as an immediate new coding target. The frozen
all-app scorecard still shows Barnes-Hut as the visible severe-regression app,
but prior focused work already diagnosed and patched the controlling OptiX
prepared-query regression through a generic prepared-query residency surface.

The correct classification after this re-audit is:

```text
Barnes-Hut = focused-fix-covered for planning, pending next reviewed full-suite validation
```

The remaining Barnes-Hut work is validation and scorecard carry-forward, not
more route tuning.

## Frozen Scorecard Rows

The frozen all-app scorecard contains six Barnes-Hut rows:

| Row | Backend | Frozen V3 vs V2.14 |
| --- | --- | ---: |
| `goal2626_large / barnes_hut_embree_node_coverage` | Embree | `1.0159569894948057x` |
| `goal2626_large / barnes_hut_optix_node_coverage` | OptiX | `0.6217023860571815x` |
| `goal2636_stress / barnes_hut_embree_node_coverage_bodies_131072` | Embree | `1.006668758835713x` |
| `goal2636_stress / barnes_hut_optix_node_coverage_bodies_131072` | OptiX | `0.9614474083364788x` |
| `goal2636_stress / barnes_hut_embree_node_coverage_bodies_32768` | Embree | `1.0018265554211925x` |
| `goal2636_stress / barnes_hut_optix_node_coverage_bodies_32768` | OptiX | `0.5910153814336409x` |

The severe regression is therefore concentrated in the OptiX node-coverage
prepared-query rows, especially the 32768 and goal2626-large rows. Embree is
near parity.

## Prior Focused Fix

M24 diagnosed the root cause:

- Native OptiX traversal was not the problem.
- The benchmark mixed Python point packing into a cold/non-prepacked prepared
  query metric.
- The fix productized a generic prepared fixed-radius query-payload surface:
  `GenericPreparedFixedRadiusCountThreshold2D.prepare_query_points(...)`.
- Both OptiX and Embree prepared paths can accept caller-prepared `PackedPoints`.

M24 evidence showed the focused stress rows cleared after the fix. Claude
reviewed M24 with verdict `accept_with_boundary`, requiring honest boundary
wording around single-query prepare cost.

M24 follow-up review then accepted gates 1-3:

- post-fix Barnes-Hut focused geomean over the blocker rows was above the
  `0.900x` severe-regression floor;
- single-query prepare penalty was documented;
- release-facing wording gate passed.

Remaining M24 process item was Codex consensus / carry-forward discipline, not
more Barnes-Hut implementation.

## M7 Blocker Intake Projection

The M7 Barnes-Hut blocker intake records the all-app-scorecard projection after
the focused generic fix:

| Row | Frozen speedup | Focused patched speedup |
| --- | ---: | ---: |
| `goal2626_large / barnes_hut_embree_node_coverage` | `1.016x` | `1.032x` |
| `goal2626_large / barnes_hut_optix_node_coverage` | `0.622x` | `0.999x` |
| `goal2636_stress / barnes_hut_embree_node_coverage_bodies_131072` | `1.007x` | `1.006x` |
| `goal2636_stress / barnes_hut_optix_node_coverage_bodies_131072` | `0.961x` | `0.990x` |
| `goal2636_stress / barnes_hut_embree_node_coverage_bodies_32768` | `1.002x` | `0.990x` |
| `goal2636_stress / barnes_hut_optix_node_coverage_bodies_32768` | `0.591x` | `1.038x` |

M7 projected:

- Barnes-Hut app geomean after focused fix: `1.008971x`
- all-row geomean if only Barnes-Hut rows supersede: `1.032810x`

M7 explicitly states this is planning evidence pending next reviewed full-suite
validation, not release evidence.

## M28/M29 Surface Boundary

M28/M29 address a different Barnes-Hut route:

```text
generic aggregate-tree fused weighted-vector sum 2D,
explicit Numba CUDA partner,
routed through prepared_execution_session_runner
```

That route is a V3 capability/productization addition and runner-parity proof,
not a same-contract V3-over-v2.14 speedup claim:

- current runner vs current fused-control geomean: `0.999328x`
- v2.14 lacks the current Numba CUDA fused route and prepared-execution session
  runner surface
- M29 classification: `v2_14_has_cpu_fused_or_typed_stream_only`

Therefore M28/M29 should not be used to claim that Barnes-Hut as an app is
fixed. They are relevant as runtime-trunk capability evidence, while M24/M7 are
the relevant blocker-fix evidence for the frozen OptiX node-coverage rows.

## Re-Audit Classification

M45 classification:

```text
active_coding_target: false
focused_fix_covered_for_planning: true
pending_full_suite_validation: true
next_pod_authorized: false
release_authorized: false
```

Reason:

- The frozen severe regression rows are known.
- The root cause is already diagnosed.
- The generic fix is already implemented and reviewed with boundary.
- Replacement-row projection removes the Barnes-Hut severe regression for
  planning.
- Another Barnes-Hut coding round would likely repeat the old leaf-first error.

## Next Engineering Implication

Do not start a new Barnes-Hut performance-tuning branch now.

The next local work should instead target one of the remaining scorecard
blockers that is not already focused-fix-covered:

1. LibRTS Set-B parity/control row below `0.95x`; or
2. another Set-A app-win shortfall that can be improved through a reusable
   runtime primitive rather than app-specific code.

Before any full-suite/all-app POD run, the scorecard packet must explicitly
carry M24/M7 as Barnes-Hut focused-fix-covered pending validation, and must not
pretend the old frozen `0.844x` value is current post-fix performance.

## Non-Authorization

This report does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- public speedup wording
- broad V3-over-V2 claim
- V4 work
- embedding
- C ABI
- true zero-copy claim

## Goal-Level Decision Audit

Decision: classify Barnes-Hut as focused-fix-covered pending full-suite
validation, not as the next active coding target.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   to see the frozen `0.844x` app geomean and start coding Barnes-Hut again
   without reading the M24/M7 fix history.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Treat M44's Barnes-Hut recommendation as an audit first, not an
   implementation order. That is what this report does.
4. Can I now try a different path that actually solves the problem? Yes. Move
   the next active local engineering target away from Barnes-Hut and toward
   remaining un-covered scorecard blockers, while preserving Barnes-Hut as a
   validation row for the future reviewed full-suite run.
