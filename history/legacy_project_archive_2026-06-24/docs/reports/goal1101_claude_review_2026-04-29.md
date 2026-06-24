# Goal1101 Claude Review

Date: 2026-04-29
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT with minor notes**

---

## Files Reviewed

- `scripts/goal1101_current_contract_non_optix_baseline_profiler.py`
- `scripts/goal1101_current_contract_non_optix_baseline_runner.sh`
- `tests/goal1101_current_contract_non_optix_baseline_profiler_test.py`
- `docs/reports/goal1101_current_contract_non_optix_baseline_profiler_2026-04-29.md`
- `docs/reports/goal1100_two_ai_consensus_2026-04-29.md` (prior gap audit)

---

## Criterion 1: Replayable same-current-contract non-OptiX baseline collection

**PASS.**

Both apps are covered with the correct scenario names matching the Goal1100 gap audit:

| App | Scenario | Path name |
| --- | --- | --- |
| `facility_knn_assignment` | `facility_service_coverage_recentered` | `coverage_threshold_prepared_recentered` |
| `barnes_hut_force_app` | `barnes_hut_node_coverage` | `node_coverage_prepared_rich` |

Replayability is enforced at two levels:

1. **Source commit captured.** `_source_commit()` reads `RTDL_SOURCE_COMMIT` env var, `.rtdl_source_commit` file, or falls back to `git rev-parse HEAD`. The runner script refuses with exit code 2 if the commit is empty.
2. **Schema version stamped.** Each artifact carries `schema_version: goal1101_current_contract_non_optix_baseline_v1`, `host`, `generated_at`, and full `parameters` for unambiguous replay.

The facility recentering logic (`_recenter_facility_points`: `x -= (id // 100) * 6`) and the canonical depot extraction (`make_facility_knn_case(copies=1)["depots"]`) are consistent: multi-copy customers are brought back into the canonical coordinate frame before the radius query and oracle, so the Embree threshold test and oracle both operate in the same space.

Runner rows match the four rows called out in Goal1100:

| Row | Scale | Contract |
| --- | --- | --- |
| Facility CPU oracle | 2.5M copies | radius 1.0, threshold 1 |
| Facility Embree | 2.5M copies | radius 1.0, threshold 1 |
| Barnes-Hut validation | 4096 bodies, depth 8, threshold 4 | radius 0.1 |
| Barnes-Hut timing | 20M bodies, depth 8, threshold 4 | radius 0.1, skip-validation |

---

## Criterion 2: Real Embree prepared threshold API

**PASS.**

The profiler calls:

```python
prepared = rt.prepare_embree_fixed_radius_count_threshold_2d(build_points)
rows = prepared.run(query_points, radius=radius, threshold=hit_threshold)
_, close_sec = _time_call(prepared.close)  # inside finally
```

This is the correct three-step prepared surface: `prepare → run → close`. The `finally` block guarantees `.close()` is always called even on exception. The `threshold_reached` field from each row is read as `int(row["threshold_reached"]) != 0`, matching the expected API contract.

**Minor note:** `pack_sec` in the timings output is always `0.0` because there is no point-packing step — the points are passed directly to `prepare`. The field name `point_pack_sec` suggests a packing phase that does not exist. This is cosmetically misleading but has no functional impact; future consumers should ignore it or it should be removed.

---

## Criterion 3: No-public-speedup-claim boundaries

**PASS.**

Every artifact emitted by `run_profile` carries:

```json
"public_speedup_claim_authorized": false,
"boundary": "Goal1101 collects same-current-contract non-OptiX baseline artifacts for later review. It does not authorize public RTX speedup claims; claim review still requires artifact intake and 2+ AI consensus."
```

The runner script also has an explicit comment boundary and refuses to run without a verifiable `RTDL_SOURCE_COMMIT`. The profiler report's Boundary section correctly states that public wording remains blocked until artifacts are reviewed against RTX A5000 artifacts.

---

## Criterion 4: Test adequacy

**PASS with minor gaps.**

Three tests are present:

| Test | What it checks |
| --- | --- |
| `test_cpu_oracle_facility_recentered_profile_preserves_no_claim_boundary` | CPU oracle facility path: app, path_name, backend, matches_oracle, claim boundary |
| `test_embree_barnes_profile_uses_prepared_threshold_surface` | Embree Barnes-Hut path: mocked prepare API, call count, timing captured, matches_oracle |
| `test_cli_writes_json_artifact` | CLI subprocess: JSON written, schema_version, claim boundary |

The claim boundary (`public_speedup_claim_authorized: False`, boundary text) is asserted in two of three tests. The `prepare_embree_fixed_radius_count_threshold_2d` mock correctly verifies the function is called exactly once per `run_profile` call (not once per iteration).

**Minor gaps:**

1. **Embree facility path has no unit test.** Only CPU oracle facility and Embree Barnes-Hut are covered at the unit level. The Embree facility case is structurally identical to Embree Barnes-Hut in the `_profile_threshold` function, so the risk is low, but a smoke test with a mocked prepare for the facility scenario would remove the gap.
2. **`_recenter_facility_points` is not tested in isolation.** The recentering logic is the most domain-specific piece of the profiler; a direct unit test asserting the coordinate mapping for a few synthetic points would be valuable for future maintainers.
3. **`skip_validation=True` is not covered by any test.** The timing-only Barnes-Hut row (20M bodies) relies on this flag. A minimal test checking that `oracle_all_queries_reached_threshold` is `None` when `skip_validation=True` would close this.

None of these gaps affect correctness for the current four runner rows; they are notes for future hardening.

---

## Overall Assessment

Goal1101 correctly addresses both Goal1100 baseline gaps. The replayability machinery (commit guard, schema version, host capture) is sound. The Embree prepared threshold API is used correctly with proper resource management. The no-speedup-claim boundary is present and machine-checkable. Tests cover the primary paths and boundary enforcement.

The three minor notes (always-zero `pack_sec` field, missing Embree facility unit test, missing `skip_validation` test) are cosmetic or low-risk. They do not block acceptance.

**Verdict: ACCEPT.**
