# Goal3379: Claude Review — Owner-Face All-Point Priority Negative Probe (Goal3378)

Date: 2026-06-04

**Verdict: accept**

This is an independent Claude review of Goal3378 (commits `75876b18`, `a494b68b`). It is distinct from the Codex implementation and from the prior Claude review of Goal3376/Goal3377 (`docs/reviews/goal3377_claude_review_live_optix_candidate_owner_face_route_probe_2026-06-04.md`).

---

## Review Question Responses

### 1. Does Goal3378 honestly test and reject the `incident_chain_length_rank` policy rather than trying to promote it?

**Yes. The probe is structurally and linguistically committed to rejection.**

The script names the probe explicitly:

- `"policy_under_test": "incident_chain_length_rank"` — records what is being tested.
- `"policy_result": "reject_for_default_route"` — records the outcome, not conditionally.

The docstring on `_build_incident_chain_length_priority_columns()` opens with "Build a deliberately experimental all-point rank signal" and closes with "Goal3378 is a negative probe: this generic-looking signal is not sufficient for route-scale correctness on the county slice." This framing appears in the function body, not only in prose documentation, so it is legible to reviewers reading the code without the report.

The `interpretation` field in the JSON repeats the rejection: "a generic incident-chain-length priority removes extras but drops true exact rows, so it must not be promoted as a default owner-face route policy."

The report's second line states: "The policy must be rejected for default route use." There is no hedging language, no "pending further investigation" qualifier. The test `test_report_and_script_keep_negative_boundary_visible` asserts this phrasing appears verbatim in the report and asserts `reject_for_default_route` and `incident_chain_length_rank` appear verbatim in the script. This creates a durable guard against prose softening in future edits.

### 2. Does the artifact support the conclusion: exact 1417, live candidates 1429, filtered 1007, missing 410, extras 0, `matches_exact: false`?

**Yes. All numbers are internally consistent and independently verifiable.**

From the JSON artifact:

| Field | Value |
| --- | ---: |
| `exact_row_count` | 1417 |
| `optix_candidate_row_count` | 1429 |
| `filtered_row_count` | 1007 |
| `missing_exact_row_count` | 410 |
| `extra_row_count` | 0 |
| `matches_exact` | false |

Arithmetic check: `filtered = exact − missing + extras` → `1007 = 1417 − 410 + 0`. This holds exactly. The policy is over-restrictive: it removes all extras (correct) but also removes 410 true exact rows (incorrect). Zero extras with 410 missing is a coherent, unambiguous failure mode — the policy is monotonically too aggressive, not wrong in both directions simultaneously.

The `missing_sample` list contains 20 entries beginning with `[260, 260]`, which the test pins exactly (`self.assertEqual(data["missing_sample"][0], [260, 260])`). The report mentions this pair by name as the first missing sample.

One relationship worth noting: `incident_row_count` (1507) and `priority_row_count` (1507) are equal because `rt.derive_owner_face_priority_columns_from_rank_signals` emits one priority row per incident row. The candidate count (1429) is OptiX-derived and measures a different scope — the generic `(point_id, shape_id)` pairs the traversal produces — so the difference from 1507 is expected and not a discrepancy.

The provenance fields pin execution to commit `75876b18c45fe3c22edaa616198b2e35f4ceefb4` (the add-script commit), GPU `NVIDIA RTX A5000, 580.126.09`, and CuPy `14.1.1`. These match the values recorded in Goal3376's artifact, confirming the same pod and environment.

### 3. Does the script keep the priority policy in caller/Python logic and avoid adding app-specific native engine behavior?

**Yes. The separation is maintained throughout.**

`_build_incident_chain_length_priority_columns()` runs entirely in Python:

1. Builds `chains_by_coordinate` by iterating `county.chains` in Python.
2. Computes `rank_short_chain_count`, `rank_negative_min_chain_length`, and `rank_face_id` in Python lists.
3. Calls `rt.derive_owner_face_priority_columns_from_rank_signals()` — an `rt.*` app-layer entry point.

The OptiX path (`prepare_point_closed_shape_membership_2d_optix`, `candidate_device_columns`) produces only a generic `(point_id, shape_id)` stream. The owner-face logic, rank signals, and topology lookups are never passed into or derived by the native engine.

`rt.run_closed_shape_owner_face_priority_membership_pipeline_cupy()` is the CuPy-layer filter. It is called with CuPy arrays assembled in Python. No RT-core dispatch is introduced.

The `finally` block at lines 200–203 correctly closes `candidate_columns` and `prepared` even on exception, consistent with the resource management pattern established in Goal3376.

### 4. Are report/test boundaries safe?

**Yes. All seven claim-boundary flags are false, and all prohibitions are reiterated in test, code, and prose.**

The JSON `claim_boundary` object:

```json
{
  "native_default_route_authorized": false,
  "public_speedup_claim_authorized": false,
  "rayjoin_paper_reproduction_claim_authorized": false,
  "release_authorized": false,
  "rt_core_speedup_claim_authorized": false,
  "rtdl_beats_rayjoin_claim_authorized": false,
  "true_zero_copy_claim_authorized": false
}
```

The test asserts `self.assertFalse(any(data["claim_boundary"].values()))`. The report's "Boundary" section lists all seven prohibitions in prose. No speedup time is highlighted as a comparative claim. No partial-match fraction is cited as a correctness claim.

One observation: the report's "Why This Matters" section references Goal3376 evidence ("the live candidate stream is real; the owner-face continuation is useful for known boundary ambiguity") as established context. This backward reference is accurate and appropriate — it correctly situates Goal3378 as a scope-extension probe on top of the confirmed Goal3376 result, not a re-test of Goal3376 correctness.

### 5. Is the proposed next direction reasonable?

**Yes. The three proposed paths are each narrower and more principled than the rejected all-point approach.**

The report proposes:

1. **Selective ambiguity-set filtering** — only points requiring owner-face reconciliation are filtered.
2. **Stronger generic boundary-topology policy** — a policy that preserves non-ambiguous true positives.
3. **Route-level validated fallback** — uses live candidate columns plus exact rows only when the policy can prove correctness.

All three are well-scoped responses to the observed failure mode (410 missing true positives). The failure established in Goal3378 provides the specific evidence needed to justify this narrowing: the policy works correctly for known boundary-ambiguous points (it produces zero extras) but is over-applied when extended to all points. The implication that "selective ambiguity detection" is the right abstraction follows directly from this failure profile.

This is a meaningful engineering conclusion, not a holding statement. The three options share the common shape of "apply the policy only where it is warranted" rather than "try a different all-point heuristic," which is the correct lesson to draw.

---

## Additional Observations

**Two-commit structure is consistent.** Commit `75876b18` adds the script; commit `a494b68b` records the artifact/report/test. This matches the split used in Goal3376 (`ddc6962c` + `5d486542`) and is coherent for internal stepping-stone evidence.

**Test coverage is sufficient for this stage.** `test_artifact_rejects_all_point_priority_policy` pins 15 specific values plus the claim-boundary aggregate. `test_report_and_script_keep_negative_boundary_visible` guards boundary vocabulary in both prose and code. Together they prevent silent mutation of either the numbers or the framing.

**The relationship between Goal3376 and Goal3378 is correctly framed.** Goal3376 proved the live OptiX candidate stream works with the seven-point mask in place. Goal3378 proves the first natural generalization (remove the mask, apply a priority policy to all points) fails. This sequence is the correct experimental order. Attempting generalization and recording failure is good practice; it narrows the problem space for the next step rather than leaving it open-ended.

**No scope creep.** The script contains no benchmarking infrastructure, no throughput claims, no comparison against RayJoin or any other baseline. The only new capability it adds is the `_build_incident_chain_length_priority_columns()` function and the all-point invocation path. Everything else reuses existing `rt.*` entry points.

---

## Summary

Goal3378 is a well-constructed negative probe. It honestly tests whether `incident_chain_length_rank` can serve as a default all-point owner-face route policy, records a clear unambiguous failure (1417 exact, 1007 filtered, 410 missing, 0 extras, `matches_exact: false`), attributes the failure correctly (too aggressive, not directionally wrong), and draws the right engineering conclusion (selective rather than universal application). The priority logic lives entirely in Python/CuPy with no native engine modifications. All seven claim-boundary flags are false, and the prohibitions are enforced in code, test, and prose. The proposed next directions are each narrower and more principled than the rejected approach.

**Verdict: accept**

This internal evidence record is complete for the all-point priority negative probe stage. The clear next step is one of the three proposed selective approaches: ambiguity-set-based filtering, stronger boundary-topology policy, or route-level validated fallback.

---

*This is an independent Claude review. It does not authorize release, public performance claims, RayJoin paper reproduction, RTDL-beats-RayJoin, RT-core speedup, true-zero-copy, or native default-route claims.*
