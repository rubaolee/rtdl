# Goal1006 External Review — Claude (claude-sonnet-4-6)

Date: 2026-04-26
Reviewer: Claude (claude-sonnet-4-6), independent external review
Artifacts reviewed: script, tests, JSON report, markdown report, Goal1005 source audit

---

## Verdict: ACCEPT

The gate is correctly implemented, conservatively calibrated, and internally consistent with the Goal1005 source data. No public speedup claims are authorized. The single public-review-ready row is correctly identified and its wording is appropriately bounded.

---

## Finding 1 — 100 ms floor is justified and correctly applied

**Status: PASS**

`MIN_PHASE_SEC_FOR_PUBLIC_SPEEDUP = 0.10` (100 ms) is a defensible threshold. Sub-10 ms RTX phases are dominated by GPU launch latency, CUDA/OptiX driver overhead, and OS scheduling jitter. At that duration, a single scheduler hiccup can swing the baseline/RTX ratio by tens of percent, making the ratio non-reproducible without much larger workloads.

The most striking example is `robot_collision_screening / prepared_pose_flags`: RTX phase = 0.49 ms, ratio = 1179x. A 1179x speedup is physically implausible as a stable public claim at sub-millisecond resolution. The 100 ms floor is the correct mechanism to hold this row.

The `_classify` function applies the floor at line 40 with `phase < MIN_PHASE_SEC_FOR_PUBLIC_SPEEDUP`, correctly using strict less-than so a row at exactly 100 ms passes.

---

## Finding 2 — Only service_coverage_gaps / prepared_gap_summary qualifies; this is correct

**Status: PASS**

Cross-checked all 17 rows against the Goal1005 source audit.

**8 Goal1005 candidates, checked for both criteria:**

| App / Path | Phase (s) | Ratio | Phase ≥ 0.10? | Ratio ≥ 1.20? | Correct status |
|---|---:|---:|:---:|:---:|---|
| robot_collision_screening / prepared_pose_flags | 0.000493 | 1179.64 | NO | yes | held ✓ |
| outlier_detection / prepared_fixed_radius_density_summary | 0.005828 | 4.64 | NO | yes | held ✓ |
| dbscan_clustering / prepared_fixed_radius_core_flags | 0.003751 | 6.62 | NO | yes | held ✓ |
| **service_coverage_gaps / prepared_gap_summary** | **0.136545** | **1.6115** | **YES** | **YES** | **public_review_ready ✓** |
| facility_knn_assignment / coverage_threshold_prepared | 0.003131 | 22.81 | NO | yes | held ✓ |
| segment_polygon_hitcount / ...native_experimental | 0.003996 | 1.71 | NO | yes | held ✓ |
| segment_polygon_anyhit_rows / ...prepared_bounded_gate | 0.004701 | 3.03 | NO | yes | held ✓ |
| ann_candidate_search / candidate_threshold_prepared | 0.000755 | 4.86 | NO | yes | held ✓ |

**9 non-candidates (8 reject + 1 internal_only):** all correctly receive `not_public_speedup_candidate`.

The lone qualifying row passes both criteria independently and unambiguously: phase 137 ms > 100 ms, ratio 1.61x > 1.20x.

---

## Finding 3 — Allowed wording is bounded and does not contain whole-app claims

**Status: PASS**

The allowed wording for `service_coverage_gaps / prepared_gap_summary`:

> "On the recorded RTX A5000 run, the bounded `service_coverage_gaps / prepared_gap_summary` query phase was 1.61x faster than the fastest same-semantics non-OptiX baseline for the measured sub-path. This is not a whole-app speedup claim."

This wording satisfies all constraints:
- Anchors to a specific recorded run ("On the recorded RTX A5000 run")
- Names the specific app and path explicitly
- Scopes to "query phase" and "measured sub-path" — not the full application
- Compares against "fastest same-semantics non-OptiX baseline" — ratio is not cherry-picked
- Explicitly disclaims whole-app speedup in the final sentence

The wording template is generated in `_classify` using `row['app']` and `row['path_name']`, so it is mechanically tied to the specific row rather than being editable free text. The ratio formatting `{ratio:.2f}x` produces `1.61x` which is accurate (source value: 1.611541...).

The Goal1005 `non_claim` for this row ("not a whole-app service coverage speedup claim and not a nearest-clinic row-output claim") is consistent with what the wording omits.

---

## Finding 4 — Held and rejected rows are conservatively handled

**Status: PASS**

**7 held rows (`candidate_but_needs_larger_scale_repeat`):**
All are legitimate Goal1005 candidates with RTX phases ranging from 0.49 ms to 6.8 ms — well under the 100 ms floor. Their allowed wording text prohibits quoting a speedup and is not promotable to a public claim as written. The policy correctly identifies them as waiting for a larger-scale repeat that keeps the comparable RTX phase above 100 ms.

**9 rejected rows (`not_public_speedup_candidate`):**
These include rows where RTX is already slower than the fastest same-semantics non-OptiX baseline (`road_hazard_screening` ratio = 0.021x, `hausdorff_distance` ratio = 0.016x, `polygon_pair_overlap` ratio = 0.000146x) and one internal-only margin case (`event_hotspot_screening`, ratio = 1.01x). The rejection wording "Do not use as a public RTX speedup claim under current evidence" is unambiguous.

No rejected row carries wording that could be misread as a claim.

---

## Finding 5 — `public_speedup_claim_authorized` is hardcoded False; count is hardcoded 0

**Status: PASS (with minor observation)**

In `build_gate()`, every row has `"public_speedup_claim_authorized": False` hardcoded (line 88), and `"public_speedup_claim_authorized_count": 0` is hardcoded in the summary (line 103). These are not derived from the row data.

This is intentional by design: Goal1006 is a wording gate, not a claim-authorization gate. Hardcoding `False`/`0` makes the constraint machine-readable and prevents any future code path from accidentally setting `True` on a row without auditing the gate logic. The approach is correct.

Minor: if a future editor changed `_classify` to return `"public_speedup_claim_authorized": True` on some path, the summary count of 0 would be stale. This is a documentation risk, not a current correctness issue.

---

## Finding 6 — Classification logic check order

**Status: PASS (minor observation)**

In `_classify`, phase is checked before ratio (lines 40–56). A row that fails both criteria (phase < 100 ms AND ratio < 1.20) is labeled `candidate_but_needs_larger_scale_repeat`, not `candidate_but_margin_too_small`. This is semantically correct: you cannot reliably evaluate a ratio until the phase is large enough to be stable. The phase gate takes priority. No rows are misclassified as a result.

---

## Finding 7 — Test suite passes and covers the critical invariants

**Status: PASS**

All 3 tests pass (verified against live data):

```
test_cli_writes_json_and_markdown ... ok
test_gate_is_stricter_than_goal1005_candidates ... ok
test_only_service_coverage_is_public_review_ready_now ... ok
```

Tests are integration-level (call `build_gate()` against the real source JSON), which is the right design: they validate the gate's behavior on actual A5000 measurements rather than synthetic fixtures. The tests lock in the current count (1 public-review-ready, 0 authorized), the specific passing row, a specific held row, and a specific rejected row.

---

## Finding 8 — Boundary language is present and consistent throughout

**Status: PASS**

The `boundary` field is present in the JSON output, in the markdown "Boundary" section, and explicitly in the gate summary (`public_speedup_claim_authorized_count: 0`). The markdown footer reinforces:
- No row authorized for front-page wording by this gate alone
- Sub-100 ms rows intentionally held
- Whole-app speedups disallowed without further audit

This language correctly describes the two-stage process (Goal1006 → separate 2-AI public wording review).

---

## Summary of Findings

| # | Finding | Status |
|---|---|---|
| 1 | 100 ms floor is justified and correctly applied | PASS |
| 2 | Only service_coverage_gaps / prepared_gap_summary qualifies | PASS |
| 3 | Allowed wording is bounded; no whole-app claims | PASS |
| 4 | Held and rejected rows are conservatively handled | PASS |
| 5 | public_speedup_claim_authorized hardcoded False/0 | PASS (minor note) |
| 6 | Check order (phase before ratio) is semantically correct | PASS (minor note) |
| 7 | Test suite passes and covers critical invariants | PASS |
| 8 | Boundary language is consistent throughout | PASS |

**No blocking issues found. ACCEPT.**

This gate correctly identifies 1 of 17 rows as mature enough for a subsequent 2-AI public wording review, holds 7 legitimate candidates for larger-scale repeats, and rejects 9 rows. It does not authorize any public speedup claims. The wording available for external review is appropriately bounded to a specific measured query phase on a specific sub-path of a specific app on a specific recorded RTX A5000 run.
