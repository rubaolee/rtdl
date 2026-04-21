# Goal 707: Claude Re-Review — RT-Core Red Line And DB/Graph/Spatial Audit

Date: 2026-04-21
Reviewer: Claude Sonnet 4.6 (claude-sonnet-4-6) — re-review after BLOCK
Prior verdict: **BLOCK** (see `goal707_claude_review_2026-04-21.md`)
This verdict: **ACCEPT**

---

## Scope

Re-review after the fix required by Finding 1 of the prior BLOCK. Checked:

- `src/rtdsl/app_support_matrix.py` — Python source of truth
- `docs/app_engine_support_matrix.md` — Markdown matrix and OptiX performance table
- `tests/goal707_app_rt_core_redline_audit_test.py` — test suite

---

## BLOCK Finding Resolved

### Finding 1 (was BLOCK, now RESOLVED): `direct_cli_native` / `host_indexed_fallback` contradiction

The prior review required changing `optix=_NATIVE` to `optix=_COMPAT` (`direct_cli_compatibility_fallback`) for four apps whose OptiX paths are `host_indexed_fallback`, resolving the mutual contradiction between the engine-matrix label and the performance classification.

**Python source (`src/rtdsl/app_support_matrix.py`):**

| App | Before | After |
| --- | --- | --- |
| `graph_analytics` (line 134) | `optix=_NATIVE` | `optix=_COMPAT` ✓ |
| `road_hazard_screening` (line 185) | `optix=_NATIVE` | `optix=_COMPAT` ✓ |
| `segment_polygon_hitcount` (line 195) | `optix=_NATIVE` | `optix=_COMPAT` ✓ |
| `segment_polygon_anyhit_rows` (line 206) | `optix=_NATIVE` | `optix=_COMPAT` ✓ |

**Markdown matrix (`docs/app_engine_support_matrix.md`):**

| App | OptiX column (observed) |
| --- | --- |
| `rtdl_graph_analytics_app.py` (line 26) | `direct_cli_compatibility_fallback` ✓ |
| `rtdl_road_hazard_screening.py` (line 31) | `direct_cli_compatibility_fallback` ✓ |
| `rtdl_segment_polygon_hitcount.py` (line 32) | `direct_cli_compatibility_fallback` ✓ |
| `rtdl_segment_polygon_anyhit_rows.py` (line 33) | `direct_cli_compatibility_fallback` ✓ |

The two representations are now internally consistent: each of the four apps carries `direct_cli_compatibility_fallback` (engine matrix) paired with `host_indexed_fallback` (performance class), which are compatible by definition.

**`database_analytics` (unaffected, confirmed correct):** Retains `direct_cli_native` for OptiX paired with `python_interface_dominated`. This is not a contradiction — real native OptiX BVH candidate discovery work exists; the Python packing, copy-back, and materialization overhead dominates the app-level timing, not the absence of native kernel work. No change warranted.

---

## Test Suite Assessment

The prior review rated the three-method test suite as PASS but noted it only verified document phrase presence. The fix adds a fourth test method:

```
test_host_indexed_optix_apps_are_marked_compatibility_fallback
```

This test calls `rt.app_engine_support_matrix()` and `rt.optix_app_performance_support()` directly, asserting `"direct_cli_compatibility_fallback"` and `"host_indexed_fallback"` for each of the four apps. It would have failed against the pre-fix data and passes against the corrected data. This is a meaningful structural gate: future edits to the Python source that revert these four apps toward `_NATIVE` will be caught automatically.

The test suite is now stronger than at the time of the BLOCK. No additional test changes are needed.

---

## Unchanged Findings (all PASS from prior review)

- **Red line (Finding 2):** Five definitional statements are technically correct and mutually consistent. No changes made or needed.
- **DB/graph/spatial status assessments (Finding 3):** Honest and internally consistent throughout. No changes made or needed.
- **Application catalog honesty boundary (Finding 5):** `"RTDL owns the accelerated core only when the app routes"` confirmed present at line 14 of `docs/application_catalog.md`. No changes made or needed.

---

## Verdict: ACCEPT

All three required conditions are met:

1. The four host-indexed OptiX apps (`graph_analytics`, `road_hazard_screening`, `segment_polygon_hitcount`, `segment_polygon_anyhit_rows`) now carry `direct_cli_compatibility_fallback` in both the Python source and the Markdown matrix.
2. The contradiction between `direct_cli_native` and `host_indexed_fallback` is fully resolved. No remaining label inconsistencies were found.
3. The test suite now includes a structural gate on the Python data layer, not just document text, and is sufficient for a consensus-gate check at this goal stage.

The document set — audit report, engine support matrix, OptiX performance and benchmark readiness tables, application catalog, and tests — is now internally consistent and ready to serve as authoritative public evidence for Goal 707.
