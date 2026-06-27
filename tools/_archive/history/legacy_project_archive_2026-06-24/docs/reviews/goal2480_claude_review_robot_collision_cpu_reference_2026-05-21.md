---

## Verdict: Approved

---

## Blocking Issues

None.

---

## Non-Blocking Issues

1. **2D-only geometry** (Gemini's #1 — confirmed). The implementation is entirely 2D (`Point2`, `Triangle2`, 2D rotation transform). This is sufficient and correct for a CPU reference contract seed, but Goal2481 must make an explicit decision: whether the generic native contract will stay 2D, extend to 3D transformed triangles, or use a proxy primitive (swept sphere/capsule). That choice must be recorded in Goal2481's design report before Embree work starts in Goal2482.

2. **Paper citation tentative** (Gemini's #2 — confirmed). The anchor (`arXiv:2409.09918`, authors Sui/Sentis/Bylard, ICRA 2025 direction) is correctly marked tentative. The `official_code_verified = False` / `official_data_verified = False` flags are present. No action needed now, but Goal2481 or Goal2482 must re-verify before any external-facing wording.

3. **`continuous_collision_supported` not asserted in tests**. The `_claim_boundary()` returns this field as `False`, but `test_cli_emits_json_and_claim_boundary` does not assert it. The implementation has no continuous collision support, so this is not a safety gap, but the test should be tightened. Minor.

4. **Native vocabulary scan is ABI-prefix-only**. `test_no_native_robot_or_collision_abi_was_added` (line 112) only matches `rtdl_*(robot|collision)*` patterns — it would not catch a bare `robot` or `collision` comment/variable in native code. Goal2481's vocabulary enforcement test should broaden this sweep. Non-blocking here since no native files were modified.

---

## Correctness/Fixture Assessment

**Segment intersection** (`_segments_intersect`, lines 103–117): Uses signed-area orientation tests (cross products) with explicit collinear handling via `_point_on_segment`. The four collinear sub-cases are all checked before the strict-straddle test. The strict straddle at line 117 uses `> 0.0` (no epsilon) — this is correct because collinear endpoints are already exhausted by the epsilon checks above. Numerically sound for a deterministic reference.

**Point-in-triangle** (`_point_in_triangle`, lines 120–129): Tests all three signed areas against `±EPSILON`. Points with any signed area exactly zero (boundary) evaluate as inside (`not (has_negative and has_positive)` = `not False` = True), which is correct for any-hit semantics.

**Triangle-triangle intersection** (`triangles_intersect`, lines 132–143): Tests all nine edge-pair combinations, then checks containment in both directions. The two-direction containment correctly handles the case where one triangle is entirely inside the other with no edge crossings. Complete and correct.

**Transform** (`transformed_link_triangles`, lines 163–177): Applies a 2D rotation matrix `[cos θ, −sin θ; sin θ, cos θ]` to local link vertices, then translates by `(base_x, base_y)`. Correct for the stated `R·local + base` convention.

**Tiny fixture expected labels**: The five poses cover the required cases — clear left, single-link hit (forearm only), both-link hit, clear right, and rotated-forearm hit. The expected dict matches the compact flag vector `[0, 0, 0, 1, 1, 1, 0, 0, 0, 1]` and pose-level booleans `{1:F, 2:T, 3:T, 4:F, 5:T}` precisely. The `rotated_forearm_hits` case validates the transform path.

**Scaled fixture**: Deterministically parameterized via grid indexing (no RNG). `expected_link_flags=None` for scaled is acceptable since the tiny fixture exercises the correctness path.

---

## Claim Boundary

All four mandated claim gates are correctly blocked and programmatically enforced:

| Claim | Metadata flag | Test asserted |
|---|---|---|
| Paper reproduction | `paper_reproduction_claim_authorized = False` | Yes, `test_cli_emits_json_and_claim_boundary` |
| Authors-code comparison | `authors_code_comparison_claim_authorized = False` | Yes |
| Public speedup | `public_speedup_claim_authorized = False` | Yes |
| Continuous collision | `continuous_collision_supported = False` | Metadata only (see NB #3) |
| Native engine touched | `native_engine_touched = False` | Yes |

The `_paper_status()` block records `comparison_policy = "separate_scoping_goal_required_if_authors_code_or_data_becomes_available"`, consistent with the roadmap. The doc-string test (`test_docs_record_goal2480_scope_and_next_gate`) anchors the report text to these flags. All native forbidden vocabulary (`robot`, `link`, `pose`, `joint`, `kinematics`, `planner`, `collision`) is listed in `metadata.native_forbidden_vocabulary`, which is a useful forward contract for Goal2481.

The implementation contains zero imports from `rtdsl` despite having `sys.path` setup code, which is correct — the path setup is for source-tree consumer convenience, not an rtdsl dependency.

---

## Next Gate

**Proceed to Goal2481: Generic RTDL Contract Design.** The CPU reference provides a clean oracle and a stated output contract (`compact_link_flags`, pose-major, 0/1). Goal2481's mandatory decisions before Goal2482 starts:

1. **2D vs 3D** for the native contract — this is the most significant open question. If the native target is 3D OptiX/Embree, the CPU reference's 2D geometry is a sufficient correctness seed but not a direct parity oracle. Goal2481 must explicitly state this gap and whether a 3D CPU reference is needed before or during Goal2482.
2. **Compact output column format** — byte-per-query vs bit-packed vs typed partner/native column. Must align with existing RTDL buffer/tensor conventions, not robot-link convenience (as the roadmap states).
3. **Vocabulary enforcement test breadth** — Goal2481 should broaden the native scan beyond `rtdl_`-prefixed patterns.

No native Embree or OptiX work should begin until Goal2481's contract design is reviewed.
