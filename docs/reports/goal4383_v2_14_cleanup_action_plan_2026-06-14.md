# Goal4383 v2.14 Cleanup Action Plan

Date: 2026-06-14

## Objective

Turn the Goal4382 cross-app audit into execution. The rule is the RTNN lesson:

1. Do not call an app optimized if the RT-core side still pays avoidable host/materialization overhead.
2. Do not call a comparison fair if Embree lacks the same aggregate/summary contract.
3. Do not call a benchmark public-grade if it is only a small toy fixture repeated many times.

## Priority Order

| Priority | Target | Why first | Done condition |
| --- | --- | --- | --- |
| P0 | RTDBSCAN Embree fairness | Current red light: OptiX uses device-column threshold/core flags, Embree materializes threshold rows. This is the closest unresolved twin of the RTNN problem. | Embree has a prepared 3D threshold-count summary/column route that avoids neighbor-row materialization; v2.14 RTDBSCAN rerun uses the same Numba continuation and large data. |
| P1 | RTDBSCAN scale | Current data is 4,096 clustered synthetic points. Existing app evidence already names 65K-1M ranges, so this should be rerun at 100K+ or 262K+ once P0 is fixed. | Fresh OptiX/Embree RTDBSCAN matrix at 100K+ points with same partner continuation and phase breakdown. |
| P2 | Librts large AABB-index | Current result is huge but on 1,024 boxes/queries. | 100K/1M boxes and queries, same all-ops contract, thread sweep for Embree. |
| P3 | Triangle-counting large graph | Current row is a good primitive probe but small graph repeated many times. | Large graph fixture, e.g. 1M+ directed edges, same weighted any-hit summary contract. |
| P4 | Barnes-Hut app-scale | Current node-coverage row has 8,192 bodies but only 4 nodes and excludes force-law work. | Larger tree/node count plus either force-law continuation or explicit primitive-only rename. |
| P5 | RayJoin PIP/overlay paper completeness | PIP still needs the specialized CDB closest-hit face-id route for RayJoin parity; overlay remains 2/8 complete. | Full PIP/LSI/overlay paper datasets, 8/8 overlay inputs, author-code comparison separated from RTDL-vs-Embree. |
| P6 | Hausdorff real/large point clouds | Current 4,096 x 4,096 synthetic copies are useful but not app-scale. | 65K/262K point-cloud pairs or real point-cloud datasets under exact threshold contract. |
| P7 | Contact/robot data diversity | Current rows are mostly acceptable but synthetic. | Add at least one non-grid/contact-derived and one larger robot scene/full-loop row. |

## P0 Implementation Plan

Add a generic Embree 3D prepared fixed-radius count-threshold route that returns compact per-query threshold-count columns or an aggregate summary without materializing neighbor rows.

Minimum acceptable native contract:

- Inputs: prepared 3D search points, query points, radius, threshold.
- Outputs: one compact row/column per query with `query_id`, threshold-capped `neighbor_count`, and `threshold_reached`.
- No neighbor rows.
- Prepared search scene reused across repeats.
- Per-worker temporary state reused where possible.

Preferred app integration:

- Add a Python `PreparedEmbreeFixedRadiusCountThreshold3D` wrapper.
- Add `prepare_embree_fixed_radius_count_threshold_3d(...)`.
- Add `run_count_threshold_raw(...)` or a host-column equivalent.
- Update RTDBSCAN `embree_core_flags_numba_prepared_grid_column_signature_3d` to use the prepared 3D threshold route instead of `rt.run_embree(...)`.
- Preserve the same Numba continuation used by the OptiX comparison.

This still uploads compact counts/flags from host to Numba because Embree is CPU-side. That is fair: CPU cores produce host columns; the shared Numba continuation then consumes device columns after a measured upload. The unfair part to eliminate is threshold-row materialization and scene rebuild.

## P0 Tests

- Native/API contract test: Embree 3D threshold symbol exposed in prelude/runtime.
- RTDBSCAN static contract test: Embree mode no longer calls `rt.run_embree(...)`/threshold-capped rows in the prepared grid column-signature path.
- Local smoke if native library is available.
- Pod run after compile:
  - Small parity: 4,096 clustered3d, repeat 3.
  - Large: 65,536 or 262,144 clustered3d, repeat chosen for 1-10s per side.

## Public Wording Rule

Until P0 and P1 pass, RTDBSCAN remains:

> Useful engineering signal, not a clean backend-only public claim.

After P0/P1 pass, wording can become:

> Same RTDL fixed-radius threshold/core-flag contract with fixed Numba continuation; the material difference is OptiX RT traversal/device output versus Embree CPU traversal/host compact columns plus measured column upload.

