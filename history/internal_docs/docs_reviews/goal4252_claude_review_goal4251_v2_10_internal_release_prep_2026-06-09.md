# Goal4252 Claude Review: Goal4251 v2.10 Internal Release-Prep Packet

Date: 2026-06-09
Verdict: **accept-with-boundary**
Reviewer: Claude (Sonnet 4.6)

---

## Scope

Independent read-only review of:

- `docs/reports/goal4251_v2_10_internal_release_prep_packet_2026-06-09.md`
- `docs/reports/goal4248_current_public_docs_claim_boundary_scan_2026-06-09.md`
- `docs/reports/goal4249_major_performance_target_map_after_public_docs_scan_2026-06-09.md`
- `docs/reports/goal4250_post_docs_scan_pod_validation_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`
- `tests/goal4251_v2_10_internal_release_prep_packet_test.py`
- `tests/goal4250_post_docs_scan_pod_validation_test.py`
- `tests/goal4248_current_public_docs_claim_boundary_scan_test.py`
- `tests/goal4219_major_performance_target_map_test.py`

---

## Q1: Does Goal4251 accurately summarize Goals4235, 4239, 4243, 4248, 4249, and 4250 without overstating release readiness?

**Finding: accurate, not overstated.**

Each goal is summarized correctly against the underlying report:

- **Goal4235** — "All ten current benchmark front doors pass on RTX 4000 Ada at clean source commit `72690687`." This matches the reading in Goal4249 and the target map.
- **Goal4239** — Described as a dedicated 20.76s RayJoin long-repeat profile within a contract-split route policy. Consistent with Goal4249 and the target map's `rayjoin_contract_split_route_policy` current reading.
- **Goal4243** — Listed as refreshing Hausdorff/contact/triangle short rows with dedicated long-repeat evidence. Consistent with the `ten_app_measurement_adequacy_closure` entry in the target map.
- **Goal4248** — "31 files, 116 claim-sensitive phrases, and 0 hard blockers." These exact figures appear in the Goal4248 report; the claim-boundary flags in the JSON artifact are all false. The four repairs (README.md ×2, examples/README.md, nearest_neighbor_workloads.md) are documented; the corresponding test (`test_initial_wording_blockers_stay_repaired`) verifies the repairs are still in place at the source tree.
- **Goal4249** — Described as folding Goal4248 into the release-grade and major-release rows without authorizing release. This matches the Goal4249 report, where `release_grade_long_run_packet` stays at `needs_broader_evidence` and `major_release_candidate_packet` stays at `pending_user_release_decision`.
- **Goal4250** — "22 tests OK" on RTX 4000 Ada at `14dbb8e0`. This matches the Goal4250 report exactly, including GPU, driver, and source commit.

The "Current Position" narrative ends with: "This is enough to say the internal evidence packet is coherent. It is not enough to press a release button by itself." The calibration is correct. No single line in the packet reads as a release authorization or public speedup claim.

One minor note: Goal4251 also credits Goal4245 in the "Evidence Closed" section for structurally blocking the `RTDL beats RayJoin` claim. Goal4245 does not appear in the packet's own "reviewer question 1" summary list (which names Goals4235, 4239, 4243, 4248, 4249, 4250), but it is present in the Evidence Closed table. This is not an inaccuracy — Goal4245 is ancillary to Goal4239 — but reviewers should be aware it is referenced beyond the primary chain listed in Q1.

---

## Q2: Are the blocked gates complete and correctly framed?

**Finding: substantially complete; one structural gap in the Still Blocked Or Deferred table.**

The "Still Blocked Or Deferred" table covers nine items: formal release packet, final public claim wording, fresh release consensus, AMD/HIPRT performance, broad RT-core speedup, whole-application acceleration, paper reproduction, true zero-copy, and automatic partner/backend selection. The framing for each is accurate:

- **Formal release packet** — correctly framed as requiring explicit user decision; this packet is not a release trigger.
- **AMD/HIPRT** — correctly tied to hardware availability, with no NVIDIA-to-AMD inference allowed.
- **Broad RT-core speedup** — correctly described as contract- and workload-scoped, not universal.
- **Whole-application acceleration** — correctly notes Python/partner continuation, data-prep, and validation phases outside the RT-heavy primitive.
- **Paper reproduction** — correctly distinguishes reconstruction instruments and route studies from full authors-code reproductions.
- **True zero-copy** — correctly scoped to residency and prepared-session evidence, not a general product guarantee.
- **Automatic partner/backend selection** — correctly held user-owned and explicit.

**The gap**: Two claim categories named in the handoff reviewer questions — **RayJoin superiority** and **package install** — do not appear as rows in the "Still Blocked Or Deferred" table. They are addressed, but only in the final Boundary paragraph ("RTDL-beats-RayJoin wording" and "package-install wording" are listed as not authorized there). This is not an evidence defect: the blocking is real and the Boundary paragraph is a recognized location for it. However, a reader scanning only the table would not find these two gates explicitly listed. Future release-prep packets should consider promoting these two items into the table as rows alongside the others.

This gap does not change the verdict because both items are covered somewhere in the document and the test suite verifies the relevant boundary strings are present in the text.

---

## Q3: Does Goal4251 preserve the principle that RTDL is a generic language/runtime with explicit user-chosen partners, not an app library or hidden dispatcher?

**Finding: yes, preserved at every layer.**

The packet states the principle twice — once in the reviewer question text ("RTDL is a generic language/runtime with explicit user-chosen partners, not an app library or hidden dispatcher") and once in the blocked-gates table ("Partner and backend choice stays explicit and user-owned"). The test `test_packet_keeps_user_chosen_partner_boundary` verifies all three of these phrases are present at test time.

The target map reinforces this at the code level. The `prepared_session_residency_surface` entry's `next_action` reads: "Keep reuse explicit and user-owned. Future work may improve front-door ergonomics, but must not enable hidden global caching or automatic backend/partner selection." The `__post_init__` guard on `CurrentMajorPerformanceTarget` raises `ValueError` if `automatic_partner_selection_authorized` is set to True, making any accidental flip a hard import failure rather than a silent drift.

No phrase in Goal4251 implies that RTDL selects partners, backends, or routes on behalf of the user.

---

## Q4: Does the target map remain structurally non-authorizing after Goal4249?

**Finding: yes, non-authorizing at every level.**

The module-level constant `CURRENT_MAJOR_PERFORMANCE_TARGET_STATUS = "internal_direction_map_not_release_authorization"` labels the map at import time. The `__post_init__` method raises `ValueError` for any of nine authorization flags if set True, which would crash the import. `summarize_current_major_performance_targets` hardcodes all nine flags to False in the summary dict. `validate_current_major_performance_targets` checks every row for the same nine flags and returns `status = "reject"` if any is True.

The test `test_no_target_authorizes_release_or_hidden_dispatch` iterates every row and asserts all nine flags are False. The test `test_target_map_validates_and_covers_required_statuses` confirms the validation returns `"accept"` with zero errors and that all five required status values are present (ensuring the map covers the full evidence-to-blocked range, not just the "done" entries).

Goal4249 added Goal4248 as an evidence reference to the `release_grade_long_run_packet` and `major_release_candidate_packet` rows. Both rows retain their non-authorizing statuses (`needs_broader_evidence` and `pending_user_release_decision` respectively), and the `release_grade_long_run_packet` current_reading explicitly states "This is still not a formal public release matrix." The Goal4249 report's own Boundary section is identical in scope to Goal4248's and Goal4250's. No authorization inflation occurred in the Goal4249 update.

---

## Q5: Assuming no AMD claim is made, what evidence or wording remains before a formal release packet can be assembled?

**Finding: no measurement gaps remain on NVIDIA; three process gates remain open.**

The current NVIDIA/OptiX evidence chain is coherent:
- All ten benchmark front doors pass at a clean commit.
- All ten have second-level (≥1s) timing evidence, with former short rows refreshed to dedicated long-repeat.
- RayJoin route policy is documented by contract, not collapsed into a single paper-reproduction number.
- RT-DBSCAN profile-aware route policy is explicit.
- Public learner/user docs pass a zero-hard-blocker scan after four wording repairs.
- The target map is structurally non-authorizing.

What remains before a formal release packet:

1. **Draft exact public release claim text.** The docs scan confirms the existing text is clean, but no release-specific claim text has been composed or reviewed. The exact wording of any public speedup, route-policy, or feature claims needs to be written and audited. This is distinct from the docs scan, which only checks the current text for hazards.

2. **Multi-AI consensus over the exact release packet.** The packet itself says this explicitly. This review (Goal4252) is over the prep packet, not the release packet. A separate consensus pass over the assembled release artifact is required before any public release action.

3. **Explicit user release decision.** The packet is framed as "pending explicit user decision." No automation or review verdict can substitute for this. The `major_release_candidate_packet` target status is `pending_user_release_decision`, and the `release_grade_long_run_packet` target status is `needs_broader_evidence` — the latter flagging that the current NVIDIA single-hardware evidence may not be sufficient for a public release matrix depending on the scope of the claims drafted in step 1.

There is one conditional: the `release_grade_long_run_packet` target has `pod_needed_next = True`. This implies the formal release packet will require a fresh pod validation pass against the exact release-packet artifact, not just the prep artifact at `14dbb8e0`.

No new measurement gaps are identified on the current NVIDIA surface. The three open items are process and governance gates, not evidence gaps.

---

## Summary

| Question | Finding |
| --- | --- |
| Q1: Accurate summary without overstating? | Yes. Each goal is summarized correctly. Release calibration is explicit. |
| Q2: Blocked gates complete and correctly framed? | Substantially yes. RayJoin superiority and package-install appear in Boundary paragraph only, not in the Still Blocked table. |
| Q3: RTDL generic language/runtime principle preserved? | Yes. Preserved in text, tests, and target-map code. |
| Q4: Target map structurally non-authorizing after Goal4249? | Yes. Enforced by ValueError guard, hardcoded False flags, validation function, and tests. |
| Q5: Remaining gaps before formal release packet? | No measurement gaps on NVIDIA. Three process gates remain: draft exact release claims, multi-AI consensus over those claims, explicit user release decision. |

**Verdict: accept-with-boundary**

The packet is accurate, correctly bounded, and structurally non-authorizing. The boundary is: the "Still Blocked Or Deferred" table omits explicit rows for RayJoin superiority and package-install claims; these are covered in the Boundary section but would be more discoverable as table rows. This does not affect correctness of the evidence or the blocking. Future release-prep packets should consolidate all blocked gates into the table.

---

## Boundary

This review does not authorize release, public speedup wording, whole-app acceleration wording, broad RT-core wording, RTDL-beats-RayJoin wording, paper-reproduction wording, package-install wording, true-zero-copy wording, automatic partner/backend selection, AMD/HIPRT performance wording, or app-specific native-engine logic.
