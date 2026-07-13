# Goal4851 Claude Amendment Response

Date: 2026-07-01

Source review:

- `history/internal_docs/claude_goal4851_public_planar_map_lsi_review_2026-07-01.md`

## Verdict Requested

`approve_goal4851_claude_amendments_addressed_with_native_abi_debt`

## AM1: Generic Name Vs Historical RayJoin Name

Status: `addressed`

Changes:

- Public Python path now uses `_PLANAR_MAP_LSI_PREDICATE_MODE = "planar_map_lsi"`.
- Native `segment_pair_predicate_mode_from_env()` now accepts both:
  - `planar_map_lsi`
  - historical alias `rayjoin_lsi`
- Result metadata now reports:
  - `native_predicate_mode: "planar_map_lsi"`
  - `native_predicate_legacy_alias: "rayjoin_lsi"`

Boundary:

The native helper/function names still contain historical `rayjoin_lsi` wording in places. That is not ideal, but the public predicate selector and API contract now use the generic planar-map LSI name.

## AM2: Env-Var Selector Is Thread-Unsafe

Status: `partially_addressed_with_explicit_native_abi_debt`

Changes:

- Added `_OPTIX_SEGMENT_PAIR_PREDICATE_LOCK = threading.RLock()`.
- `_optix_segment_pair_predicate_mode()` now serializes its environment mutation with that process-local lock.
- Result metadata records:
  - `predicate_selection.mechanism: "process_env_guarded_by_python_lock"`
  - `predicate_selection.env_var: "RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"`
  - an explicit concurrency note.
- Report and docs state that a future native ABI should pass predicate mode as an explicit parameter.

Boundary:

This closes the public Python front-door race among calls using this API in one process. It does not prevent interference from code that manually mutates `RTDL_OPTIX_SEGMENT_PAIR_PREDICATE` outside the API. Full closure requires a native ABI parameter, not a process env selector.

## AM3: Expected Count Provenance

Status: `addressed`

Changes:

- Added `expected_count_provenance` to the user-mode script.
- Added provenance fields to existing Goal4851 summary artifacts:
  - Australia representative: `goal4848_rtdl_bundled_lsi_representative_count`
  - County x Zipcode: `goal4845_authorpatch_and_rtdl_historical_route_count`
  - Block x Water: `goal4846_authorpatch_and_rtdl_historical_route_count`
- Updated the result report to describe the evidence as count-consistency for the available pairs, not full independent author-answer proof for all Section 5.2 pairs.

## AM4: Count-Only Boundary

Status: `addressed`

Changes:

- Report keeps `section52_lsi_count_only: true`.
- Non-authorization now explicitly blocks claiming full geometric correctness from scalar count equality alone.

## AM5: RayJoin Exact-Paper Float Mismatch

Status: `recorded_as_follow-up_debt`

Changes:

- Result report now records that the `8e-14` failure in `tests.goal4374_rayjoin_exact_paper_suite_test` must be checked before stronger exact-paper wording.

Boundary:

It does not block Goal4851's count-only public front door. It does block stronger exact-paper correctness language.

## AM6: Public Documentation Integration

Status: `addressed`

Changes:

- `docs/rtdl_feature_guide.md` now lists planar-map LSI counts.
- `docs/features/engine_support_matrix.md` now lists `planar_map_lsi_count_2d`.
- `src/rtdsl/engine_feature_matrix.py` now lists `planar_map_lsi_count_2d` as:
  - OptiX: `native`
  - Embree/Vulkan/HIPRT/Apple RT: `unsupported_explicit`
- `docs/features/lsi/README.md` now teaches `prepare_planar_map_lsi_2d_optix`.
- Focused test now verifies `engine_feature_support("planar_map_lsi_count_2d", "optix")`.

## Verification

Local focused test:

```text
PYTHONPATH=src py -m unittest tests.goal4851_planar_map_lsi_public_front_door_test
```

Result:

```text
Ran 3 tests in 0.014s
OK
```

Support matrix spot-check:

```text
EngineFeatureSupport(feature='planar_map_lsi_count_2d', engine='optix', status='native', ...)
EngineFeatureSupport(feature='planar_map_lsi_count_2d', engine='embree', status='unsupported_explicit', ...)
```

Initial native rebuild attempt on POD:

```text
make build-optix
```

Result:

```text
RTDL OptiX SDK header not found at /opt/optix/include/optix.h
Set OPTIX_PREFIX to the OptiX SDK root...
```

Interpretation:

This first attempt failed because the default `OPTIX_PREFIX` pointed to `/opt/optix`, which did not exist on the active POD.

Resolution:

The correct SDK header location was found at:

```text
/tmp/optix-sdk-probe/include/optix.h
```

The OptiX backend was rebuilt successfully with:

```text
make build-optix OPTIX_PREFIX=/tmp/optix-sdk-probe
```

Artifact:

- `history/internal_docs/goal4851_am1_make_build_optix_with_prefix.log`

Post-rebuild smoke checks:

- `history/internal_docs/goal4851_planar_map_lsi_metadata_after_am1.json`
  - `native_predicate_mode: "planar_map_lsi"`
  - `native_predicate_legacy_alias: "rayjoin_lsi"`
- `history/internal_docs/goal4851_synthetic_after_am1_stdout.json`
  - synthetic semantic-delta probe still reports 6 differing shared-endpoint/boundary cases, matching the pre-amendment LSI contract evidence.

Interpretation:

The POD build issue is resolved. AM1 is now source-level and rebuilt-library verified on the active POD. The remaining AM2 debt is not a POD build problem; it is the product design debt of replacing the env-var selector with a native explicit predicate parameter.

## Non-Authorization

This response does not authorize:

- full Section 5.2 8/8 exact-input completion;
- Section 5.7 overlay;
- broad RTDL or RayJoin speedup;
- V3/V4 claims;
- Embree claims;
- treating restored `/dev/shm` caches as durable dataset management;
- full closure of AM2's native ABI debt.
