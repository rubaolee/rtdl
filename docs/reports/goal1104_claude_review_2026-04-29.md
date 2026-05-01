# Goal1104 Claude Review

Date: 2026-04-29  
Reviewer: Claude Sonnet 4.6  
Verdict: **PASS — with one minor test-coverage note**

---

## 1. Barnes-Hut Embree Baseline Artifact

**Valid.**

`docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_4096_embree_validation_baseline.json`

| Check | Result |
| --- | --- |
| `matches_oracle` | `true` |
| `query_count` / `threshold_reached_count` | 4096 / 4096 — all queries reached threshold |
| `node_count` | 65536 — consistent with depth-8 fixed quad-tree (4096 × 2⁴) |
| `barnes_tree_depth` / `hit_threshold` / `radius` | 8 / 4 / 0.1 — match Goal1104 spec exactly |
| `backend` | `embree` |
| `source_commit` | `c500a63fe36efaeac994159e8c37f72797398d85` — matches HEAD at execution time |
| `public_speedup_claim_authorized` | `false` |
| `schema_version` | `goal1101_current_contract_non_optix_baseline_v1` |
| Timing plausibility | `native_query_sec.median` ≈ 4.9 ms for 4096 points — plausible on ARM64 Embree |

No anomalies. All three timing iterations recorded (min/median/max populated); validation timing is present and non-zero, confirming `skip_validation` was not in effect.

---

## 2. Goal1102 Intake Counts

**Correct.**

`docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.json`

| Field | Value | Expected |
| --- | --- | --- |
| `ok_count` | 1 | 1 (barnes_hut_validation_embree) |
| `missing_count` | 3 | 3 (facility_cpu_oracle, facility_embree, barnes_hut_timing_embree) |
| `blocked_count` | 0 | 0 |
| `public_speedup_claim_authorized_count` | 0 | 0 |
| `artifact_set_complete` | `false` | `false` |
| `overall_status` | `waiting_for_baseline_artifacts` | correct |

The three missing rows are intentionally absent: Goal1103 classified the facility-recentered runs (2.5M copies) and Barnes-Hut 20M timing run as high-to-very-high risk for the 16 GB Mac. Their absence is correct, not a defect.

---

## 3. Source-Commit Stale-File Fix

**Correctly implemented; archive pod fallback preserved.**

The `.rtdl_source_commit` file on disk contains `21fa036881bf9a0c806f69c15727d87b482ccfcf` — a stale pod commit that differs from HEAD (`c500a63...`). Without the fix, the profiler would have recorded the wrong commit in the artifact.

**Fix in both profilers** (`goal887_prepared_decision_phase_profiler.py:100–118`, `goal1101_current_contract_non_optix_baseline_profiler.py:57–75`):

```
1. RTDL_SOURCE_COMMIT env var   (set explicitly at execution time)
2. git rev-parse HEAD            (live lookup; authoritative on any git checkout)
3. .rtdl_source_commit           (fallback — only reached when git is unavailable,
                                  i.e. archive-style pod with no .git directory)
```

**Fix in runner scripts** (`goal1084`, `goal1093`, `goal1101`):

```bash
export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(git rev-parse HEAD 2>/dev/null || cat .rtdl_source_commit 2>/dev/null || true)}"
```

All three scripts then abort with exit code 2 if `RTDL_SOURCE_COMMIT` is still empty after the fallback chain. This mirrors the profiler logic and is consistent.

**Archive pod fallback is intact**: the file path `.rtdl_source_commit` is still checked as last resort in both the Python `_source_commit()` functions and the shell runners. A pod with no `.git` directory but a populated `.rtdl_source_commit` (written at image-build time) will still produce a stamped artifact.

**Minor test-coverage gap (non-blocking):** `test_source_commit_prefers_git_head_over_stale_source_file` confirms git HEAD is used, but does not cover the case where git is unavailable and the file is the only source. The archive pod fallback path has no unit-test coverage. This is low risk given it is the pre-existing path and the test confirms the priority order is correct, but it would be worth adding a mock-git-failure test in a follow-up.

---

## 4. Public Speedup Claim Gate

**No claim authorized — confirmed at every layer.**

| Location | Field | Value |
| --- | --- | --- |
| Artifact JSON | `public_speedup_claim_authorized` | `false` |
| Intake JSON | `public_speedup_claim_authorized_count` | 0 |
| Intake JSON | `artifact_set_complete` | `false` |
| Intake JSON | `overall_status` | `waiting_for_baseline_artifacts` |
| Goal1104 report | boundary statement | "does not authorize public RTX speedup claims" |
| Test | `test_cpu_oracle_facility_recentered_profile_preserves_no_claim_boundary` | `public_speedup_claim_authorized` asserted `false` |
| Test | `test_embree_facility_profile_can_skip_validation_for_timing_rows` | `public_speedup_claim_authorized` asserted `false` |

The baseline set is incomplete (1/4 rows present). Even a complete set would still require 2+ AI consensus review and a separate public wording gate, both of which are recorded in the intake boundary string and the artifact boundary string. No speedup claim is authorized at this stage.

---

## Summary

All four review criteria pass. The Barnes-Hut Embree artifact is valid and correctly stamped. The intake correctly reflects 1 ok / 3 missing. The source-commit priority fix works as described and preserves the archive pod fallback. No public speedup claim is authorized or implied at any layer. The one non-blocking gap is missing unit test coverage for the git-unavailable fallback path in `_source_commit()`.
