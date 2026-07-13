# Goal4826 County x Zipcode Current-Line Revalidation After Goal4820 Core Fix

Date: 2026-06-30

## Purpose

Goal4826 revalidated the old Goal4806 County x Zipcode byte-equality clue under
the current repaired RTDL product line.

This is not V4 continuation. The run used the current Goal4820 repair tree on
the POD and reused only old data/artifact paths from Goal4806.

## Input

POD:

```text
host: e7820d339c40
gpu: NVIDIA RTX 4000 Ada Generation
tree: /workspace/rtdl_goal4820_sos_fix
native lib: /workspace/rtdl_goal4820_sos_fix/build/librtdl_optix.so
```

Dataset:

```text
dataset_root: /workspace/rayjoin_section57_same_source_cdb
left:  /workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb
right: /workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb
left bytes: 904,529,353
right bytes: 2,603,929,396
input_provenance: same_source_regenerated_cdb
```

Author baseline file reused only as a byte-comparison target:

```text
/workspace/rtdl_goal4806_fast_min/artifacts/section57_author_output_debug/author_overlay_debug.overlay.txt
```

## First Current-Line Run: Product Gap Exposed

The first current-line full-output run failed before producing output:

```text
RuntimeError: RayJoin CDB point-location query points must be finite
```

The failure occurred during midpoint PIP, after LSI and vertex PIP had already
started the full overlay pipeline.

## Diagnosis

Diagnostic artifact copied locally:

`history/internal_docs/goal4826_midpoint_finiteness_probe.json`

Key findings:

| Metric | Value |
|---|---:|
| LSI rows | `965,844` |
| nonfinite LSI rows | `69` |
| map0 midpoint candidates | `123,082` |
| map0 nonfinite midpoints | `26` |
| map1 midpoint candidates | `141,510` |
| map1 nonfinite midpoints | `24` |

This means the failure was not merely a local list bug. The current overlay
route can materialize nonfinite intersection coordinates, and those can produce
nonfinite midpoint query points.

## Product/Core Repair Made During Goal4826

A small, product-level finite-query repair was made:

- `_midpoint_points_from_lsi_rows_numpy` now drops nonfinite midpoint query
  points and records `map{0,1}_nonfinite_midpoints_dropped`.
- `_midpoints_for_sorted_xsects` applies the same finite filter for the
  full-output owner path, keeping midpoint owners synchronized with the
  filtered midpoint list.
- `run_rayjoin_overlay_rtdl` output now records dropped midpoint counts in
  `midpoint_pip`.

This is not a RayJoin-specific shortcut. It enforces the general product
invariant that native point-location kernels must not receive NaN/Inf query
points.

Regression tests added:

- `test_lsi_midpoint_projection_drops_nonfinite_points_with_telemetry`
- `test_output_chain_midpoint_projection_drops_nonfinite_points_with_telemetry`

Verification:

```text
local: py -m unittest tests.goal4374_rayjoin_exact_paper_suite_test tests.goal4373_rayjoin_cdb_point_location_route_test
result: 30 tests OK

POD: PYTHONPATH=src python3 -m unittest tests.goal4374_rayjoin_exact_paper_suite_test tests.goal4373_rayjoin_cdb_point_location_route_test
result: 30 tests OK
```

## Second Current-Line Run After Finite Filter

Command:

```bash
cd /workspace/rtdl_goal4820_sos_fix
export RTDL_OPTIX_LIB=/workspace/rtdl_goal4820_sos_fix/build/librtdl_optix.so
export PYTHONPATH=src
python3 scripts/rayjoin_paper_reproduction_suite.py run-rtdl \
  --dataset-root /workspace/rayjoin_section57_same_source_cdb \
  --case-id overlay_county_zipcode \
  --backend optix \
  --warmup 0 \
  --repeat 1 \
  --assemble-overlay-output \
  --overlay-output artifacts/goal4826_county_zipcode_current_revalidation/rtdl_current_overlay_county_zipcode_optix_after_finite_filter.txt \
  --input-provenance same_source_regenerated_cdb \
  --output-json artifacts/goal4826_county_zipcode_current_revalidation/rtdl_current_overlay_county_zipcode_optix_after_finite_filter.json
```

Local JSON artifact copied from POD:

`history/internal_docs/goal4826_rtdl_current_overlay_county_zipcode_optix_after_finite_filter.json`

Output:

```text
/workspace/rtdl_goal4820_sos_fix/artifacts/goal4826_county_zipcode_current_revalidation/rtdl_current_overlay_county_zipcode_optix_after_finite_filter_optix.txt
```

## Result

The run completed, but byte-equality failed.

| Item | Current RTDL output | Author baseline |
|---|---:|---:|
| SHA256 | `5a1808def771992e6532bbd1edd05a9625531b9e39a235578a11b5e29c395267` | `e8fed3e7e4691c028ee6c8e8a16a74eb06de5a0ffb20cc2b132ce8646b797b2a` |
| bytes | `2,388,737,142` | `2,390,767,769` |
| byte equal | `false` | `false` |

Current RTDL output summary:

| Metric | Value |
|---|---:|
| total_sec | `404.76801423728466` |
| pack_inputs_sec | `61.77191745489836` |
| LSI intersections | `965,844` |
| output chain count | `29,253,910` |
| face count | `115,515` |
| map0 midpoints in map1 | `123,056` |
| map0 nonfinite midpoints dropped | `26` |
| map0 positive midpoint faces | `97,937` |
| map1 midpoints in map0 | `141,486` |
| map1 nonfinite midpoints dropped | `24` |
| map1 positive midpoint faces | `109,449` |
| output-chain assembly sec | `231.04580410569906` |
| output-chain write sec | `78.51605707406998` |

Earlier Goal4806 report had claimed:

```text
chain_count 29254027
face_count 115490
```

Current-line after finite filter:

```text
chain_count 29253910
face_count 115515
```

Therefore the old County x Zipcode byte-equality clue is **not currently
validated** under the current repaired line.

## Interpretation

Goal4826 did two useful things:

1. It exposed and repaired a real product invariant violation: native
   point-location must not receive nonfinite query points.
2. It proved that this finite-query repair is insufficient for County x
   Zipcode byte-equality.

The remaining mismatch is likely downstream of LSI count and finite-query
admission. The most likely next diagnosis area is intersection coordinate
materialization and output-chain semantics:

- exact/scaled intersection coordinate storage;
- author internal-coordinate midpoint materialization;
- output-chain sorting/deduplication;
- whether dropping nonfinite midpoint pairs is semantically equivalent to the
  author path or only a safe kernel-input guard.

## Claim Boundary

Allowed claim:

- Current RTDL now completes the County x Zipcode full overlay run without the
  finite-query crash.
- The run is not byte-equal to the author baseline.

Forbidden claims:

- County x Zipcode paper reproduction is complete.
- Section 5.7 exact reproduction is complete.
- Performance can be compared as a valid paper row.
- The old Goal4806 byte-equality result has been revalidated.

## Next Goal

Goal4827 must diagnose the County x Zipcode output mismatch before any
performance row or Block x Water escalation.

Recommended Goal4827 title:

**Goal4827 — County x Zipcode Output Mismatch Diagnosis After Finite-Query
Repair**

Exit gate:

- identify whether the first material mismatch is due to coordinate
  materialization, dropped nonfinite midpoint pairs, sorting, deduplication, or
  face assignment;
- no performance claim until correctness passes.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   I would be foolish if I treated the run completion as success or moved to
   performance despite byte inequality.

2. **What actions would make the decision foolish?**
   Calling finite-filter completion a paper reproduction; ignoring the
   chain/face-count mismatch; moving to Block x Water before County x Zipcode
   correctness is understood.

3. **Is there another path that avoids being stuck?**
   Yes. The mismatch should be diagnosed by comparing output structure and
   coordinate materialization, not by running larger datasets.

4. **Can I start a different path that truly solves the problem?**
   Yes. Goal4827 should find the first semantic divergence and decide whether
   the fix belongs in RTDL core/product semantics or in the application wrapper.
