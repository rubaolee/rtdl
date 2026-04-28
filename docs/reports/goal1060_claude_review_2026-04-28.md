# Goal1060 External Review — Claude

Date: 2026-04-28
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Scope

Goal1060 compares the 11 accepted Goal1058 RTX A5000 artifacts (sourced from
`docs/reports/goal1052_post_goal1048_cloud_batch/`) against existing
same-semantics baselines. It must not authorize any public speedup wording, and
candidate rows must remain gated behind a separate 2-AI public wording review.

---

## Checks Performed

### 1. Artifact source matches Goal1058 consensus

Goal1058 three-AI consensus (`ACCEPT_FOR_SAME_SEMANTICS_REVIEW_RECORD`) accepted
exactly 11 artifacts from `goal1052_post_goal1048_cloud_batch`. Goal1060 reads
from that same directory with the same 11 `(app, path_name, file_name)` tuples.
All 11 `artifact_ok` fields are `true` in the produced JSON. No mismatch.

### 2. No public speedup authorization — hardcoded, not computed

- `public_speedup_claim_authorized` is set to the **literal** `False` for every
  row (script line 120). There is no code path that sets it to `True`.
- `public_speedup_claim_authorized_count` is set to the **literal** `0` in the
  summary dict (line 141). It is not derived by counting rows.
- The markdown output prints `public speedup claims authorized here: \`0\``.
- Both test cases assert these values:
  - `test_audit_classifies_…`: `assertEqual(payload["public_speedup_claim_authorized_count"], 0)`
  - `test_cli_writes_json_and_markdown`: `assertIn("public speedup claims authorized here: \`0\`", markdown)`

### 3. `facility_knn_assignment` — internal candidate, public wording blocked

| Field | Value |
| --- | --- |
| `recommendation` | `candidate_for_separate_2ai_public_claim_review` |
| `current_public_wording_status` | `public_wording_blocked` |
| `public_speedup_claim_authorized` | `false` |
| RTX phase | 0.001211 s |
| Fastest baseline (`cpu_oracle_same_semantics`) | 0.071395 s |
| Ratio (baseline / RTX) | 58.96× |
| Warning | "RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence." |

The internal candidate classification is correct: RTX is 58.96× faster than the
CPU oracle baseline. The `public_wording_blocked` status is faithfully propagated
from `rt.rtx_public_wording_status`, and the sub-10 ms timing-floor warning is
present. No tension between these fields — being an internal candidate does not
imply authorization.

### 4. `robot_collision_screening` — internal candidate, public wording blocked

| Field | Value |
| --- | --- |
| `recommendation` | `candidate_for_separate_2ai_public_claim_review` |
| `current_public_wording_status` | `public_wording_blocked` |
| `public_speedup_claim_authorized` | `false` |
| RTX phase | 0.002990 s |
| Fastest baseline (`embree_anyhit_pose_count_or_equivalent_compact_summary`) | 0.581851 s |
| Ratio (baseline / RTX) | 194.59× |
| Warning | "RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence." |

Same pattern as facility: large internal speedup ratio, correctly blocked from
public wording, sub-10 ms timing-floor warning present. The `public_wording_boundary`
field echoes the timing-floor concern explicitly.

### 5. Ratio arithmetic — spot check all 11 rows

Recomputed baseline/RTX ratios from JSON values against the reported
`fastest_ratio_baseline_over_rtx` field:

| App | Computed ratio | Reported ratio | Match |
| --- | ---: | ---: | --- |
| facility_knn_assignment | 58.963× | 58.963× | ✓ |
| robot_collision_screening | 194.589× | 194.589× | ✓ |
| database_analytics / sales_risk | 0.605× | 0.605× | ✓ → reject |
| database_analytics / regional_dashboard | 0.919× | 0.919× | ✓ → reject |
| graph_analytics | 0.431× | 0.431× | ✓ → reject |
| event_hotspot_screening | 1.546× | 1.546× | ✓ → candidate |
| road_hazard_screening | 0.037× | 0.037× | ✓ → reject |
| polygon_pair_overlap_area_rows | 0.000611× | 0.000611× | ✓ → reject |
| polygon_set_jaccard | 0.005056× | 0.005056× | ✓ → reject |
| hausdorff_distance | 0.005733× | 0.005733× | ✓ → reject |
| barnes_hut_force_app | 0.392× | 0.392× | ✓ → reject |

All ratios are correct. The 3 candidate rows (facility, robot, event_hotspot)
each have ratio > 1.2× against every timed same-semantics baseline. The 8 reject
rows each have ratio < 1.0 against the fastest timed baseline (RTX slower).

### 6. Baseline provenance

Every row uses `baseline_status: same_semantics_baselines_complete` and
`baseline_complete_for_speedup_review: true`. Baseline paths reference the
established `goal835_baseline_*` files. All `correctness_parity: true`.
Claim-limit annotations on each baseline correctly prevent over-broad wording
(e.g., "bounded sub-path only", "scalar pose-count collision screening only").

### 7. `_classify` reuse

Goal1060 imports `_classify` from `goal1005_post_a5000_speedup_candidate_audit`
(proven in prior goals) rather than reimplementing classification logic. This
reduces the risk of introducing an unauthorized claim path via a new code path.

### 8. Boundary statement

The boundary string appears three times: the JSON `boundary` field, the markdown
header, and the markdown `## Boundary` section. It is unambiguous:

> "It does not authorize public speedup wording; candidate rows still require
> separate 2-AI public wording review."

### 9. Test coverage

The unit test asserts:
- `valid == True`, `row_count == 11`, `public_speedup_claim_authorized_count == 0`
- `facility` recommendation is `candidate_for_separate_2ai_public_claim_review`
- `robot` `current_public_wording_status` is `public_wording_blocked`
- `event_hotspot_screening` recommendation is `candidate_for_separate_2ai_public_claim_review`
- `database_analytics/sales_risk` recommendation is `reject_current_public_speedup_claim`
- CLI produces `"valid": true` and the zero-claims markdown string

Coverage is appropriate for the boundary conditions.

---

## Issues Found

None. No code path produces a `true` public authorization. Timing-floor warnings
are present on both sub-10 ms candidate rows. `public_wording_blocked` is
correctly propagated and does not conflict with internal candidate classification.
The audit is strictly comparative; it does not modify source code or baselines.

---

## Verdict

**ACCEPT**

Goal1060 correctly compares accepted Goal1058 RTX A5000 artifacts against
existing same-semantics baselines, correctly classifies `facility_knn_assignment`
and `robot_collision_screening` as internal speedup candidates while maintaining
`public_wording_blocked` and sub-10 ms timing-floor warnings on both, and does
not authorize any public speedup wording anywhere in the script, output, or test.
