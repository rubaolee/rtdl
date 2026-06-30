# Goal635: v0.9.5 Pre-Release Gate — Claude Review

Date: 2026-04-19
Reviewer: Claude Sonnet 4.6

## Verdict

**ACCEPT**

No release-blocking findings.

## Gate Items Verified

| Item | Status |
|------|--------|
| Full test suite: 1187 tests OK (skipped=171) | PASS |
| Focused any-hit + visibility tests: 22 tests OK | PASS |
| Public doc command audit (`goal497`, `goal515`): both valid | PASS |
| Feature cookbook smoke: 24 features, includes `ray_tri_anyhit` and `visibility_rows` | PASS |
| Claude Goal632/633 review: ACCEPT | PASS |
| Gemini Flash Goal632/633 review: ACCEPT | PASS |
| Goal631 acceptance ladder: all Goal632/633/634 criteria satisfied | PASS |

## Independent Source Spot-Check

- `reference.py:180–192` — `ray_triangle_any_hit_cpu`: early-exit `break` present, output schema is `{ray_id, any_hit}`. Correct.
- `reference.py:224–278` — `visibility_rows_cpu`: full direction vector with `tmax=1.0` bounds intersection to the observer–target segment. Correct.
- `api.py:144` — `ray_triangle_any_hit(*, exact=False)` returns a `Predicate`. Correct.
- `runtime.py:172–173` — dispatches `ray_triangle_any_hit` to `ray_triangle_any_hit_cpu`. Correct.
- `oracle_runtime.py:327–330` — `ray_triangle_any_hit` falls through to Python reference via `candidates.left`/`right`. Consistent with `ray_triangle_closest_hit` pattern.
- `__init__.py` — `ray_triangle_any_hit`, `ray_triangle_any_hit_cpu`, `visibility_rows_cpu` all present in imports and `__all__`. Correct.

## Non-Blocking Observations

None beyond those already recorded in the Goal632/633 Claude review (oracle input-ordering assumption, mixed 2D/3D validation site). Neither is a regression introduced in v0.9.5.

## Scope Honesty

Docs correctly represent this as a language/reference/oracle contract slice. No native backend early-exit kernels and no performance speedup claims are made. Visibility rows are documented as a CPU standard-library spatial-query helper, not a renderer or scene system.
