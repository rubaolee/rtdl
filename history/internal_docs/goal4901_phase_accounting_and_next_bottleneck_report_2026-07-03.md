# Goal4901 — Same-Process Phase Accounting and Next Bottleneck Identification

Date: 2026-07-03

## Verdict

`completed_phase_accounting_gap_closed__next_bottleneck_point_location_prepare`

Goal4901 split the cache-enabled Python+Numba+RTDL representative overlay route into previously missing phases. It showed that the `~9.8s` unexplained gap from Goal4900 was not a mysterious runtime effect. It was mostly unmeasured point-location preparation/BVH setup, with first-run cold effects.

The goal also updated the public-primitives internal harness so future runs record these phases directly.

This goal does not change RTDL LSI/PIP semantics and does not change RayJoin overlay correctness logic.

## Files Changed

- Added:
  - `history/internal_docs/goal4901_same_process_phase_accounting.py`
- Updated:
  - `history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py`

The harness update only adds timing scopes:

- `shared_bounds_sec`
- `prepare_point_location_map0_in_map1_sec`
- `prepare_point_location_map1_in_map0_sec`
- `midpoint_points_map{0,1}_sec`
- `pack_midpoint_points_map{0,1}_sec`
- `assign_midpoint_faces_map{0,1}_sec`
- `destroy_point_location_sessions_sec`
- `file_summary_generated_sec`
- `file_summary_author_sec`

## Evidence Artifacts

- Same-process two-repeat phase accounting:
  - `history/internal_docs/goal4901_phase_accounting_summary_2026-07-03.json`
- Accounted harness verification after instrumentation:
  - `history/internal_docs/goal4901_accounted_harness_verify_summary_2026-07-03.json`
- Prior Goal4900 reference:
  - `history/internal_docs/goal4900_numba_cache_overlay_summary_2026-07-03.json`

## Same-Process Measurement

The same-process script dynamically imports the existing Goal4886 Numba wrapper, installs the same Numba app-continuation functions, runs the same public RTDL LSI/PIP route, and times regions that were previously outside phase accounting.

It uses:

- public RTDL planar-map LSI;
- public RTDL planar-map point-location/PIP;
- Numba app-layer continuation/writer helper;
- packed CDB cache;
- no `rtdsl.rayjoin_overlay` import.

### Repeat Results

| Repeat | Total elapsed | Timed phase sum | Unattributed |
|---:|---:|---:|---:|
| 0 | `42.369s` | `42.369s` | `0.0006s` |
| 1 | `11.320s` | `11.320s` | `0.0005s` |

Both repeats were byte-identical to AuthorOfficial:

```text
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
```

Interpretation:

- The unexplained time can be accounted for.
- Repeat 0 includes cold effects: first-touch cache behavior, first prepare/JIT/setup, and possibly OS/GPU initialization.
- Repeat 1 is the cleaner steady-state view of this same route.

### Steady-State Repeat 1 Breakdown

| Phase | Time |
|---|---:|
| load/pack left+right | `0.187s` |
| LSI public pair-id rows | `1.908s` |
| intersection reprojection | `0.472s` |
| sort map0+map1 | `0.409s` |
| prepare point-location map0 in map1 | `0.236s` |
| prepare point-location map1 in map0 | `4.123s` |
| vertex PIP map0 in map1 | `1.117s` |
| vertex PIP map1 in map0 | `0.032s` |
| midpoint generation/pack/PIP/assign | about `0.029s` |
| output writer | `2.529s` |
| destroy point-location sessions | `0.243s` |
| file summaries | `0.036s` |
| total | `11.320s` |

Main bottlenecks now:

1. `prepare_point_location_map1_in_map0_sec`: `4.123s`
2. `output_chain_write_sec`: `2.529s`
3. `lsi_public_pair_id_rows_sec`: `1.908s`
4. `vertex_pip_map0_in_map1_sec`: `1.117s`

The largest single item is not CDB loading and not Numba app continuation. It is point-location preparation for the large left map.

## Accounted Harness Verification

After patching the main internal public-primitives harness, the cache-enabled Numba route produced:

- `byte_equal_to_author: true`
- elapsed: `13.314s`
- wrapper total: `13.464s`
- sum of recorded phases excluding wrapper total: `13.306s`
- unaccounted: about `0.008s`

This means the previous Goal4900 accounting gap is resolved for future runs.

Key recorded phases from the verified harness:

| Phase | Time |
|---|---:|
| load/pack left+right | `0.199s` |
| LSI public rows | `2.913s` |
| prepare point-location map0 in map1 | `0.768s` |
| prepare point-location map1 in map0 | `4.102s` |
| vertex PIP map0 in map1 | `1.117s` |
| output writer | `2.575s` |
| file summary generated+author | `0.268s` |

## What Was Learned

Goal4900's `~9.8s` unexplained gap was not evidence of a hidden RayJoin-specific issue or a need to change semantics. It was a measurement hole.

The missing scopes were mostly:

- point-location session preparation, especially preparing the large left-map point-location structure;
- first-run cold effects;
- smaller midpoint and file-summary costs.

After adding the scopes, the measured route is explainable.

## What This Does Not Claim

This goal does not claim:

- broad RayJoin speedup;
- full eight-pair Section 5.7 performance;
- LSI/PIP kernel speedup;
- Numba acceleration of RTDL primitive traversal;
- raw author-program equivalence beyond the documented AuthorOfficial contract;
- any V3/V4 resurrection.

## Next Engineering Target

The next performance goal should target point-location preparation, but only generically:

> Build or expose a reusable prepared point-location base-map session/cache so that repeated point-location queries against the same planar map do not rebuild the same native structure, while preserving the public `prepare_planar_map_point_location_2d_optix` contract and byte-for-byte RayJoin representative output.

This target is justified because:

- point-location prepare is the largest steady-state phase (`4.123s`);
- it is generic to planar-map point-location/PIP, not RayJoin overlay;
- the current app already uses two vertex queries and two midpoint queries against prepared maps, so the public API should make reuse explicit and measurable;
- the goal is consistent with the post-v2.14 direction: make downstream composition cheaper before attempting deeper traversal fusion.

## Goal-Level Decision Audit

1. Did I make a stupid decision?
   - No on direction: I measured the unexplained gap before optimizing. That avoided a blind rewrite.
2. What actions would have made it stupid?
   - Assuming the gap was Numba JIT or CDB cache without timing PIP prepare and other missing scopes.
3. Was there another path?
   - Yes: immediately start implementing a prepared PIP cache. That might still be right, but doing it before phase accounting would repeat the old "looks busy" failure mode.
4. Did I correct course?
   - Yes. The goal produced a fine-grained measurement and patched the harness so future evidence cannot hide point-location prepare inside "unattributed" time.
