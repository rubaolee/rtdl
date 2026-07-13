# Goal4853: Section 5.2 LSI Final Reproduction Closure

Date: 2026-07-01

## Purpose

Close the RayJoin paper Section 5.2 LSI reproduction line for the currently available inputs by running one final POD pass through the public RTDL front door:

```python
prepare_planar_map_lsi_2d_optix(base).count(query)
```

This goal is only about Section 5.2 line-segment intersection counts. It is not Section 5.7 polygon overlay, not PIP/point-location, not all eight exact paper pairs, and not a performance claim.

## Final POD Run

Environment artifact:

`history/internal_docs/goal4853_section52_final/environment.json`

Important environment facts:

- POD worktree: `/workspace/rtdl_goal4817_user_smoke_20260630_102224`
- Git HEAD: `5f049502e268417b0c0d78b93fd6fc575092e8d6`
- Python: `/usr/bin/python3`
- `PYTHONPATH=src`
- `RTDL_OPTIX_LIB=/workspace/rtdl_goal4817_user_smoke_20260630_102224/build/librtdl_optix.so`

The POD worktree was intentionally not represented as a clean release checkout. It contains active product-development changes for the v2.14 recovery line, including the public planar-map LSI primitive and related tests. This closure verifies the current product line behavior, not a clean tagged release package.

## Results

Summary artifact:

`history/internal_docs/goal4853_section52_final/final_summary.json`

| Pair | Expected count | Observed public RTDL count | Match | Expected-count provenance | Total observed sec | Count sec |
|---|---:|---:|---|---|---:|---:|
| County x Zipcode | 961165 | 961165 | yes | `authorpatch_goal4845_exact_count` | 398.502 | 56.866 |
| Block x Water | 649605 | 649605 | yes | `authorpatch_goal4846_exact_count` | 642.445 | 57.502 |
| Australia Lakes x Parks representative | 13622 | 13622 | yes | `rtdl_bundled_goal4848_representative_count` | 76.733 | 5.070 |

All three case scripts returned `rc=0`; all three stderr files are empty:

- `history/internal_docs/goal4853_section52_final/county_zipcode_final.rc`
- `history/internal_docs/goal4853_section52_final/county_zipcode_final.stderr`
- `history/internal_docs/goal4853_section52_final/block_water_final.rc`
- `history/internal_docs/goal4853_section52_final/block_water_final.stderr`
- `history/internal_docs/goal4853_section52_final/australia_lakes_parks_representative_final.rc`
- `history/internal_docs/goal4853_section52_final/australia_lakes_parks_representative_final.stderr`

Each case summary records:

- `section52_lsi_count_only: true`
- `public_generic_rtdl_primitive: true`
- `bundled_rayjoin_helper_used: false`
- `full_overlay_claim: false`
- `all_eight_exact_paper_pairs_claim: false`
- `broad_speedup_claim: false`
- `native_predicate_mode: "planar_map_lsi"`

## What This Proves

For the available Section 5.2 inputs and representative pair, the public RTDL planar-map LSI front door reproduces the known expected LSI counts without importing or calling the bundled RayJoin helper.

This is the product boundary we wanted for Section 5.2:

- RTDL core supplies a generic planar-map LSI primitive.
- The application author can call the public primitive directly.
- The RayJoin bundled helper is not needed for these count results.

## What This Does Not Prove

This does not prove:

- Full Section 5.2 all-eight exact paper-pair completion.
- Section 5.7 polygon overlay reproduction.
- PIP or directed point-location correctness.
- Output-chain byte equality.
- A broad RTDL performance claim.
- A clean release-tag validation.

The remaining all-eight limitation is input provenance, not the public primitive on the tested pairs. The exact paper-preprocessed CDBs for the other Section 5.2 pairs are not all present in the current workspace/POD state. A future data-management goal can recover or regenerate more same-source pairs, but those must be labeled honestly as exact paper inputs only when the paper-preprocessed CDB provenance is proven.

## Exit Label

`completed_section52_lsi_public_front_door_available_pairs__no_full_8pair_claim`

## Recommended Next Step

Move to Section 5.3 with the same discipline:

1. Read the paper section and author source first.
2. Identify the workload contract and the author-patched baseline.
3. Map it to public RTDL primitives plus Numba only where Numba is the user-level partner.
4. Do not use bundled app helpers as evidence for a generic language claim.
5. Keep correctness ahead of performance.
