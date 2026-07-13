# Call For Claude Review - Goal4857 Planar-Map Point-Location Public Front Door Cleanup

Date: 2026-07-01

Claude, please critically review Goal4857.

## Context

We are cleaning the RayJoin Section 5.3 PIP reproduction route after discovering
that the working route was mostly correct but still looked too RayJoin-specific
at the user/application boundary.

Before Goal4857, the Section 5.3 RTDL user scripts used:

```python
with _point_location_env(...):  # user-side RTDL_RAYJOIN_CDB_* bridge
    with prepare_directed_segment_point_location_2d_optix(base) as locator:
        rows = locator.run_raw(points)
```

Goal4857 changed this to:

```python
with prepare_planar_map_point_location_2d_optix(
    base,
    query_map_id=1,
    scale_bounds=bounds,
) as pip:
    rows = pip.run_raw(points)
```

The intended distinction:

- Public API should say "planar-map point-location/PIP", not "RayJoin helper".
- User/application code should not set `RTDL_RAYJOIN_CDB_*` directly.
- The lower compatibility bridge may still use historical environment variables
  internally for now, but they should be hidden and restored by RTDL.
- This is not a Section 5.7 overlay claim, not an all-eight Section 5.3 claim,
  and not a broad performance claim.

## Files To Review

Primary report:

- `history/internal_docs/goal4857_planar_map_point_location_public_front_door_cleanup_2026-07-01.md`

Existing Antigravity review:

- `history/internal_docs/antigravity_goal4857_planar_map_point_location_public_front_door_cleanup_review_2026-07-01.md`

Code:

- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/datasets.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/engine_feature_matrix.py`
- `tests/goal4857_planar_map_point_location_public_front_door_test.py`

Internal Section 5.3 runners:

- `history/internal_docs/goal4855_rayjoin_section53_pip_public_front_door.py`
- `history/internal_docs/goal4856_rtdl_section53_pip_raw_diagnostic.py`

Docs:

- `docs/rtdl_feature_guide.md`
- `docs/features/engine_support_matrix.md`
- `docs/features/pip/README.md`
- `docs/features/lsi/README.md`

## Verification Already Run

```text
PYTHONPATH=src;. py -m unittest \
  tests.goal4373_rayjoin_cdb_point_location_route_test \
  tests.goal4857_planar_map_point_location_public_front_door_test \
  tests.goal4851_planar_map_lsi_public_front_door_test
```

Result:

```text
Ran 11 tests in 0.037s
OK
```

Also passed:

```text
PYTHONPATH=src;. py -m py_compile \
  history/internal_docs/goal4855_rayjoin_section53_pip_public_front_door.py \
  history/internal_docs/goal4856_rtdl_section53_pip_raw_diagnostic.py \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/datasets.py \
  src/rtdsl/__init__.py \
  src/rtdsl/engine_feature_matrix.py
```

## Requested Verdict Labels

Please choose one:

- `approve_goal4857_public_front_door_cleanup`
- `approve_with_required_amendments`
- `reject_goal4857_redo`

## Questions

1. Does `prepare_planar_map_point_location_2d_optix` establish a legitimate
   public generic planar-map point-location/PIP front door?
2. Or is it merely a RayJoin-specific helper hidden under a generic name?
3. Is it acceptable that the underlying implementation still uses
   `RTDL_RAYJOIN_CDB_*` internally, given that the public wrapper guards and
   restores the environment and user/application code no longer sets those
   variables directly?
4. Should the native bridge be considered acceptable for this cleanup, or must
   it be changed now to a first-class native ABI parameter before the cleanup can
   close?
5. Do `chains_to_planar_map_segments` and `chains_to_planar_map_points` improve
   the public user model without erasing compatibility with the older
   `chains_to_rayjoin_cdb_segments` name?
6. Do the Section 5.3 runners now avoid the old user-side `_point_location_env`
   and avoid direct `RTDL_RAYJOIN_CDB_*` use?
7. Are the docs bounded correctly, especially avoiding:
   - Section 5.7 overlay claims;
   - all-eight Section 5.3 claims;
   - broad RayJoin performance claims;
   - broad RTDL performance claims?
8. Are the tests sufficient for this cleanup, or is a stronger regression gate
   needed before closing?
9. Should Goal4857 close with
   `completed_planar_map_point_location_public_front_door_cleanup`?

## Specific Skeptical Point

Please be especially strict on this:

The public API name is now generic, but the lower native compatibility bridge is
still historically RayJoin-shaped.  Is the current boundary honest enough for
v2.14 product cleanup, or does it still risk misleading users into thinking RTDL
has a fully generalized planar-map point-location ABI when it currently exposes
a cleaned front door over a historical native route?

If you approve, please state exactly what claim is authorized and what claim is
not authorized.
