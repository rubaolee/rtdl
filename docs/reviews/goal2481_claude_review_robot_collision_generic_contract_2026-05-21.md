---

## Verdict: Approved

Goal2481 is a clean, minimal contract design. The primitive name, signature, semantics, output format, and boundary are all concretely stated. No blockers found.

---

## Blocking Issues

None.

---

## Non-Blocking Issues

**1. Invalid-segment enforcement location is unspecified.**
The semantics section says "Zero-length query segments are invalid for V1" but does not specify who enforces this — the Python packer, a native assertion, or silent undefined behavior. Given that degenerate triangles are explicitly pushed to the Python packer, the same sentence should appear for zero-length segments. Add one line to the contract: "Zero-length query segments must be rejected by the Python packer before native traversal."

**2. Float precision narrowing protocol is incomplete.**
The contract notes that `static_vertices_xyz` may be narrowed from float64 to float32 "if metadata records it," but `segment_start_xyz`/`segment_end_xyz` carry no equivalent note. If the backend narrows query coordinates independently, a precision mismatch between scene and query coordinates is possible. The Goal2482 3D probe-oracle fixture should include at least one test at full float64 input to surface this early.

**3. Test suite is intentionally red until this review and a consensus are written.**
`test_external_reviews_and_consensus_approve_goal2481` (line 79) requires `goal2481_claude_review_*.md` and a consensus document to exist. This is by design as a gate, but it should be noted: the test suite cannot pass until the review artifacts are committed. Goal2482 gates should include running this test green as a precondition.

---

## Contract Assessment

**1. Is Goal2481's contract concrete and minimal?**
Yes. `PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1` is precisely specified with two named entry points, a well-typed field table, explicit semantics for edge cases (empty groups, empty scenes, duplicate hits), and a clear non-goals list (bit-packed output, row witnesses, pair rows, per-segment rows, pose/link summaries). The contract name is intentionally generic and carries no robot vocabulary.

**2. Is 3D grouped finite segment/probe any-hit against a prepared triangle scene a defensible first native target?**
Yes. The rationale is strong on three counts. First, both Embree and OptiX are natively optimized for ray/segment traversal against BVH-accelerated triangle scenes; the contract fits the hardware exactly. Second, grouped segment probes are reusable across other workloads (swept samples, sensor beams, boundary probes, broad-phase screening), so the primitive pays for itself beyond robot collision. Third, and most importantly, the design correctly avoids the alternative — a native triangle-triangle solid-collision Boolean — which would force collision policy decisions into the native layer. The 2D→3D step is appropriately handled by requiring a 3D CPU probe-oracle fixture before any Embree parity claim, so the gap between Goal2480's 2D reference and the 3D native contract is explicitly bridged.

**3. Is byte-per-query-group uint8 output reasonable for V1?**
Yes. The tradeoff is correctly analyzed. `uint8` flags are directly consumable by NumPy, Torch, CuPy, and C ABI structs without unpacking, they are shape-stable across Embree, OptiX, and partner backends, and memory pressure from one byte per group is not material at the scales that matter before Goal2485. The design correctly defers bit-packing to only after performance evidence identifies flag bandwidth as a bottleneck. Row witnesses and pair rows are correctly rejected for V1 — they would pull in row-returning and `COLLECT_K_BOUNDED` semantics that belong to a different primitive family.

---

## Boundary Assessment

The app/native boundary is strictly enforced at three levels:

1. **Semantic boundary**: Python owns robot model construction, pose generation, transform matrices, group assignment, collision policy, and per-pose/per-link summaries. The native engine sees only triangles, segments, group offsets, and flags. This is cleanly separated with no leakage in either direction.

2. **Vocabulary enforcement**: Goal2481 broadens the previous ABI-prefix-only scan to a full-text regex scan of `src/native/embree` and `src/native/optix` for the forbidden word set (`robot`, `link`, `pose`, `joint`, `kinematic`, `kinematics`, `planner`, `collision`). The `FORBIDDEN_NATIVE_WORDS` regex in the test (line 22–25) matches the report's forbidden list exactly. Notably `collision` is now forbidden in native code, which is a tighter constraint than Goal2479 required — this is correct given that the native primitive uses `any_hit` and `intersection` vocabulary instead.

3. **Claim boundary**: The report explicitly blocks paper reproduction, authors'-code comparison, public speedup wording, exact solid-collision claims, and continuous/swept collision. The `native_robot_abi_added = false` and `native_collision_abi_added = false` sentinel pattern from Goal2480 carries forward.

One gap: the vocabulary scan does not cover `src/rtdsl/partner_adapters.py` and `src/rtdsl/optix_runtime.py`. This is correct — those are Python adapter files in the app layer and may legitimately use collision vocabulary. No issue here.

---

## Goal2482 Gate

The gates are explicit and actionable. Specifically:

- **3D CPU probe-oracle fixture** — required before any Embree parity claim, directly filling the 2D→3D gap from Goal2480. This is the right gate; without it, parity claims would rest on a mismatched reference.
- **Embree same-contract parity against that fixture** — not against the Goal2480 app, which is explicitly excluded as insufficient.
- **`uint8` compact flag output** — matches the contract exactly.
- **Phase timing with four named phases** (prepare/build, query packing/upload, traversal, output/postprocess) — sufficient for Goal2484/2485 performance separation.
- **Vocabulary tests passing** — must include `test_active_native_targets_remain_free_of_app_vocabulary`.

One addition worth making explicit in Goal2482's exit criteria: the `test_external_reviews_and_consensus_approve_goal2481` test must be green before Embree work begins, meaning this Claude review and a consensus document must be committed. That currently lives implicitly in the test file but is not stated in the Goal2481 or Goal2482 reports.

**Agreement with Gemini's approval: Yes.** Gemini's assessment is correct on all points. The contract is minimal, the native target is defensible, `uint8` is appropriate for V1, the boundary is strict, and the Goal2482 gates are unambiguous. The non-blocking issues above are refinements, not contradictions.
