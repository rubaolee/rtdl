The write was denied, so here is the full review as direct text output:

---

# Claude Independent Review: Goal4384 V3.0 Preflight Consensus Gate

Date: 2026-06-14

Reviewer: Claude (independent, acting on packet `docs/reports/goal4384_v3_0_preflight_3ai_consensus_gate_2026-06-14.md`)

**Verdict: `accept-with-boundary`**

This review does not authorize V3.0 implementation. It does not authorize public speedup claims, whole-app claims, paper-reproduction claims, automatic partner selection, true zero-copy or device-residency claims, or app-specific native engine semantics. Authorization to begin V3.0 implementation requires this gate to record three acceptable verdicts in the final consensus document, and requires v2.14 cleanup gates to be complete.

---

## Summary

The preflight packet is well-structured, honest about current limits, and imposes appropriate governance. The architecture boundary is sound and the non-goals list is specific enough to prevent the most dangerous scope creeps. However, five boundary conditions must be recorded before implementation begins. These are not grounds for rejection — they are clarifications that prevent the gate from being interpreted loosely at M1 or M2.

---

## Review by Question

### Q1: Is V2.X correctly treated as complete enough to freeze after v2.14 cleanup rather than continuing indefinite optimization inside V2.X?

**Yes, with one hard dependency.**

The packet's structural analysis is correct. The Goal4382 cross-audit shows that the remaining gaps — RayJoin overlay output assembly, RTDBSCAN device-side component continuation, Barnes-Hut force aggregation, contact broadphase-to-solver composition, partner state and CUDA graph replay as system-level concepts — are not local optimization targets. Fixing them one app at a time inside V2.X would produce exactly the app-specific native patches the non-goals forbid.

The RTNN lesson from Goal4381 reinforces this: the route from row-materializing Python aggregation to native aggregate plus same-stream CuPy was an architectural change, not a local optimization. The same pattern must be repeated for RTDBSCAN continuation, RayJoin fused point-location, and Barnes-Hut force sums, and doing all of them ad hoc inside V2.X is indistinguishable from starting V3.0 without the discipline.

The hard dependency: "complete enough to freeze" must mean v2.14 cleanup gates from Goal4382 and Goal4383 are actually resolved — promoted rows reach GREEN/GREEN/YELLOW or better, RED-dimension rows are removed from public wording, and the v2.14 release packet is published. Freezing V2.X before v2.14 completes would leave the corrected evidence unreleased. The packet implies this but does not state it as a hard pre-condition of the gate. **This must be explicit.**

### Q2: Does the proposed V3.0 architecture preserve the app-agnostic native engine rule?

**Yes, as written.**

The seven-point architecture uses generic vocabulary throughout: primitive graph planner, device-resident streams, fused generic continuations, partner runtime protocol, backend lowering, profiler-grade phase accounting, policy selection. No RayJoin, DBSCAN, Barnes-Hut, or contact terminology appears in the architecture definition. This is the right pattern.

The weakest link is item 3 ("fused generic continuations") in combination with the M2 RTDBSCAN pilot. "Component-style unions" and "frontier traversal" are described generically, but when M2 implements them concretely against RTDBSCAN's component-continuation workload, there is a real risk that the resulting primitives are generic in name but DBSCAN-shaped in practice. The exit condition for M2 must require a positive test: the fused continuation primitives must be demonstrably reusable by at least one other workload class (e.g., robot grouped-segment flags or Barnes-Hut frontier) without modification. A primitive that only passes DBSCAN tests at M2 exit is an app-specific primitive.

### Q3: Are the non-goals strong enough to prevent app-specific native rewrites?

**Mostly yes. One gap at the Python API level.**

The non-goals enumerate the specific engine names and claim types that are forbidden. "No native RayJoin engine," "no native DBSCAN engine," etc. are clear and enforceable at code review time. "No automatic public speedup claims" and "no true-zero-copy claim unless pointer/lifetime/stream evidence proves it" carry forward the strongest V2.X evidence standards.

The gap: the non-goals address app-specific vocabulary at the native engine level but not at the Python API level. In V2.X the pattern has been `PreparedEmbreeFixedRadiusNeighbors3D`, `PreparedEmbreeFixedRadiusCountThreshold3D` — generic names. V3.0 must maintain this at the Python API surface as well. A non-goal that blocks `NativeRayJoinEngine` at the C++ layer but permits `RayJoinPIPPlanBuilder` as a Python API class is not strong enough. **Add: no app-specific name in the Python public API surface, including wrapper classes, factory functions, and plan builder names.**

### Q4: Are RTDBSCAN and RayJoin the right first V3.0 pilots, or should the first pilot be a smaller generic graph primitive?

**The ordering is acceptable, but M1's exit condition is underspecified.**

M2 (RTDBSCAN) and M3 (RayJoin PIP/overlay) are sensible pilot choices: they expose real continuation and fused-path problems that cannot be solved by local optimization. They are representative, not cherry-picked.

The risk is that M1 ("execution graph IR") exits on "static tests validate graph contracts and no app-specific vocabulary" without a written IR specification document. A test suite validates an implementation; it does not prevent an underspecified IR from accumulating app-shaped assumptions during M2. **M1 must produce a frozen IR design document — not only test results — before M2 implementation begins.** The document should specify graph value types, residency annotations, phase boundary markers, and the invariant that no graph node type encodes app semantics.

If the IR is underspecified at M1, RTDBSCAN's component-continuation pilot at M2 will implicitly define the IR rather than validate it.

### Q5: Does the partner runtime plan correctly treat CuPy/Numba/Triton/Torch as explicit user/app continuations rather than hidden RTDL magic?

**Yes in principle. One measurement gap.**

Item 4 of the V3.0 architecture correctly makes partner continuations explicit, same-stream when possible, and measurable as part of the plan. This is consistent with the Goal4381 evidence where the same-stream CuPy path is separately flagged and its float32/boundary-delta properties are disclosed.

The gap: "same-stream when possible" is currently evaluated via application metadata (`same_stream_partner_consumer=True` in the JSON output), not via independent hardware verification. At V3.0, a same-stream partner claim must be backed by hardware-observable evidence — CUDA event insertion, Nsight stream correlation, or equivalent — before it can appear in a public phase accounting table. **V3.0 milestone exit conditions for M2 through M4 should require at least one partner stream claim to be verified with hardware-level evidence, not metadata flags alone.**

### Q6: What evidence must exist before V3.0 implementation begins?

The packet lists the 3-AI consensus gate and v2.14 work as prerequisites. Based on this review, the minimum evidence set should be:

1. **v2.14 release packet published.** All promoted rows GREEN/GREEN/YELLOW or better in the Goal4382 audit matrix. RED-dimension rows removed from public wording. v2.14 tag exists or the maintainer has explicitly decided the v2.13 governance path (bridge vs. superseded).
2. **Three acceptable verdicts recorded in the final consensus document.** This gate.
3. **M1 IR design document written and frozen.** Before any M2 code is written. At minimum: graph value types, residency model, phase boundary semantics, and the prohibition on app-specific node types.
4. **Non-goal extended to Python API surface.** Written explicitly into the scope document, not just the architecture description.
5. **M2 exit condition updated to require cross-app reuse test.** At least one non-DBSCAN workload must exercise M2's fused continuation primitives.

### Q7: What evidence must exist before any V3.0 public performance claim?

The packet answers this for V2.X (phase accounting, same-contract comparison, external review, row-scoped wording) but does not carry an equivalent forward to V3.0. The milestone sequence ends at M5 ("release-grade benchmark harness"), but M5's exit condition does not explicitly authorize public claims — it defines repeatability.

**Add an explicit rule:** No V3.0 public performance claim is authorized until M5 is complete and Claude and Gemini review the M5 benchmark harness packet. The same standards apply as for V2.X: row-scoped wording, named hardware, named backend, named partner, phase explanation, and an explicit caveat separating RTDL-vs-Embree from author-code-parity.

The "no true-zero-copy claim unless pointer/lifetime/stream evidence proves it" non-goal is correct and should be restated as a gate condition at each public-claim boundary, not only at V3.0 start.

---

## Findings Summary

| Finding | Severity | Required action |
| --- | --- | --- |
| v2.14 completion not stated as hard pre-condition of this gate | Must fix before V3.0 start | Add explicit: V3.0 implementation blocked until v2.14 release packet is published and cleanup gates are resolved |
| M1 exit condition requires only static tests, not an IR design document | Must fix before M1 exit | M1 must produce a frozen IR spec document; M2 may not begin without it |
| Python API surface not covered by non-goals | Must fix before M2 | Add non-goal: no app-specific name in Python public API surface (wrappers, factories, plan builder classes) |
| M2 exit condition does not require cross-app reuse test | Must fix before M2 exit | At least one non-DBSCAN workload must exercise M2 fused continuation primitives |
| Same-stream partner claims not required to have hardware-level evidence | Must fix before M2–M4 public claim | At least one same-stream partner claim per milestone must be verified via CUDA events or Nsight, not metadata flags |
| No explicit rule for when V3.0 public performance claims are authorized | Must fix before any V3.0 public claim | Add: claims blocked until M5 complete and external AI review accepts the harness packet |

---

## Boundary Declarations

This review explicitly does **not** authorize:

- V3.0 implementation start, pending resolution of findings 1–3 above and final consensus record.
- Any public performance claim for V3.0 work.
- Any claim that V3.0 achieves author-hot-compute parity. That target requires M5-complete evidence and external review.
- True zero-copy or device-residency claims without pointer/lifetime/stream proof.
- App-specific native engine semantics (RayJoin engine, DBSCAN engine, Barnes-Hut force engine, contact solver engine) at any layer.
- Automatic partner selection claims. Partner selection must remain explicit, named, and measurable.
- Any expansion of the v2.13 or v2.14 public wording beyond what the respective cleanup gates authorize.

Subject to the above findings being resolved and recorded in the final consensus document, this reviewer accepts the V3.0 scope boundary, architecture description, non-goals list, and milestone ordering as a sound preflight framework.
