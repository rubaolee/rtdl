# Goal4914 — Workspace API POD Smoke

Date: 2026-07-03

## Requested Verdict

`completed_goal4914_workspace_api_pod_smoke__byte_equal__no_hot_regression`

## Goal

Validate that the Goal4913 public workspace API is not only a local unit-test
wrapper. It must run the Australia representative Section 5.7 app path on the
NVIDIA POD using:

```text
public PlanarMapWorkspace2DOptix
public planar-map LSI
public planar-map point-location/PIP
Numba app-layer continuation/writer
```

The goal is integration and regression control. It does not claim a new speedup.

## Files

Runner:

```text
history/internal_docs/goal4914_workspace_api_smoke.py
```

POD summary:

```text
history/internal_docs/goal4914_workspace_api_smoke_summary_2026-07-03.json
```

## POD Command

Run on:

```text
root@157.157.221.29:23132
```

Worktree:

```text
/workspace/goal4894_productize_20260703b
```

Command shape:

```text
PYTHONPATH=src python history/internal_docs/goal4914_workspace_api_smoke.py \
  --left /workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb \
  --right /workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb \
  --author-output /workspace/goal4875_section57_au_representative/author_contract_full/author_contract_au_overlay.txt \
  --output-template history/internal_docs/goal4914_workspace_repeat{repeat}.txt \
  --summary history/internal_docs/goal4914_workspace_api_smoke_summary_2026-07-03.json \
  --cache-dir /workspace/goal4894_productize_20260703b/packed_cache_goal4895_new \
  --repeat 2
```

## Result

### Correctness

Both repeats are byte-equal to AuthorOfficial:

```text
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
bytes:  6189260
lines:  276320
```

Counts:

| Metric | Value |
|---|---:|
| LSI row count | `13452` |
| xsects map0 | `13452` |
| xsects map1 | `13452` |
| vertex positives map0 in map1 | `193846` |
| vertex positives map1 in map0 | `30538` |

### Hot-Body Regression Check

Reference:

```text
Goal4910 best prepared-hot body: 3.918s
5% regression threshold:        4.114s
```

Goal4914 workspace repeat 1:

```text
elapsed_sec: 3.955s
```

Regression:

```text
3.955 / 3.918 = 1.0094x
```

This is within the 5% threshold. The workspace API preserves the hot path.

### Repeat 1 Phase Breakdown

| Phase | Time |
|---|---:|
| workspace LSI pair-id rows | `0.006s` |
| intersection reprojection | `0.468s` |
| sort map0 | `0.211s` |
| sort map1 | `0.204s` |
| vertex PIP map0 in map1 | `1.090s` |
| vertex PIP map1 in map0 | `0.029s` |
| output writer | `1.875s` |
| total hot body | `3.955s` |

Workspace setup:

| Setup phase | Time |
|---|---:|
| load/pack left | `2.281s` |
| load/pack right | `0.788s` |
| prepare LSI base | `0.514s` |
| prepare LSI query | `0.690s` |
| prepare point-location left in right | `1.354s` |
| prepare point-location right in left | `5.934s` |
| total workspace prepare wrapper | `11.561s` |

This confirms the earlier conclusion: the workspace is a repeated-query/hot
session API. It does not erase cold setup cost.

## Claim Boundary

The JSON records:

```text
public_planar_map_workspace_used: true
public_lsi_used: true
public_point_location_used: true
numba_on_app_continuation_path: true
numba_on_rtdl_primitive_path: false
bundled_rayjoin_overlay_imported: false
broad_performance_claim: false
single_run_speedup_claim: false
```

Workspace metadata records:

```text
public_generic_rtdl_workspace: true
bundled_rayjoin_helper_used: false
raw_optix_callback_exposed: false
cross_process_gas_cache: false
application_continuation_inside_rtdl_core: false
broad_speedup_claim_authorized: false
```

## Interpretation

Goal4914 proves that Goal4913 is a real product integration:

```text
The hand-built prepared-session harness can be replaced by public
PlanarMapWorkspace2DOptix without losing correctness and without meaningful
hot-path regression.
```

This is not a new algorithm and not a RayJoin-specific core path. It is a
generic lifecycle API for the already measured RTDL prepared-session route.

## Not Authorized

This goal does not authorize:

- broad RayJoin performance claims;
- single-run speedup claims;
- raw OptiX callback exposure;
- cross-process GAS cache claims;
- V3/V4 resurrection;
- public release wording changes.

## Recommendation

Close Goal4914 as successful.

The next rational choices are now:

1. consolidate the current bounded performance story; or
2. if continuing optimization, target a deeper compiled output descriptor path
   for intersection-bearing chains, because shallow Python writer tweaks are
   already exhausted and point-location group-mode tuning is exhausted.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   No. This goal validated the new API on the real POD path before claiming it
   as product-ready.

2. **What action would have made this stupid?**

   Calling the 3.955s result a new performance win. It is a no-regression
   integration proof, not a speedup claim.

3. **Was there another path?**

   Yes: skip POD and trust unit tests. That would have been weak because the
   point of this API is preserving prepared-hot behavior on the actual GPU path.

4. **Can I start a different path that truly solves the problem?**

   Yes. After this, further speed work should either stop and consolidate or
   move to a genuinely compiled descriptor/output path. It should not return to
   group-mode tuning or shallow writer micro-edits.
