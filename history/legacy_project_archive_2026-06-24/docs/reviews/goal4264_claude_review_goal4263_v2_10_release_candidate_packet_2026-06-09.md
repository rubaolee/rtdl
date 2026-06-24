# Goal4264 Claude Review: Goal4263 v2.10 Release-Candidate Packet

Date: 2026-06-09
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **accept-with-boundary**

---

## Scope

Independent read-only review of the v2.10 release-candidate packet draft after
claim-wording closure. Files reviewed:

Primary:
- `docs/reports/goal4257_v2_10_release_candidate_packet_draft_2026-06-09.md`
- `docs/reports/goal4261_major_performance_target_map_after_claim_wording_closure_2026-06-09.md`
- `docs/reports/goal4262_exact_head_release_prep_pod_validation_2026-06-09.md`
- `docs/reports/goal4254_v2_10_public_claim_wording_candidate_2026-06-09.md`
- `docs/reports/goal4258_public_claim_wording_repair_closure_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`

Supporting reviews:
- `docs/reviews/goal4252_claude_review_goal4251_v2_10_internal_release_prep_2026-06-09.md`
- `docs/reviews/goal4253_gemini_review_goal4251_v2_10_internal_release_prep_2026-06-09.md`
- `docs/reviews/goal4255_claude_review_goal4254_public_claim_wording_2026-06-09.md`
- `docs/reviews/goal4256_gemini_review_goal4254_public_claim_wording_2026-06-09.md`
- `docs/reviews/goal4259_claude_review_goal4258_claim_wording_repair_closure_2026-06-09.md`
- `docs/reviews/goal4260_gemini_review_goal4258_claim_wording_repair_closure_2026-06-09.md`

Tests:
- `tests/goal4257_v2_10_release_candidate_packet_draft_test.py`
- `tests/goal4219_major_performance_target_map_test.py`
- `tests/goal4262_exact_head_release_prep_pod_validation_test.py`
- `tests/goal4254_v2_10_public_claim_wording_candidate_test.py`
- `tests/goal4258_public_claim_wording_repair_closure_test.py`
- `tests/goal4248_current_public_docs_claim_boundary_scan_test.py`

This is a read-only review. It does not authorize release.

---

## Q1: Is the release-candidate packet now internally coherent after Goal4258-4262?

**Yes, with one editorial gap to note.**

The evidence chain from Goal4235 through Goal4262 is coherent and internally
consistent. The wording repair loop closed cleanly:

- Goal4255 (Claude) issued three required wording fixes (R1–R3) against Goal4254.
- Goal4258 records the closure of all three, with pod validation at commit
  `b24a561d` (14 tests, OK).
- Goal4259 (Claude) and Goal4260 (Gemini) independently verify all three fixes
  are present in Goal4254 and that no new overclaim or platform issue was
  introduced.
- Goal4261 refreshes the target map to version `goal4261.v1`, placing
  `release_grade_long_run_packet` at `needs_broader_evidence` and
  `major_release_candidate_packet` at `pending_user_release_decision`.
- Goal4262 runs 18 tests at source commit `3cbd7557` on RTX 4000 Ada, all
  passing, including the `goal4219` map test which asserts the `goal4261.v1`
  version string.

The Python dataclass in `current_major_performance_targets.py` structurally
enforces all nine authorization flags to `False` via `__post_init__`, making
any accidental authorization flip a hard import failure.

**Editorial gap:** Goal4257's "Included Evidence" table was written before
Goal4261 and Goal4262 existed. The table lists "Goal4249" as the "Current
target map" and does not cite Goal4261 (target-map refresh after wording
closure) or Goal4262 (exact-head pod validation). Both artifacts were produced
after the draft was written and post-date the current version string
`goal4261.v1`. The associated test `goal4257_v2_10_release_candidate_packet_draft_test.py`
checks that Goal4235 through Goal4260 appear in the report but does not assert
Goal4261 or Goal4262.

This gap does not create a false claim and does not affect any authorization
flag, but a final release packet that cites Goal4249 as its canonical target
map will be referencing a superseded version. The gap should be closed before
final packet assembly.

---

## Q2: Does the packet preserve all blocked claims?

**Yes. All eleven blocked-claim categories are explicitly preserved.**

| Blocked-claim category | Location in packet |
| --- | --- |
| Release without user decision | Goal4257 Required Steps: "User release decision \| pending" |
| Public speedup | Goal4254 §"Claims That Must Not Be Made" #2; Goal4257 §Boundary |
| Whole-app acceleration | Goal4254 #4; Goal4257 §Excluded From This Release Packet |
| Broad RT-core | Goal4254 #3; Goal4257 §Excluded |
| RTDL-beats-RayJoin | Goal4254 #5; Goal4257 §Excluded; Goal4245 structurally blocking |
| Paper reproduction | Goal4254 #6; Goal4257 §Excluded |
| Package install | Goal4254 #1; Goal4257 §Excluded |
| True zero-copy | Goal4254 #7; Goal4257 §Excluded |
| Automatic partner/backend selection | Goal4254 #8; Goal4257 §Excluded |
| AMD/HIPRT | Goal4254 #9; Goal4257 §Excluded; target map `blocked_pending_hardware` |
| App-specific native-engine logic | Goal4254 #10; Goal4257 §Excluded |

The dataclass `__post_init__` guard enforces the same nine flags at the Python
level and the test `test_no_target_authorizes_release_or_hidden_dispatch`
iterates every target row asserting all nine flags are `False`.

The Goal4254 Candidate Front-Page Paragraph also states all blocked categories
verbatim in a learner-visible negative list: "Do not read v2.10 as a
package-install promise, universal speedup promise, whole-app acceleration
promise, paper-reproduction claim, automatic partner-selection claim,
true-zero-copy product guarantee, or AMD/HIPRT performance claim."

No omissions found.

---

## Q3: Does the packet correctly state what remains?

**Yes.**

Goal4257 "Required Final Steps Before Release" table states:

| Step | Status |
| --- | --- |
| Final Claude review of Goal4254 wording | done-with-boundary |
| Focused repair-closure review | done |
| Final 3-AI release consensus over this exact packet | pending |
| User release decision | pending |
| Final pod validation at the exact release commit | pending |

The packet also explicitly notes: "Must include Codex plus two distinct
external AI systems, not Codex+Codex."

Goal4261 independently states: "Explicit user decision plus final consensus
still gate release." The target map `major_release_candidate_packet` next
action reads: "A formal major release needs explicit user release decision,
final pod validation at the release commit, and the required multi-AI consensus
over the exact release packet."

The AMD caveat is correctly segregated: `amd_hiprt_functional_parity` is
`blocked_pending_hardware` with `amd_hardware_needed=True`. No AMD claim is
made anywhere in the packet. The target map `next_action` reads: "When an AMD
pod is available, run HIPRT functional parity first, then only make performance
claims after same-contract AMD evidence exists."

---

## Q4: Assuming no AMD/package-install/universal-speedup/whole-app claim is made, is any additional NVIDIA/OptiX measurement needed before the user can decide?

**No additional measurement is needed.**

Goal4257 "Current Readiness" states: "The remaining work is governance and
exact packet validation, not a known NVIDIA measurement gap." This matches the
finding of Goal4252 (Claude review of Goal4251): "No measurement gaps are
identified on the current NVIDIA surface. The three open items are process and
governance gates, not evidence gaps."

Current NVIDIA/OptiX evidence covers:

- All ten benchmark front doors passing on RTX 4000 Ada at clean commit
  `72690687` (Goal4235).
- Second-level timing for all ten apps (Goal4230, Goal4243).
- Dedicated 20.76s RayJoin long-repeat profile within a contract-split route
  policy (Goal4239).
- Short-row refresh with current-head dedicated long-repeat evidence (Goal4243).
- Public-doc claim-boundary scan with 31 files, 116 claim-sensitive phrases,
  zero hard blockers (Goal4248).
- Exact-head pod validation of 18 release-prep tests at commit `3cbd7557`
  (Goal4262).

The `release_grade_long_run_packet` target has `pod_needed_next=True`, which
refers to a final pod validation pass against the final release commit, not a
new performance measurement campaign. Goal4262 provides this at the current
head. If the packet text is updated before release (e.g., to add Goal4261/4262
to the evidence table), a fresh pod run at the final commit would close that
step.

---

## Q5: What exact change, if any, must happen before this can become a final release packet?

Two items are required; three are process gates that remain open.

**Required (editorial) — Update Goal4257 evidence table and test to include Goal4261 and Goal4262:**

The packet's "Included Evidence" table currently cites Goal4249 as the
"Current target map." Goal4261 supersedes Goal4249 as the target map at
version `goal4261.v1`. Goal4262 is the exact-head pod validation that was run
after all wording repairs were applied. Before the packet becomes final, the
evidence table should be updated to add:

```
| Target map after claim-wording closure | Goal4261 |
| Exact-head release-prep pod validation | Goal4262 |
```

The test `goal4257_v2_10_release_candidate_packet_draft_test.py`
`test_packet_includes_current_evidence_chain` should be extended to assert
`Goal4261` and `Goal4262` appear in the report text.

This is the only editorial change identified. It is not an evidence gap and
does not affect any authorization flag, but a final release packet that
references Goal4249 as the canonical target map will be citing a superseded
source.

**Remaining process gates (all correctly listed as pending in Goal4257):**

1. Final 3-AI release consensus over the exact packet (this review is one of
   the required AI reviews; Goal4265 and user decision complete the set).
2. Explicit user release decision.
3. Final pod validation at the exact release commit after any final packet
   edits; Goal4262 covers commit `3cbd7557`, and should be rerun if the
   evidence table is updated.

---

## Summary

| Question | Finding |
| --- | --- |
| Q1: Internally coherent after Goal4258-4262? | Yes. One editorial gap: evidence table does not yet cite Goal4261 or Goal4262. |
| Q2: All blocked claims preserved? | Yes. All eleven categories are explicitly blocked in document text, in the front-page paragraph, and enforced by Python dataclass guards and tests. |
| Q3: Remaining steps correctly stated? | Yes. 3-AI consensus, user decision, and final pod validation are all listed as pending. AMD gating is correctly segregated. |
| Q4: Additional NVIDIA measurement needed? | No. Remaining work is governance and final pod validation, not evidence. |
| Q5: Required change before final packet? | One editorial update: add Goal4261 and Goal4262 to the Goal4257 evidence table and the associated test assertion. |

**Verdict: accept-with-boundary**

The packet is structurally sound, all blocked claims are preserved at every
layer (text, tests, Python enforcement), and no additional NVIDIA measurements
are needed under the stated claim scope. The boundary is: before this draft
becomes a final release packet, the evidence table in Goal4257 must be updated
to reference Goal4261 and Goal4262 (both post-date the current draft), and the
`test_packet_includes_current_evidence_chain` test must assert these two goals.
After that one editorial update and a fresh pod validation at the final commit,
the packet is ready for user release decision.

This review does not authorize release.

---

## Boundary

This review does not authorize release, public speedup wording, whole-app
acceleration wording, broad RT-core wording, RTDL-beats-RayJoin wording,
paper-reproduction wording, package-install wording, true-zero-copy wording,
automatic partner/backend selection, AMD/HIPRT performance wording, or
app-specific native-engine logic.
