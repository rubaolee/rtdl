`accept_with_required_amendments`

---

**Structural integrity: passes.** The dataclass guards, `__post_init__` authorization flag checks, and 4-test suite are tight. The `validate_v4_goal4627_coverage_audit` function enforces the exact 10-app order and singleton Goal4628 recommendation. No test passes by accident.

**Coverage labels: honest and conservative.** The 1/5/1/3 split (strong/partial/candidate/deferred) is internally consistent. The three deferred entries (`barnes_hut`, `spatial_rayjoin`, `librts_spatial_index`) are correctly held — their stated reasons (app-specific operator rejection, not-in-V4-Tier-2-surface) are sound. The non-authorization list is comprehensive and explicit.

**Triangle_counting classification: inconsistency in reasoning that requires amendment.** `triangle_counting.mapped_v4_operators` lists both `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` (candidate) and `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` (strongly measured, with serious POD evidence). The row is classified `candidate_not_measured_release_coverage`. That may be the correct decision — but the `release_gap` field only explains the weighted-sum candidate without stating why the presence of the measured grouped-i64 operator does not upgrade this row to `partial_measured_operator_coverage`. A future Goal4629 reviewer will need to know: does grouped-i64 cover triangle counting's primary any-hit counting continuation or only an adjacent reduction shape? The answer is load-bearing for Goal4629 scope, and it is currently absent from both the doc and the code.

**Goal4628 recommendation: correct.** Grouped-i64 satisfies all four stated criteria (non-fixed-radius, generic, serious POD evidence at two widths, prior external promotion review). Reconciliation over existing evidence is acceptable provided the review finds no same-contract or product-boundary gap.

**Fixed-radius prerequisite notation: adequate but passive.** The doc notes the constraint correctly. Goal4628 must state an explicit check; Goal4627 itself doesn't need to enforce it.

---

**Required amendment before Goal4627 can be marked complete:**

Add an explicit sentence to `triangle_counting`'s `release_gap` field (and mirror it in the audit doc table) explaining why `grouped_i64_reduction` being in `mapped_v4_operators` does not upgrade the row to `partial_measured` — specifically: that grouped-i64 covers the grouped reduction dimension but not the any-hit counting path that is triangle counting's dominant continuation shape, so the weighted-sum candidate remains the primary coverage route and determines the row's classification.
