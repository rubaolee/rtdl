# Goal4857 - Clean Planar-Map Point-Location Public Front Door

Date: 2026-07-01

## Purpose

Clean the Section 5.3 PIP reproduction route so it is clearly a RTDL generic
primitive route, not a RayJoin-specific helper route and not a user script that
manually drives RayJoin-era environment variables.

The concrete cleanup target was:

```python
with prepare_planar_map_point_location_2d_optix(base, query_map_id=1, scale_bounds=bounds) as pip:
    rows = pip.run_raw(points)
```

instead of:

```python
with _point_location_env(...):
    with prepare_directed_segment_point_location_2d_optix(base) as locator:
        rows = locator.run_raw(points)
```

## What Changed

### 1. Public dataset adapter names

Added application-neutral aliases in `src/rtdsl/datasets.py`:

- `chains_to_planar_map_segments(dataset)`
- `chains_to_planar_map_points(dataset)`

These preserve the face-id payload needed by planar-map point-location/PIP and
LSI without forcing users to call a `rayjoin_*` adapter name.

### 2. Public OptiX primitive

Added `prepare_planar_map_point_location_2d_optix` and
`PreparedOptixPlanarMapPointLocation2D` in `src/rtdsl/optix_runtime.py`.

The new wrapper:

- exposes the public primitive name `PLANAR_MAP_POINT_LOCATION_2D`;
- delegates to the already repaired directed point-location native path;
- hides the legacy `RTDL_RAYJOIN_CDB_*` environment bridge inside RTDL;
- restores environment variables after each call;
- guards the bridge with a process-local lock;
- records metadata stating `bundled_rayjoin_helper_used: false`;
- does not import or call `rtdsl.rayjoin_overlay`.

This is not a new RayJoin kernel. It is a public planar-map point-location/PIP
front door over the same core primitive that Section 5.3 needs.

Scope correction after Claude review: this goal is an API-boundary cleanup.  It
does not add new PIP correctness evidence by itself.  Correctness claims must
continue to cite the separate Section 5.3/point-location correctness artifacts
that actually run AuthorPatch-vs-RTDL comparisons.  Passing this goal's export,
metadata, and environment-bridge tests must not be read as "PIP is correct" or
"Section 5.3 is complete."

The public claim is therefore narrower: RTDL exposes a cleaner public front door
over the historical native point-location route.  It is not yet a fully
generalized first-class native planar-map point-location ABI; the lower native
compatibility bridge still uses historical `RTDL_RAYJOIN_CDB_*` names behind the
wrapper.

### 3. Public exports and feature matrix

Updated:

- `src/rtdsl/__init__.py`
- `src/rtdsl/engine_feature_matrix.py`

New feature id:

- `planar_map_point_location_2d`

OptiX is marked `native`; the other engines are `unsupported_explicit` for this
specific public front door.

### 4. Internal Section 5.3 runners migrated

Updated internal evidence runners:

- `history/internal_docs/goal4855_rayjoin_section53_pip_public_front_door.py`
- `history/internal_docs/goal4856_rtdl_section53_pip_raw_diagnostic.py`

They now import and use `prepare_planar_map_point_location_2d_optix`.

They no longer define or import `_point_location_env`, and they no longer set
`RTDL_RAYJOIN_CDB_*` variables in user/application code.

### 5. User-visible docs

Updated:

- `docs/rtdl_feature_guide.md`
- `docs/features/engine_support_matrix.md`
- `docs/features/pip/README.md`
- `docs/features/lsi/README.md`

The docs now describe planar-map LSI and planar-map point-location/PIP as paired
public primitives, while explicitly refusing overlay and broad performance
claims.

After Claude review, the docs also clarify that the new front door is currently
OptiX-only and that the internal compatibility bridge is guarded and restored
but serializes overlapping calls through a process-local lock.

### 6. Regression tests

Added:

- `tests/goal4857_planar_map_point_location_public_front_door_test.py`

The test verifies:

- public export of `prepare_planar_map_point_location_2d_optix`;
- public export of `PreparedOptixPlanarMapPointLocation2D`;
- feature matrix support for `planar_map_point_location_2d`;
- public dataset aliases;
- environment bridge is internal and restored after use;
- metadata says this is a generic public primitive, not bundled RayJoin helper;
- Section 5.3 internal runners use the new front door and no longer import the old env helper.

## Verification

Passed:

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

Passed:

```text
PYTHONPATH=src;. py -m py_compile \
  history/internal_docs/goal4855_rayjoin_section53_pip_public_front_door.py \
  history/internal_docs/goal4856_rtdl_section53_pip_raw_diagnostic.py \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/datasets.py \
  src/rtdsl/__init__.py \
  src/rtdsl/engine_feature_matrix.py
```

Additional scan:

- No `prepare_directed_segment_point_location_2d_optix` in the two Section 5.3 internal runners.
- No `_point_location_env` in the two Section 5.3 internal runners.
- No direct `RTDL_RAYJOIN_CDB_*` use in those runners.

Known unrelated failure:

```text
tests.goal4274_current_doc_recheck_test
```

This test still points to the old `docs/reports/goal4274_current_doc_recheck_2026-06-10.md`
path, which was moved during the public-surface cleanup. It is unrelated to
the planar-map point-location API cleanup.

## Boundaries

- This does not claim Section 5.3 all-eight completion.
- This does not claim Section 5.7 overlay.
- This does not claim broad RayJoin performance.
- This does not claim broad RTDL performance.
- This does not claim PIP correctness by itself; correctness must be established
  by separate data-bearing AuthorPatch-vs-RTDL evidence.
- This does not remove the lower-level compatibility names; old internal code
  can still call them.
- This does not yet replace the native environment bridge with a first-class
  ABI parameter. The bridge is now hidden and guarded at the public Python API
  boundary, but overlapping calls through this public front door are serialized
  by the process-local lock. A deeper native ABI cleanup remains optional future
  work.

## Claude Review Amendments Applied

Claude review file:

- `history/internal_docs/claude_goal4857_planar_map_point_location_review_2026-07-01.md`

Amendments:

- AM1: narrowed the exit claim to API-boundary cleanup only; PIP correctness is
  inherited from separate correctness artifacts and remains outside this goal.
- AM2: explicitly described this as a public front door over a historical native
  route, not a fully generalized native ABI.
- AM3: documented that the lock makes the bridge safe but serializes overlapping
  calls, and clarified that this public front door is OptiX-only.

## Exit Label

Recommended:

`completed_planar_map_point_location_public_front_door_cleanup`
