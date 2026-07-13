# Goal4913 — Planar-Map Workspace API Implementation

Date: 2026-07-03

## Requested Verdict

`completed_goal4913_workspace_api_implemented__tests_pass__no_new_performance_claim`

## Goal

Implement the Goal4912-approved in-process workspace/session API:

```text
prepare public planar-map inputs and primitive handles once
→ reuse them across hot query bodies
→ keep app continuation and output assembly outside RTDL core
```

This goal turns the previously hand-built prepared-session harness pattern into
a public RTDL lifecycle object. It does not add a RayJoin-specific kernel and
does not expose raw OptiX callbacks.

## Files Changed

Product/API:

```text
src/rtdsl/optix_runtime.py
src/rtdsl/__init__.py
```

Tests:

```text
tests/goal4913_planar_map_workspace_api_test.py
```

## New Public API

```python
from rtdsl import prepare_planar_map_workspace_2d_optix

with prepare_planar_map_workspace_2d_optix(left_cdb, right_cdb, cache_dir=cache) as ws:
    pair_rows = ws.run_lsi_pair_id_rows()
    left_faces = ws.run_left_points_in_right()
    right_faces = ws.run_right_points_in_left()
```

Exports:

```text
PlanarMapWorkspace2DOptix
prepare_planar_map_workspace_2d_optix
```

## What The Workspace Owns

The workspace owns:

- loaded/packed planar-map inputs;
- shared scale bounds;
- prepared public planar-map LSI base handle;
- prepared public planar-map LSI query handle;
- prepared public point-location handle for left points in right map;
- prepared public point-location handle for right points in left map;
- setup phase timings;
- context-manager close semantics.

It exposes:

- `run_lsi_pair_id_rows()`;
- `run_lsi_raw()`;
- `run_left_points_in_right()`;
- `run_right_points_in_left()`;
- `metadata()`;
- `close()`.

## Boundary

The implementation deliberately does not:

- import or call `rtdsl.rayjoin_overlay`;
- expose raw OptiX callback / shader hooks;
- add cross-process OptiX GAS serialization;
- move RayJoin app logic into RTDL core;
- make new performance claims;
- change LSI/PIP correctness semantics.

The workspace is a generic planar-map lifecycle API. RayJoin Section 5.7 can use
it, but the API is not named after RayJoin and does not contain overlay-specific
output logic.

## Verification

Commands run locally:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal4913_planar_map_workspace_api_test tests.goal4851_planar_map_lsi_public_front_door_test tests.goal4857_planar_map_point_location_public_front_door_test
```

Result:

```text
Ran 15 tests in 0.028s
OK
```

Compile check:

```text
$env:PYTHONPATH='src'; py -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/__init__.py tests/goal4913_planar_map_workspace_api_test.py
```

Result:

```text
passed
```

First run note:

The first unittest attempt failed because the local Windows shell did not have
`PYTHONPATH=src`, so `rtdsl` was not importable. Re-running with the project
source path fixed the environment issue. This was a command/environment issue,
not a code failure.

## Test Coverage Added

`tests/goal4913_planar_map_workspace_api_test.py` verifies:

1. public export of `PlanarMapWorkspace2DOptix` and
   `prepare_planar_map_workspace_2d_optix`;
2. the workspace prepares public LSI/PIP sessions once and reuses them;
3. `close()` closes LSI query, LSI base, and both point-location locators;
4. packed-cache environment override is restored after loading path inputs;
5. workspace source does not import bundled `rayjoin_overlay`;
6. workspace metadata records claim boundaries.

Existing public primitive tests were also re-run:

- Goal4851 LSI public front door;
- Goal4857 point-location public front door.

## Expected Performance Impact

No new performance claim is made in this goal.

The implementation productizes the already measured prepared-hot path:

- Goal4902: point-location session reuse reduced hot body from `11.320s` to
  `6.915s`;
- Goal4904: prepared LSI query replay reduced LSI from `1.814s` to `0.006s`;
- Goal4910: current best prepared-hot body is `3.918s`, byte-equal.

Goal4913 is the API/lifecycle productization step that makes this route
available to users without a hand-built internal harness.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   No. I implemented the already-reviewed in-process workspace, not a broad
   native cache or callback system.

2. **What action would have made this stupid?**

   Hiding RayJoin overlay logic inside the workspace, or claiming a new speedup
   without rerunning performance.

3. **Was there another path?**

   Yes: stop after Goal4911 and only document current results. But the user asked
   to continue improving the product, and Goal4912 approved this exact API
   productization.

4. **Can I start a different path that truly solves the problem?**

   Yes. After this review, the next meaningful step is a POD smoke that rewires
   the Australia representative harness to use the workspace API and verifies
   byte equality plus no hot-body regression. That should be Goal4914, not part
   of this implementation report.
