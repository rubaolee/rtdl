# Goal4893 Result: Route A Candidate-Range / Index Measurement Gate

Date: 2026-07-03

## Exit Label

`route_a_existing_range_mode_passed_strong_gate__productization_next`

## One-Line Result

Route A passed. A fine-grained existing RTDL range-construction mode,
`block_merge64` with `max_iter=0`, preserves correctness and reduces vertex PIP
candidate work by `53,400x` on map0 and `18,542x` on map1 versus the fixed8
baseline.

This is the first post-v2.14 RayJoin high-performance result that moves the
measured blocker directly.

## What Was Tested

Goal4893 tested whether RTDL's directed point-location candidate explosion can
be reduced by **generic candidate-range / spatial-index construction**, rather
than by:

- Python output tuning;
- Numba continuation;
- prepared-session hygiene;
- in-loop lower-bound pruning;
- RayJoin-specific hidden kernels.

The test used the same Australia current-source representative Section 5.7 pair
as Goal4890 and Goal4892:

- left: `/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb`
- right: `/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb`
- comparator output:
  `/workspace/goal4875_section57_au_representative/author_contract_full/author_contract_au_overlay.txt`

## Artifacts

Local:

- `history/internal_docs/goal4893_route_a_candidate_range_index_redesign_measurement_gate_2026-07-03.md`
- `history/internal_docs/goal4893_pip_group_mode_matrix_runner.py`
- `history/internal_docs/goal4893_pip_group_full_matrix_2026-07-03.json`
- `history/internal_docs/goal4893_block_merge64_i0_e1p5_full_overlay_summary_2026-07-03.json`

POD:

- matrix summary:
  `/workspace/goal4893_route_a/pip_group_full_matrix.json`
- matrix stream:
  `/workspace/goal4893_route_a/pip_group_full_matrix.jsonl`
- full overlay summary:
  `/workspace/goal4893_route_a/block_merge64_i0_e1p5_summary.json`
- full overlay output:
  `/workspace/goal4893_route_a/block_merge64_i0_e1p5_overlay.txt`

## Measurement Method

The PIP-only matrix runner:

1. loads and packs the two CDB files once;
2. rebuilds point-location locators under different group-mode environment
   settings;
3. runs vertex PIP map0 and map1 only;
4. records:
   - raw candidate segment-loop count;
   - run time;
   - positive face count;
   - face-array FNV64 hash;
   - whether the face hash matches fixed8.

This avoids wasting time on repeated CDB load/pack and output-chain writing.

After the matrix identified a winner, the full public-primitives overlay route
was run once with that mode to prove byte-for-byte correctness.

## Candidate Matrix Result

The best modes were all `block_merge64` with `max_iter=0`. The `area_enlarge`
parameter is irrelevant when no merge iteration runs.

Top valid rows:

| Mode | map0 candidates | map0 reduction | map1 candidates | map1 reduction | Face hash |
| --- | ---: | ---: | ---: | ---: | --- |
| `block_merge64_i0_e1.5` | 9,586,860 | 53,400.5x | 1,960,935 | 18,541.9x | matches |
| `block_merge64_i0_e2.0` | 9,586,860 | 53,400.5x | 1,960,935 | 18,541.9x | matches |
| `block_merge64_i0_e3.5` | 9,586,860 | 53,400.5x | 1,960,935 | 18,541.9x | matches |
| `block_merge64_i1_e1.5` | 11,343,846 | 45,129.6x | 2,146,318 | 16,940.3x | matches |
| `adaptive_ms8_e1.5` | 20,171,952 | 25,379.0x | 2,950,835 | 12,321.7x | matches |

Baseline fixed8:

| Stage | fixed8 candidates |
| --- | ---: |
| vertex PIP map0 in map1 | 511,943,147,571 |
| vertex PIP map1 in map0 | 36,359,368,176 |

Best Route-A mode:

| Stage | best candidates | Reduction |
| --- | ---: | ---: |
| vertex PIP map0 in map1 | 9,586,860 | 53,400.5x |
| vertex PIP map1 in map0 | 1,960,935 | 18,541.9x |

This clears both:

- hard gate: `10x`;
- strong gate: `100x`.

## Full Overlay Correctness Result

Full overlay command used:

```text
RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE=block_merge64
RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER=0
RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE=1.5
```

Result:

```text
byte_equal_to_author: true
generated sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
author sha256:    a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
```

So the candidate-range change preserved the full overlay output, not only the
individual PIP face arrays.

## Performance Interpretation

Do not overstate the result.

### What Improved Dramatically

PIP traversal work:

| Stage | fixed8 traversal | Route-A traversal |
| --- | ---: | ---: |
| vertex PIP map0 | 34.856 s | 0.010 s |
| vertex PIP map1 | 2.870 s | 0.002 s |
| midpoint PIP map0 | 0.063 s | 0.00016 s |
| midpoint PIP map1 | 0.056 s | 0.00014 s |

Candidate work:

| Stage | fixed8 candidates | Route-A candidates | Reduction |
| --- | ---: | ---: | ---: |
| vertex PIP map0 | 511,943,147,571 | 9,586,860 | 53,400.5x |
| vertex PIP map1 | 36,359,368,176 | 1,960,935 | 18,541.9x |
| midpoint PIP map0 | 68,493,462 | 7,581 | 9,034.9x |
| midpoint PIP map1 | 105,145,275 | 13,131 | 8,006.0x |

### What Did Not Disappear

End-to-end wall time still includes load/pack and LSI:

| Metric | fixed8 | Route-A mode | Speedup |
| --- | ---: | ---: | ---: |
| full elapsed | 129.448 s | 93.345 s | 1.39x |
| elapsed excluding load/pack | 52.888 s | 16.292 s | 3.25x |

The remaining dominant costs are:

- CDB load/pack: about 77 s;
- LSI public rows: about 6.5 s;
- output-chain writer: about 2.7 s;
- hidden locator prepare/build cost, not fully represented in `phase_seconds`.

Therefore this goal authorizes "PIP candidate explosion solved for this
representative via Route A," not "full RayJoin app now beats AuthorPatch."

## Why This Worked

The failed Goal4892 proof tried to skip obvious losers after traversal already
visited broad ranges. It could not reduce the range visits.

Goal4893 changes the range construction. The winning mode effectively keeps
point-location AABB primitives fine-grained instead of merging consecutive
segments into large ranges. This lets OptiX's BVH reject most irrelevant
segments before the custom intersection loop.

That is why candidate work collapses from hundreds of billions to millions.

## Genericity Boundary

This is a generic directed point-location / planar-map range-construction result:

- no output-chain logic changed;
- no RayJoin overlay hidden kernel was added;
- no public API changed;
- no comparator/SoS semantics changed;
- the public route still uses `prepare_planar_map_point_location_2d_optix`.

However, it is still measured on one representative RayJoin-derived workload.
Before productizing as a default, the next goal needs:

- second non-RayJoin directed point-location synthetic workload;
- regression on Section 5.2 / 5.3 PIP correctness;
- clear product rule for when to prefer fine-grained AABBs over merged ranges;
- measurement of locator prepare/build cost.

## Productization Recommendation

Start Goal4894:

```text
Productize generic fine-grained directed point-location range construction.
```

Proposed product rule:

- for large directed point-location workloads, prefer fine-grained segment AABBs
  or a mode equivalent to `block_merge64 + max_iter=0`;
- keep coarser grouping available for cases where build memory or build time
  dominates;
- expose the choice as an internal planner/default, not as a RayJoin-specific
  environment hack.

Goal4894 must not simply set an environment variable and call it done. It must
turn the measured mode into a clean generic implementation decision with tests.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   No. This goal chose a path and measured the actual blocker instead of asking
   the user to choose or tuning unrelated layers.

2. **What actions would make this decision stupid?**

   Claiming full app performance victory from a PIP-stage win, ignoring load/LSI
   costs, or shipping an environment-variable hack as product design.

3. **Is there another possible path?**

   Yes, Route C remains the compiler/fusion path. It is not needed for this
   specific candidate-explosion blocker yet because Route A passed strongly.

4. **Can we start a different path that truly solves the problem?**

   Yes. Start Goal4894 to productize the fine-grained generic directed
   point-location range construction, then measure the full app again.
