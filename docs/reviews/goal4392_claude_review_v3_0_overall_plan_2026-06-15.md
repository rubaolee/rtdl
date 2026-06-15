# Goal4392 Claude Review: V3.0 Overall Plan

Date: 2026-06-15

Reviewer: Claude (independent)

Reviewed artifact: `docs/reports/goal4392_v3_0_overall_plan_2026-06-15.md`

Prior binding context: Goal4384 preflight consensus, Goal4384 preflight gate, Goal4385 v2.14 closeout instructions, Goal4387 M1 design-only unlock, Goal4391 doc cleanup consensus.

---

VERDICT: ACCEPT_WITH_NOTES

---

## Top Findings

### Finding 1 — All six Goal4384 binding conditions are carried forward correctly

The plan's Binding Preconditions section reproduces the six conditions from the Goal4384 preflight consensus verbatim, with one correctly described update: condition 1 (v2.14 closeout) is noted as satisfied by Goal4387, so M1 design may now begin. The remaining five implementation and claim gates continue to apply. This is accurate and consistent with Goal4387.

### Finding 2 — App-agnostic native engine rule is preserved and enforced concretely

The Architecture Thesis section restates the core RTDL rule. The Public API Boundary section gives explicit allowed and forbidden concept lists. The forbidden list covers app-specific public Python API names, app-specific native ABI names, and named native engine types (RayJoin, DBSCAN, Barnes-Hut, contact-manifold). These prohibitions are consistent with Goal4384 and Goal4387 and are specific enough to be testable.

### Finding 3 — Implementation is blocked until M1 is frozen and reviewed

The milestone table's M1 exit condition requires a frozen design document and static tests before M2 may begin. The Immediate Next Actions section makes external review of M1 a named prerequisite before implementation is unblocked. The Final Gate confirms the current state is `v3_0_overall_plan_accepted_m1_design_only_implementation_blocked`. This structure correctly prevents M2 from opening without an external pass on M1.

### Finding 4 — RTDBSCAN cross-app reuse requirement is preserved

The Benchmark-App Targets table entry for RTDBSCAN states: "Must prove one fused continuation primitive is reused by at least one non-DBSCAN workload." The M4 exit condition adds: "Same primitive reused without DBSCAN-specific names or semantics." This satisfies Goal4384 condition 4 and is specific enough to block a DBSCAN-only fused continuation from satisfying M4.

### Finding 5 — Hardware-observable evidence requirement is present and specific

The Partner Policy and the Binding Preconditions both prohibit same-stream, device-resident, and zero-copy wording without hardware-observable evidence. The Partner Policy specifies: CUDA events or Nsight-level evidence for same-stream claims; pointer identity, residency, lifetime, and transfer evidence for device-resident or zero-copy claims. This is consistent with Goal4384 condition 5 and Goal4387.

### Finding 6 — Public V3.0 performance claims are blocked until M7

The plan says "Public V3.0 performance claims may not proceed until M7." M7 is the Release-grade benchmark harness milestone with external review as its exit condition. The Claims That Are Not Allowed Yet section lists six specific prohibited claim types. The preflight gate blocked claims until M5 of its numbering scheme; that M5 was the release-grade harness equivalent. The renumbering from M5 to M7 reflects the addition of M2 (planner skeleton) and M3 (residency and phase instrumentation) as explicit milestones. The functional requirement is preserved.

### Finding 7 — Milestone order and exit conditions are credible

M1 (IR design) must be frozen before M2 (planner skeleton). M3 (residency and phase instrumentation, with CUDA-event and Nsight evidence required) is placed before the pilots (M4–M6), ensuring the measurement infrastructure exists before pilot performance evidence is gathered. M7 (release-grade harness) gates all public claims. The sequencing is sound.

### Finding 8 — Design questions for M1 are concrete and sufficient

The ten M1 design questions cover graph schema, residency annotations, stream representation, lifetime checking, mandatory phase markers, partner-node value exchange, OptiX lowering, Embree lowering parity, API name forbidding, and same-stream/device-resident/zero-copy evidence standards. This is enough specificity to guide an execution-graph IR design document.

---

## Required Changes

None. No finding rises to the level that blocks M0 acceptance.

---

## Notes (Non-Blocking)

### Note 1 — "when feasible" qualifier on Numba reference is slightly weaker than Goal4387

The Partner Policy says: "also test a Numba reference when feasible, because it is the no-C++/CUDA user path."

Goal4387 states, without qualification: "partner-dependent benchmark plans name both the best-performance partner and Numba reference."

The "when feasible" qualifier introduces room for judgment that Goal4387 did not provide. In practice, Numba is a reasonable fallback for every GPU continuation workload in the current benchmark set, so the qualifier is unlikely to be abused. However, the M1 IR design document should make the expectation concrete: Numba reference is the default; omitting it requires a documented justification (for example, a workload where no Numba continuation path exists at the time of the pilot).

Recommendation: tighten the wording in the M1 IR design document to match Goal4387's unqualified requirement, or add a sentence here such as: "Omitting the Numba reference requires a written justification in the pilot document explaining why no Numba continuation path exists for that workload."

### Note 2 — M4 exit condition does not explicitly mention same-contract pod-run evidence

The M4 exit condition reads: "Same primitive reused without DBSCAN-specific names or semantics; OptiX, Embree, best partner, and Numba reference policy satisfied."

It does not explicitly require that the same-contract OptiX/Embree comparison be run on hardware with OptiX/RT-core access (a pod run or equivalent). Phase accounting is covered by M3's exit condition, which M4 depends on, so the gap is partially filled by sequencing. However, the M4 exit condition could be strengthened by adding: "same-contract OptiX and Embree measurements taken on hardware with OptiX-capable GPU, with M3-grade phase accounting."

This note applies equally to M5 and M6. The Fairness Rules section covers this globally, but pilot exit conditions that name hardware requirements explicitly are harder to skip under review pressure.

### Note 3 — M1 external review requirement is in Immediate Next Actions but not in the milestone table

The milestone table's M1 exit condition does not mention external review. The Immediate Next Actions section says "prepare a new Claude/Gemini review packet for the M1 IR design" and "keep implementation blocked until that M1 review passes." The Final Gate says M1 must be "frozen and reviewed" before implementation.

The requirement is present but split across sections. Consider adding "passes external Claude/Gemini review" explicitly to the M1 row in the milestone table so the gate is self-contained.

---

## Optional Suggestions

1. The Benchmark-App Targets table could carry a "Partner policy" column that names the expected best-partner and whether Numba reference is expected, so the M1 design document inherits a concrete starting point.

2. The "Claims That Are Not Allowed Yet" section is strong. Consider adding: "V3.0 may not claim that RT cores always beat CUDA-core partners for any workload class until M7 provides a policy-selection table."

3. Consider explicitly naming the M0 exit condition as "this packet receives 3-AI acceptance and the consensus is recorded in a dated document" to match the convention used for M7.

---

## Final Recommendation

The Goal4392 V3.0 overall plan is sound. It correctly inherits all Goal4384 binding conditions, preserves the app-agnostic native engine rule, blocks implementation until M1 is frozen and externally reviewed, requires same-contract cross-app reuse from the RTDBSCAN pilot, requires hardware-observable evidence for same-stream and zero-copy claims, blocks public performance claims until M7, and provides concrete enough M1 design questions to begin IR design work. The notes above are improvements to carry into the M1 design document; none of them blocks acceptance of this plan as the V3.0 gate document.

VERDICT: ACCEPT_WITH_NOTES
