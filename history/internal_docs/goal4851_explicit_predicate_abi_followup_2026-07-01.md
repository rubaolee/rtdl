# Goal4851 Explicit Predicate ABI Follow-Up

Date: 2026-07-01

## Purpose

Close the remaining Goal4851 AM2 engineering debt: the public
`prepare_planar_map_lsi_2d_optix` front door must not select the planar-map LSI
predicate through process-global environment state.

## What Changed

- Added a native explicit-predicate C ABI:
  `rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_grouped_range_direct_intersection_with_predicate_mode`.
- Kept the old grouped-range count symbol unchanged for backward compatibility.
- Changed `PreparedOptixPlanarMapLsi2D.count_with_metadata()` to pass
  `predicate_mode=1` through the new native ABI.
- Removed the Python env-var predicate context from the public planar-map LSI
  path. The old native env-var fallback remains only behind old/native legacy
  entrypoints.
- Updated focused tests so the front door must keep
  `RTDL_OPTIX_SEGMENT_PAIR_PREDICATE` unset and pass the mode as a native
  parameter.

## Verification

Local:

- `PYTHONPATH=src py -m py_compile src/rtdsl/optix_runtime.py`
- `PYTHONPATH=src py -m unittest tests.goal4851_planar_map_lsi_public_front_door_test`
- Public doc leak scan on:
  - `docs/rtdl_feature_guide.md`
  - `docs/features/engine_support_matrix.md`
  - `docs/features/lsi/README.md`

POD:

- Host: `root@157.157.221.29 -p 23132`
- Worktree: `/workspace/rtdl_goal4817_user_smoke_20260630_102224`
- Build command:
  `make build-optix OPTIX_PREFIX=/tmp/optix-sdk-probe`
- New native symbol verified with `nm -D build/librtdl_optix.so`.
- Metadata smoke verified:
  - `native_predicate_mode: planar_map_lsi`
  - `native_predicate_mode_id: 1`
  - `predicate_selection.mechanism: native_abi_explicit_parameter`
  - `env_after: null`
  - raw native symbol is the new explicit-predicate symbol.
- Synthetic semantic-delta probe still reports 6 differing cases, preserving the
  intended distinction between raw segment-pair intersection and planar-map LSI.

## Artifacts

- `history/internal_docs/goal4851_explicit_predicate_build.log`
- `history/internal_docs/goal4851_explicit_predicate_metadata.json`
- `history/internal_docs/goal4851_explicit_predicate_synthetic_stdout.json`

## Boundary

This is still a count-only planar-map LSI primitive. It does not authorize:

- full RayJoin overlay reproduction claims,
- Section 5.7 paper reproduction claims,
- broad speedup claims,
- or any statement that the public primitive is an application-specific RayJoin
  kernel.

## Remaining Notes

The native implementation still contains historical names such as
`rayjoin_lsi_*` internally. The public front door and native exported predicate
mode now use `planar_map_lsi`; deeper internal symbol renaming can be handled as
a cleanup task, but it is no longer required to remove the env-var concurrency
risk from the public route.
