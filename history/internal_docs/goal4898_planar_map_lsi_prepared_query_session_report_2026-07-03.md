# Goal4898 — Planar-Map LSI Prepared-Query Session and Remaining Cost Boundary

Date: 2026-07-03

## Verdict

`completed_bounded_prepared_query_session__hot_reuse_improved__single_overlay_still_setup_bound`

Goal4898 produced a real generic RTDL API improvement, but not a broad single-run performance win:

- Added a public `PreparedOptixPlanarMapLsi2DQuery` session API.
- Added `PreparedOptixPlanarMapLsi2D.prepare_query(query)` so query-side preparation can be reused explicitly.
- Updated the Section 5.7 representative public-primitives harness to use the public prepared-query session.
- Verified byte-for-byte correctness on the Australia lakes x parks representative overlay.
- Verified that repeated pair-id-row execution inside one prepared-query session is stable at about 5.8 ms.
- Confirmed that the current single overlay run is dominated by load/pack and output writer, not by LSI row emission.

This is not a claim that RTDL now beats the author implementation. It is a bounded runtime/API cleanup that exposes an already-measured hot reuse capability to users.

## Files Changed

- `src/rtdsl/optix_runtime.py`
  - Added `PreparedOptixPlanarMapLsi2DQuery`.
  - Added `PreparedOptixPlanarMapLsi2D.prepare_query(query)`.
  - Re-routed `run_raw`, `run_pair_id_rows`, and `count_with_metadata` through the same query-session path.
  - Count metadata now records:
    - `query_prepare.prepared_query_reused`
    - `query_prepare.public_session_api`
- `src/rtdsl/__init__.py`
  - Exported `PreparedOptixPlanarMapLsi2DQuery`.
- `tests/goal4851_planar_map_lsi_public_front_door_test.py`
  - Added export coverage.
  - Added a prepared-query reuse test proving one query-side prepare can feed both count and pair-id rows without environment leakage.
- `history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py`
  - Updated the LSI phase to use:
    ```python
    with prepare_planar_map_lsi_2d_optix(right.lsi_segments) as lsi:
        with lsi.prepare_query(left.lsi_segments) as query:
            row_view = query.run_pair_id_rows()
    ```

## Measurements

### 1. Prepared-Query Reuse Probe

Artifact:

- `history/internal_docs/goal4898_prepared_query_probe_2026-07-03.json`

Dataset:

- Australia current-source lakes x parks representative
- Left edges: `14,430,155`
- Right edges: `941,375`

Measured result:

| Phase | Time |
|---|---:|
| `prepare_query(left)` | `0.681934s` |
| first `count_with_metadata()` in query session | `1.512251s` |
| `run_pair_id_rows()` repeat 0 | `0.005820s` |
| `run_pair_id_rows()` repeat 1 | `0.005773s` |
| `run_pair_id_rows()` repeat 2 | `0.005755s` |

Interpretation:

- Query-side preparation is real cost.
- First use still pays scaled-cache/grouped-range setup.
- After setup, repeated pair-id-row execution is about 5.8 ms.
- The new API makes this hot reuse a public RTDL capability instead of a private/manual pattern.

### 2. Direct vs Grouped Route Probe

Artifact:

- `history/internal_docs/goal4898_direct_vs_grouped_probe_2026-07-03.json`

Measured result:

| Route | Wall | Native pass |
|---|---:|---:|
| direct count, first use | `1.505442s` | `0.084060s` |
| grouped count after direct setup | `0.618463s` | `0.002898s` |
| grouped pair-id rows after grouped setup | `0.005875s` | `0.002829s + 0.002831s` |

Interpretation:

- Direct traversal avoids grouped-GAS setup but has a much slower hot kernel.
- Grouped traversal pays one-time setup, then has a much faster hot kernel.
- A new direct pair-id-row route is not justified yet: it would be useful only in a narrow one-shot case after scaled caches are warm but grouped GAS is not built.
- Implementing that route now would be another "looks busy" optimization without a strong release payoff.

### 3. Full Representative Overlay

Artifact:

- `history/internal_docs/goal4898_prepared_query_overlay_summary_2026-07-03.json`

Result:

- `byte_equal_to_author: true`
- Output SHA256 matches AuthorOfficial:
  - `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`
- Total elapsed: `51.316807s`

Key phases:

| Phase | Time |
|---|---:|
| load/pack left | `22.277669s` |
| load/pack right | `2.005301s` |
| public planar-map LSI rows | `2.755288s` |
| intersection reprojection | `0.482725s` |
| vertex PIP map0 in map1 | `1.097824s` |
| vertex PIP map1 in map0 | `0.039091s` |
| output-chain streaming write | `17.101428s` |
| total | `51.316807s` |

Interpretation:

- Correctness is preserved after the public prepared-query API change.
- LSI is no longer the dominant wall-time component in this representative run.
- Remaining large costs are:
  - CDB packed load/pack/cache path
  - output-chain streaming writer
- Continuing to squeeze LSI without a new measurement would be the wrong target.

## Validation

Local:

```text
PYTHONPATH=src py -m unittest \
  tests.goal4851_planar_map_lsi_public_front_door_test \
  tests.goal4857_planar_map_point_location_public_front_door_test \
  tests.goal4894_directed_point_location_fine_grained_default_test \
  tests.goal4895_planar_map_cdb_packed_loader_test \
  tests.goal4895_public_cdb_loader_harness_integration_test

Ran 16 tests in 0.123s
OK
```

POD:

```text
PYTHONPATH=src python -m unittest \
  tests.goal4851_planar_map_lsi_public_front_door_test \
  tests.goal4857_planar_map_point_location_public_front_door_test \
  tests.goal4894_directed_point_location_fine_grained_default_test \
  tests.goal4895_planar_map_cdb_packed_loader_test \
  tests.goal4895_public_cdb_loader_harness_integration_test

Ran 16 tests in 0.042s
OK
```

Representative overlay:

```text
byte_equal_to_author: true
```

## What This Does Not Claim

- No broad RayJoin speedup claim.
- No full eight-pair Section 5.7 claim.
- No claim that prepared-query sessions improve single-shot overlay wall time by themselves.
- No claim that direct rows should now replace grouped rows.
- No V3/V4 resurrection claim.
- No raw callback / OptiX shader exposure.

## Engineering Judgment

This goal did not find a safe LSI-only route to a large single-run win. It did find and productize a real generic RTDL runtime shape:

> prepare base once, prepare query once, then run repeated count/row operations without redoing query-side preparation.

That is the correct public abstraction for repeated LSI workloads. For the current single representative overlay, the next meaningful optimization target is not LSI; it is the remaining large app-layer costs:

1. packed CDB load/cache behavior;
2. output-chain streaming writer;
3. phase telemetry that separates setup from hot traversal clearly enough that users do not confuse cold setup with RT traversal.

## Goal-Level Decision Audit

1. Did I make a stupid decision?
   - Partially. I initially copied files to the POD worktree root with `scp` instead of their exact target paths.
2. What actions made it stupid?
   - I used a directory destination for multiple files, allowing default placement instead of explicit paths.
3. Was there another path?
   - Yes. Use one `scp` per source with the full remote destination path, or archive/extract with explicit paths.
4. Did I correct course?
   - Yes. I immediately copied the files to the correct paths, verified the accidental root copies, removed only those exact misplaced files, and continued validation.

On the optimization decision itself, the answer is better: I did not implement a direct pair-id-row route after measurements showed the payoff was too narrow and uncertain. That avoided another "looks busy but useless" implementation.
