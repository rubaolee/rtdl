# Call For Review: Goal4851 Public Planar-Map LSI Front Door

Date: 2026-07-01

## Requested Verdict

Please review Goal4851 with one of:

- `approve_goal4851_completed_public_planar_map_lsi_available_pairs_passed`
- `approve_goal4851_completed_with_claude_amendments_addressed`
- `approve_goal4851_with_amendments`
- `block_goal4851_as_disguised_rayjoin_helper`
- `block_goal4851_insufficient_validation`

My requested label is:

`approve_goal4851_completed_with_claude_amendments_addressed`

## Files To Review

- Result report:
  - `history/internal_docs/goal4851_public_planar_map_lsi_front_door_result_2026-07-01.md`
- Claude second-seat review:
  - `history/internal_docs/claude_goal4851_public_planar_map_lsi_review_2026-07-01.md`
- Amendment response:
  - `history/internal_docs/goal4851_claude_amendment_response_2026-07-01.md`
- Goal:
  - `history/internal_docs/goal4851_public_cdb_lsi_primitive_contract_goal_2026-07-01.md`
- Public API implementation:
  - `src/rtdsl/optix_runtime.py`
  - `src/rtdsl/__init__.py`
- Focused tests:
  - `tests/goal4851_planar_map_lsi_public_front_door_test.py`
- User-mode script:
  - `history/internal_docs/goal4851_rayjoin_section52_lsi_public_front_door.py`
- Synthetic semantic probe:
  - `history/internal_docs/goal4851_synthetic_planar_map_lsi_probe.py`
  - `history/internal_docs/goal4851_synthetic_planar_map_lsi_probe_summary.json`
- POD artifacts:
  - `history/internal_docs/goal4851_current_osm_au_public_front_door_summary.json`
  - `history/internal_docs/goal4851_county_zipcode_restored_public_front_door_summary.json`
  - `history/internal_docs/goal4851_block_water_restored_public_front_door_summary.json`
  - `history/internal_docs/goal4851_am1_make_build_optix_with_prefix.log`
  - `history/internal_docs/goal4851_planar_map_lsi_metadata_after_am1.json`
  - `history/internal_docs/goal4851_synthetic_after_am1_stdout.json`
- Data recovery helper:
  - `history/internal_docs/goal4851_restore_rayjoin_pgraph_cache_to_cdb.py`
- Prior context:
  - `history/internal_docs/goal4850_section52_lsi_public_generic_rtdl_app_result_2026-07-01.md`
  - `history/internal_docs/goal4845_section52_lsi_county_zipcode_status_2026-07-01.md`
  - `history/internal_docs/goal4846_section52_lsi_results_2026-07-01.md`

## What Goal4851 Claims

Goal4851 claims that the public-language gap from Goal4850 has been repaired.

Before Goal4851, ordinary user code could call raw segment-pair primitives, or it could rely on the bundled `rtdsl.rayjoin_overlay` helper. It did not have a public generic planar-map/CDB LSI front door.

Goal4851 adds:

```python
from rtdsl import load_cdb, prepare_planar_map_lsi_2d_optix

base = load_cdb("base_Point.cdb")
query = load_cdb("query_Point.cdb")

with prepare_planar_map_lsi_2d_optix(base) as lsi:
    count = lsi.count(query)
```

The front door internally selects the existing native author-style LSI predicate and restores the environment afterward. It does not require user code to import `rtdsl.rayjoin_overlay`.

After Claude review, the public predicate mode was renamed to `planar_map_lsi`; native code still accepts the historical `rayjoin_lsi` alias for compatibility. The public API guards this env-based selector with a Python process-local lock, but native explicit predicate parameters remain future product debt.

## What Goal4851 Does Not Claim

Goal4851 does not claim:

- full Section 5.2 eight-pair exact-input reproduction;
- Section 5.7 polygon overlay;
- broad RayJoin speedup;
- broad RTDL speedup;
- generated CDBs are exact paper inputs;
- cache recovery is acceptable as long-term dataset management.

## Key Evidence

### 1. Historical Primitive Audit

A read-only subagent audit found no pre-existing public generic CDB/planar-map LSI primitive equivalent to `prepare_planar_map_lsi_2d_optix`.

Existing pieces before Goal4851:

- raw segment-pair OptiX primitives;
- bundled RayJoin helper path;
- hidden `RTDL_OPTIX_SEGMENT_PAIR_PREDICATE=rayjoin_lsi` predicate mode;
- CDB helpers.

Missing piece:

- public user-level CDB/planar-map LSI front door.

### 2. Synthetic Semantic Delta

The synthetic probe finds six small cases where raw segment-pair count and planar-map LSI count differ, mainly shared-left-endpoint / boundary cases:

```text
raw segment-pair count = 1
planar-map LSI count   = 0
```

This supports that the new primitive is not just a cosmetic alias for raw segment-pair count.

### 3. POD Gates

All runs used:

- public API: `prepare_planar_map_lsi_2d_optix`
- no user import of `rtdsl.rayjoin_overlay`
- `bundled_rayjoin_helper_used: false`
- `public_generic_rtdl_primitive: true`

Results:

| Pair | Expected | Public API count | Match | Artifact |
|---|---:|---:|---|---|
| Australia Lakes x Parks representative | 13622 | 13622 | yes | `goal4851_current_osm_au_public_front_door_summary.json` |
| County x Zipcode restored exact/same-source CDB | 961165 | 961165 | yes | `goal4851_county_zipcode_restored_public_front_door_summary.json` |
| Block x Water restored exact/same-source CDB | 649605 | 649605 | yes | `goal4851_block_water_restored_public_front_door_summary.json` |

### 4. Exact CDB Recovery

The ordinary CDB files used by earlier Section 5.2 runs were missing from their historical paths on the active POD. Goal4851 recovered the County/Zipcode and Block/Water text CDB files from RayJoin serialized planar-graph caches still present in `/dev/shm`, using the author source layout in `src/map/planar_graph.h`.

The recovered CDBs then passed the public-front-door count gates above.

This is a successful rescue of the available exact/same-source inputs, but it also exposes data-management debt: future proof must store exact CDB assets durably rather than relying on workspace or `/dev/shm` survival.

## Review Questions

1. Is `prepare_planar_map_lsi_2d_optix` a legitimate public generic CDB/planar-map LSI front door, or is it a disguised RayJoin helper?
2. Does the implementation avoid importing or requiring `rtdsl.rayjoin_overlay` in user code?
3. Does the `planar_map_lsi` public predicate mode plus legacy `rayjoin_lsi` native alias resolve the generic-vs-RayJoin-name concern?
4. Does the synthetic probe sufficiently demonstrate that raw segment-pair count and planar-map LSI are distinct contracts?
5. Do the three POD gates support completing Goal4851 for the available Section 5.2 LSI pairs?
6. Is it correct to keep full 8/8 Section 5.2 reproduction out of claim scope until the other six exact inputs or agreed representative inputs are available?
7. Is it correct to treat the old regenerated County x Zipcode `2509228` as non-evidence against the historical `961165` row, now that the restored exact/same-source CDB row passes?
8. Are the focused unit tests sufficient for the API/front-door behavior?
9. Is the expected-count provenance now clear enough to prevent reading this as full independent author-answer proof?
10. Is the env-var concurrency limitation adequately bounded for this goal, given the Python lock and explicit future native-ABI debt?
11. Is the user-facing documentation integration sufficient for the new public symbol?
12. What additional evidence is required before claiming full Section 5.2 eight-pair completion?

## Non-Authorization

This review must not authorize:

- full Section 5.2 eight-pair exact-input completion;
- Section 5.7 overlay reproduction;
- V3/V4 claims;
- Embree claims;
- broad RTDL or RayJoin speedup;
- treating regenerated CDBs as exact paper inputs;
- pretending that `/dev/shm` cache recovery is durable dataset management.
