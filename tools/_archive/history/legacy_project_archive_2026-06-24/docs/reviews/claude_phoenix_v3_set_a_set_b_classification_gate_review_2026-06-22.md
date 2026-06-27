## External Review: Phoenix V3 Set A / Set B Classification Gate

**Review date:** 2026-06-22
**Reviewer:** Claude (external AI, Sonnet 4.6)
**Verdict:** `approve_with_required_edits`

---

### Q1: Is the Set A / Set B classification defensible as mechanism-based preregistration?

Yes, with one caveat. The rationale for each app is genuinely mechanism-based:

- Set A rationales describe specific V3 architectural properties (prepared execution, continuation phases, residency effects, multi-phase stream behavior) that should compound across the named workloads.
- Set B rationales correctly describe bounded, single-phase workloads where overhead avoidance is the correct target rather than material speedup.

No app clearly belongs in the other set given the stated mechanisms. The classification reads as honest preregistration, not result-driven sorting.

The caveat: **barnes_hut has a 0.844x geomean**, a 15.6% regression on a Set A "architecture-bearing" app. This does not invalidate the classification—the classification is based on mechanism, not result—but it signals an active architectural problem, not merely a missed gain. The gate should treat sub-0.90x Set A app geomeans differently from "just below 1.05x." It currently does not. See Q6.

---

### Q2: Is it acceptable that AABB M2.1 counts as a focused material probe while Contact Manifold / LibRTS AABB rows remain Set B?

Yes, this is coherent and not contradictory.

The M2.1 probe answers: "Does the AABB primitive route perform well when measured in focused productized-path conditions?" Contact Manifold and LibRTS all-app rows answer: "Does V3 avoid adding overhead on whole-app workloads that happen to route through AABB?" These are distinct questions. The focused probe tests the primitive in isolation before spending pod money; the Set B rows test whole-app experience.

What is not acceptable is counting the M2.1 probe without verifying the probe artifact exists on disk. The focused count (1) is sourced from a field in the classification JSON, not derived from the referenced file paths. See Q6.

---

### Q3: Does the gate correctly prevent another full all-app pod run right now?

Yes. The `all_app_pod_spend_authorized` flag requires `focused_count >= required_focused_count` (currently 1 >= 2, false). This correctly blocks the full run regardless of scorecard state.

The gate also correctly shows that even if the precondition were met, Set A would fail badly: 1.013x geomean vs. 1.20x minimum, 1 of 5 required app wins. The two-layer block is structurally sound.

---

### Q4: Does the gate correctly keep release/public/broad V3-over-V2 claims false?

Yes. All three authorization booleans (`release_authorized`, `public_speedup_claim_authorized`, `broad_v3_faster_than_v2_claim_authorized`) are hardcoded `False` in `build_payload()`—they are not derived from scorecard state. This is the correct design. A passing scorecard should never auto-authorize public claims; that requires explicit human decision outside this gate. The gate is sound on this point.

---

### Q5: Is app_id-level classification strong enough, or must every future case_id be listed explicitly?

**This is a real integrity gap.** App_id-level classification with an unknown-app-id failing rule is adequate for controlling which apps appear, but it does not control what rows appear within a known app.

If a future run adds a new `case_id` under `barnes_hut` or `rtnn`—perhaps a trivial case, a calibration row, or a different problem size—it will silently inherit the Set A `architecture_bearing` classification and influence the geomean without ever being reviewed. The gate has no mechanism to catch this.

For this to be a sound measurement-control artifact for the next run, either:

- A whitelist of approved `case_id` values per app must be added to the classification JSON, with unknown case_ids failing the gate, OR
- The classification JSON must include an explicit `classification_unit_scope` field stating that new case_ids within a known app require out-of-band written approval before they are counted in the scorecard, with the gate checking a `case_id_whitelist_frozen` boolean.

The current design is not sufficient for a serious run.

---

### Q6: What changes are required before this gate becomes the controlling measurement-control artifact?

**Required edits (blocking):**

1. **Case_id whitelist or explicit freeze gate.** As described in Q5. App_id classification is necessary but not sufficient. The next full run must not be able to add new case_ids that silently inherit classification.

2. **Focused probe count must be verified from artifacts, not trusted from JSON.** The gate reads `focused_productized_material_probe_count` from the classification JSON. That field is editable. The gate should verify that each entry in `focused_productized_material_probes` has a corresponding file on disk (the `path` field is already there—use it). Without this, the precondition count is not independently verifiable.

3. **LibRTS regression requires resolution, not just identification.** `librts_embree_aabb_index` is at 0.869x—a 13.1% regression on a Set B "no added overhead" app. The gate correctly flags this as `set_b_rows_below_0_95x: 1` and blocks release. But the artifact treats identification as sufficient progress. It is not. A Set B control row at 0.869x means V3 is actively adding overhead on a workload that is supposed to be parity. This must be root-caused and addressed before the next full run is authorized, not just before release. The gate should require Set B regressions to be resolved or explicitly deferred with written rationale before `all_app_pod_spend_authorized` can become true.

4. **Sub-0.90x Set A app geomean should trigger a harder block.** Barnes_hut at 0.844x is not in the same category as rtnn at 1.003x or triangle_counting at 0.987x. Both miss the 1.05x bar, but one represents an active architectural regression. The gate should add a `set_a_severe_regressions` check (e.g., any Set A app geomean below 0.90x) and expose it as a named failing check, not have it silently fold into the geomean calculation.

**Non-blocking observations:**

- The 1.20x Set A geomean threshold is aspirational relative to current actuals (best app: hausdorff at 1.149x, most apps below 1.0x). This is fine as a gate threshold—it should be hard—but the classification JSON should include a written rationale for why 1.20x is the number, not just state it.
- The `goal_level_decision_audit.was_i_foolish` field is appropriate self-discipline, but it belongs in the prose documents, not in a machine-readable gate artifact. It cannot be checked or verified by the gate logic and adds noise to the JSON schema.

---

### Summary

The classification mechanism is sound and preregistered correctly. The gate correctly prevents the full pod run, correctly keeps all public claims false, and the AABB M2.1 / Set B distinction is coherent. The scorecard is honest: Set A is failing badly (1.013x geomean, 1 of 5 required app wins, one 0.844x regression).

Required before this becomes the controlling artifact: case_id whitelist, artifact-verified probe count, Set B regression must gate `all_app_pod_spend_authorized`, and a harder block for sub-0.90x Set A app geomeans.

**Verdict: `approve_with_required_edits`**
