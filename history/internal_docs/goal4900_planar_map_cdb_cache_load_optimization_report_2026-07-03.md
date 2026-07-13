# Goal4900 — Generic Planar-Map CDB Packed Cache Load Optimization

Date: 2026-07-03

## Verdict

`completed_generic_packed_cache_load_optimization__correctness_preserved__next_gap_is_unattributed_runtime_overhead`

Goal4900 reduced the Australia representative RayJoin reproduction path's CDB load cost by making the existing packed-cache path explicit, durable, and cheaper on repeated loads. It did not change LSI, PIP, overlay semantics, or RayJoin application logic.

The important result:

- byte-for-byte correctness is preserved;
- load/pack time drops from about `25.437s` to about `0.192s` on the cache-enabled measured run;
- total wall time drops from `39.373s` to `18.238s`;
- the remaining unexplained gap is no longer CDB loading, but uninstrumented wrapper/startup/JIT/phase-accounting overhead.

This is a generic dataset-loader improvement, not a RayJoin-specific kernel shortcut.

## Files Changed

- `src/rtdsl/datasets.py`
  - Added optional bounds reuse when constructing `PlanarMapCdbPackedInputs`.
  - Persisted bounds in packed-cache `meta.json`.
  - Added lazy metadata backfill for old cache entries that lack bounds.
  - Continued to use the generic `RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR` cache mechanism.
- `tests/goal4895_planar_map_cdb_packed_loader_test.py`
  - Added cache metadata coverage for stored bounds.
  - Added legacy-cache backfill coverage.
- `history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py`
  - Added `--cache-dir`.
  - Temporarily sets `RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR` only around dataset loading.
  - Records cache status/path in the summary artifact.

## Evidence Artifacts

- No-cache load probe:
  - `history/internal_docs/goal4900_load_cache_bounds_probe_2026-07-03.json`
- Cache-enabled load probe:
  - `history/internal_docs/goal4900_load_cache_bounds_probe_with_env_2026-07-03.json`
- Cache-enabled Numba+RTDL representative overlay:
  - `history/internal_docs/goal4900_numba_cache_overlay_summary_2026-07-03.json`
- Previous comparison baseline:
  - `history/internal_docs/goal4899_author_python_rtdl_numba_rtdl_comparison_2026-07-03.json`

## Load Measurements

Dataset:

- Australia current-source lakes x parks representative
- Left/lakes: `14,788,065` points, `14,430,155` edges
- Right/parks: `992,505` points, `941,375` edges

### Without Packed Cache Env

The harness was reparsing raw CDB inputs each run.

| Repeat | Left load | Right load | Total load |
|---:|---:|---:|---:|
| 0 | `23.719s` | `2.178s` | `25.898s` |
| 1 | `22.550s` | `2.026s` | `24.576s` |
| 2 | `22.944s` | `2.028s` | `24.971s` |

### With Packed Cache Env

Cache directory:

```text
/workspace/goal4894_productize_20260703b/packed_cache_goal4895_new
```

| Repeat | Left load | Right load | Total load |
|---:|---:|---:|---:|
| 0 | `4.460s` | `1.881s` | `6.341s` |
| 1 | `0.163s` | `0.102s` | `0.264s` |
| 2 | `0.136s` | `0.095s` | `0.231s` |

Interpretation:

- The old no-cache path was dominated by raw CDB parsing.
- The first cache-enabled repeat may still pay first-touch, metadata backfill, and OS cache effects.
- Subsequent cache hits are around `0.23-0.26s` total for both maps.
- Persisting bounds matters because old cache entries without bounds otherwise force a full point scan to recompute min/max.

## Full Representative Overlay Result

Command class:

```text
Python + public RTDL planar-map LSI/PIP primitives
+ Numba app continuation
+ packed CDB cache enabled
```

Artifact:

```text
history/internal_docs/goal4900_numba_cache_overlay_summary_2026-07-03.json
```

Correctness:

```text
byte_equal_to_author: true
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
lines: 276320
bytes: 6189260
```

Key timings:

| Phase | Goal4899 no explicit cache | Goal4900 cache-enabled |
|---|---:|---:|
| total wall | `39.373s` | `18.238s` |
| load/pack | `25.437s` | `0.192s` |
| LSI public rows | `3.246s` | `2.881s` |
| vertex PIP map0 in map1 | not separately compared here | `1.127s` |
| vertex PIP map1 in map0 | not separately compared here | `0.042s` |
| output writer | `2.358s` | `3.289s` |

Derived:

- Total speedup versus the Goal4899 no-explicit-cache Numba run: about `2.16x`.
- Load speedup versus the Goal4899 no-explicit-cache Numba run: about `132.7x`.

## Important Boundary

The load win is real, but it is not an RT traversal win.

This goal does not claim:

- LSI kernel speedup;
- PIP kernel speedup;
- Numba acceleration of RTDL primitive traversal;
- broad RayJoin performance superiority;
- full eight-pair Section 5.7 performance;
- raw author-program reproduction beyond the already documented bounded/representative contract.

It claims only:

> The generic planar-map CDB packed-cache path is now explicit in the harness, stores/reuses bounds, lazy-backfills legacy cache metadata, and reduces representative input load cost while preserving byte-for-byte output.

## New Bottleneck / Next Measurement

The cache-enabled run exposes a new issue.

Recorded phases sum to about `8.435s`:

| Recorded phase group | Time |
|---|---:|
| load/pack | `0.192s` |
| LSI public rows | `2.881s` |
| reprojection + sorting | `0.903s` |
| vertex/midpoint PIP | `1.171s` |
| output writer | `3.289s` |
| recorded phase total | `8.435s` |
| full elapsed | `18.238s` |
| unattributed | about `9.803s` |

That unattributed time is now the largest remaining gap in the measured Python+Numba+RTDL path.

Most likely candidates:

- Numba import/JIT compile/startup overhead;
- wrapper-level setup not recorded by the per-phase timers;
- Python object construction or output pre/post processing outside the current timing scopes;
- measurement-accounting mismatch between wrapper total and internal harness phases.

The next goal should not guess. It should measure steady-state versus first-run overhead in one process and split:

```text
startup/import/JIT
prepared dataset cache load
RTDL primitive phases
Numba continuation phases
writer
unaccounted app glue
```

## Validation

Local:

```text
PYTHONPATH=src py -m unittest \
  tests.goal4895_planar_map_cdb_packed_loader_test \
  tests.goal4895_public_cdb_loader_harness_integration_test \
  tests.goal4851_planar_map_lsi_public_front_door_test

Ran 7 tests
OK
```

POD:

```text
PYTHONPATH=src python -m unittest \
  tests.goal4895_planar_map_cdb_packed_loader_test \
  tests.goal4895_public_cdb_loader_harness_integration_test \
  tests.goal4851_planar_map_lsi_public_front_door_test

Ran 7 tests
OK
```

Representative overlay:

```text
byte_equal_to_author: true
```

## Engineering Judgment

This was the correct next target after Goal4899 because load/pack had become a dominant visible wall-time cost. The fix is not a paper benchmark trick:

- the cache is generic for planar-map CDB packed inputs;
- bounds persistence/backfill is generic metadata hygiene;
- the harness now exposes cache selection explicitly instead of relying on ambient environment state.

The next biggest target is not another CDB cache tweak. It is the `~9.8s` unattributed runtime gap in the cache-enabled route. Until that is split, optimizing another named phase risks returning to the old failure mode: busy-looking work without a verified bottleneck.

## Goal-Level Decision Audit

1. Did I make a stupid decision?
   - I avoided the main stupid decision this time: I did not keep optimizing RT kernels after evidence showed the visible bottleneck had moved to CDB loading.
2. What actions would have made it stupid?
   - Treating the 2.16x total improvement as a broad performance claim, or claiming Numba/RT traversal improved when the evidence says the win is loader/cache.
3. Was there another path?
   - Yes: directly chase LSI/PIP kernels or writer again. That would have ignored the measured load wall time.
4. Did I correct course?
   - Yes. The work stayed on the generic loader/cache surface, preserved correctness, and ends by naming the next measured bottleneck instead of inventing a new unmeasured optimization.
