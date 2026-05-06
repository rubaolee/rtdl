Here is my line-by-line analysis across all eight files.

---

## Question 1: Does the repo honestly state v1.5 is standalone for the supported Embree+OptiX surface but not yet native-engine app-agnostic internally?

### Docs layer

**README.md:8-18** — States "standalone Embree+OptiX language/runtime completion candidate for the supported v1.5 surface" and explicitly: "v1.5 is not yet app-agnostic inside the native engine implementation." Also listed in both the Scope section (line 37) and Disallowed Conclusions (line 57).

**release_statement.md:10-17** — The proposed release statement includes the exact dual claim: primitive layer is app-name-free, native engine implementation is not yet app-agnostic. Line 48 lists "that the native engine is app-agnostic internally or has app-free internals" under Must Not Claim.

**audit_report.md:21-25** — Repeats the distinction: app-name-free primitives exist, but "some native entry points remain workload-shaped compatibility/proof surfaces." Line 46 also disallows "claiming the native engine has app-free internals."

All three docs are consistent and non-contradictory. ✓

### Code layer

**v1_5_readiness.py:165-177** — Three dedicated constants:
- `V1_5_ENGINE_APP_AGNOSTIC_INTERNAL_STATUS = "not_yet_app_agnostic"`
- `V1_5_ENGINE_APP_AGNOSTIC_TARGET_STATUS = "target_for_v1_5_1_to_v2_0"`
- `V1_5_ENGINE_APP_KNOWLEDGE_BOUNDARIES` names four concrete remaining app-knowledge surfaces

The `claim_boundary` string (line 770–775) requires "native engine is not yet app-agnostic internally" and `validate_v1_5_standalone_release_gate()` (line 911–928) enforces all three constants and requires that phrase in the boundary. ✓

**v1_5_release_public_wording.py:24-52** — `V1_5_RELEASE_PUBLIC_WORDING_ALLOWED_STATEMENT` (line 24-30) says "no claim that the native engine is app-agnostic internally yet." Required phrase list (line 38) mandates "not yet app-agnostic" appear in the scanned docs. Forbidden phrases (lines 48-52) block "native engine is fully app-agnostic", "native engine has zero app knowledge", "engine has zero app knowledge." ✓

### Test layer

**goal1398:92-135** — `test_gate_preserves_app_agnostic_engine_boundary` exercises all three constants and the four `engine_app_knowledge_boundaries` entries individually.

**goal1398:19-23** — `claim_boundary` check verifies "native engine is not yet app-agnostic internally" is in the gate boundary string.

**goal1407:41-43** — `test_release_public_wording_preserves_gate_dependencies` checks "no new whole-app speedup claim" and "standalone Embree+OptiX" are in the allowed statement. ✓

All layers are mutually consistent and non-overclaiming on the app-agnostic boundary.

---

## Question 2: Is the RTX pod Embree-vs-OptiX explanation bounded and not overclaiming?

### v1.5 vs v1.0 per-backend sections (goal1410)

**Embree results (lines 44-63):** Most rows are "roughly equal." Two are labeled "v1.5 slower" (`road_hazard_screening` 0.620x, `polygon_pair_overlap_area_rows` 0.945x). The interpretation correctly says "broadly performance-neutral" with the two exceptions named. No speedup claim is made. ✓

**OptiX results (lines 66-82):** Four rows labeled "v1.5 faster" with ratios of 1.139x–1.589x. The interpretation qualifies these as "positive RTX pod movement … under the measured compact/prepared subpaths." No unqualified whole-app speedup claim is made. ✓

### Embree-vs-OptiX comparison table (lines 84-110)

Several ratios are very large: `ann_candidate_search` 12168x, `robot_collision_screening` 3516x, `barnes_hut_force_app` 1232x, `hausdorff_distance` 183x. These are arithmetically correct from the raw numbers provided. The interpretation paragraph (lines 102-110) explicitly:

1. Attributes Embree wins to "small, compact, or CPU-refinement-heavy profiles where avoiding GPU upload/download, CUDA launch latency, synchronization, and marshaling outweighs GPU RT traversal throughput."
2. Attributes large OptiX wins to "prepared decision-style" profiles where the work is compact enough and large enough to amortize fixed GPU overhead.
3. **Critically (lines 132-135):** "Several OptiX measurements are extremely small sub-millisecond prepared queries; those should not be used as headline speedup claims. Public wording must stay subpath-specific and should cite this artifact plus external review before release-facing speedup claims are made."

The large OptiX ratios are presented as raw measurement artifacts with an explicit warning against headline use. The report neither presents them as headline claims nor suppresses them. ✓

### Release interpretation (lines 125-135)

Three bounded claims: v1.5 is broadly performance-neutral on Embree, v1.5 improves several OptiX RTX subpaths at 1.139x–1.589x (the reasonable range, not the extreme ratios), and explicit warning that sub-millisecond prepared-query figures must not drive public speedup wording. ✓

---

## Issues Found

None requiring fixes. The following are confirmed as designed:

- Gemini review is still missing from `V1_5_INTERNAL_READINESS_ACCEPTED_EXTERNAL_REVIEW_PARTNERS` — this is correct. The internal readiness gate enforces `external_3_ai_consensus_ready: False`, so public claims cannot be made. The release-candidate status does not require completed 3-AI consensus, only the eventual public claims do.
- goal1410 is not in the evidence pointer list in release_statement.md — this is intentional; goal1410 is supplemental RTX pod evidence, not a core gate requirement. Core benchmark gates reference goal1406.
- The extreme Embree-vs-OptiX ratios (12168x, 3516x) are not suppressed in the table — correct, the data is presented honestly with an explicit caution against headline use.

---

**VERDICT: ACCEPT**
