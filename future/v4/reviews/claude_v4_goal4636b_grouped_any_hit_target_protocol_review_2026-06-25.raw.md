I have now read all specified files. Here is the critical review.

---

## V4 Goal4636B Grouped Any-Hit Target Protocol — Critical Review

### Q1: Is `ray_triangle_grouped_any_hit_flags_3d` generic or too robot-app-specific?

**It is generic at the native level, but with a structural gap.**

The native contract (`run_grouped_segment_any_hit_flags`, `run_native_prepared_grouped_segment_any_hit_flags`) takes generic arrays: `segment_start_xyz`, `segment_end_xyz`, `segment_group_offsets` — no robot vocabulary. The app-side lowering (pose × link × probe_points → generic segment groups) stays entirely in Python before the native call. The `native_forbidden_vocabulary` block in the benchmark app (`robot`, `link`, `pose`, `joint`, `kinematics`, `planner`, `collision`) is correctly enforced.

**However:** `RAY_TRIANGLE_GROUPED_ANY_HIT_FLAGS_3D` is not defined as a top-level generic function in `generic_primitives.py`. There is no `run_generic_ray_triangle_grouped_any_hit_flags_3d` analogous to `run_generic_ray_triangle_any_hit`. The primitive exists only as backend prepared-object methods. This is consistent with the `rtdl_native_prepared_runner` scope claim (not catalog), but it means the catalog promotion path requires a future generic front-door addition — which the protocol does not specify.

The `grouped_any_hit_flag_stream` continuation class is genuinely distinct from the existing `any_hit_flag` (per-ray) in the current partial `robot_collision` coverage row. The grouping step is a real new surface.

---

### Q2: Are the floors material enough?

**The traversal and tail-total floors (3.0x) are material. The wrapper floors are weak and structurally unenforced.**

**Material:**
- `tail_total_mean_embree_over_optix_floor >= 3.0` — hard to fake, directly measures RT traversal benefit net of kernel overhead
- `traversal_mean_embree_over_optix_floor >= 3.0` — measures the RT-core path only

**Weak but justified:**
- `wrapper_mean_embree_over_optix_floor >= 1.10` and `wrapper_min_embree_over_optix_floor >= 1.00` — justified by the explanation that the wrapper includes Python process and app lowering cost. Accepted provided the material claim is about the operator, not the app wall time.

**Critical structural gap:** The runner's `timed_status: pass` is determined by `all_timed_pairs_ok`, which checks contract/shape/signature/counts/probe-disabled. It does **not** check any of the four performance floors. The runner does compute `aggregate_ratios` and `all_wrapper_no_probe_pairs_above_1x` (strictly >1.0, not ≥1.00 as declared), but these are **output fields**, not `timed_status` determinants.

This means a run can produce `timed_status: pass` with a 1.5x traversal ratio (below the 3.0x floor) and still appear to pass the gate. The floors are declared but not structurally enforced by the runner. The reviewer must manually apply all four floors to `aggregate_ratios` after collection. This is consistent with Goal4636A practice (a floor failure was observed from output data, not enforced by runner status), but it needs to be explicitly required in the post-POD review protocol.

There is also a subtle discrepancy: the runner's `all_wrapper_no_probe_pairs_above_1x` uses strict `> 1.0` while the declared floor says `>= 1.00`. This is a minor inconsistency but inconsequential given the floors are reviewer-applied anyway.

---

### Q3: Is native prepared-runner scope acceptable?

**Yes, conditionally.**

`V4_GOAL4636B_SCOPE = ("rtdl_native_prepared_runner",)` is correctly distinct from catalog scope. `measured_catalog_promotion_authorized: bool = False` is structurally enforced. The test `test_target_is_not_catalog_promotion_before_pod_gate` confirms `V4_GOAL4636B_API_SURFACE` is absent from `V4_TIER2_OPERATOR_SURFACES`.

The condition is that the protocol must state a defined future mechanism for catalog promotion — a named goal or obligation. The current protocol says "any catalog promotion later resolves the same catalog-scope issue" without naming a goal. Without this, post-POD scope resolution is untracked.

---

### Q4: Is it correct that this step adds no measured catalog surface before POD?

**Yes, correctly enforced and verified.**

`measured_catalog_promotion_authorized: bool = False` is enforced at construction time via the dataclass. `validate_v4_goal4636_grouped_any_hit_target()` explicitly raises on this flag being True. The test independently confirms the operator is not in `V4_TIER2_OPERATOR_SURFACES`. This boundary is solid.

---

### Q5: May POD proceed?

**Yes, after amendments are accepted as evaluation criteria.**

---

## Required Amendments

**Amendment 1 (Required before POD evaluation — process gap):**
The protocol must explicitly state that `timed_status: pass` from the runner is a **correctness gate only** (contract/shape/signature/counts/probe-disabled). Post-POD review must manually verify ALL FOUR performance floors from `aggregate_ratios` in the JSON output before authorizing promotion. A floor failure (traversal or tail-total mean < 3.0x, wrapper mean < 1.10x, or wrapper min < 1.00x) is a gate failure regardless of `timed_status: pass`.

**Amendment 2 (Required before promotion — coverage label scope):**
If the gate passes, the promotion document must explicitly state that "strong measured operator coverage" for `robot_collision` applies to the **generic grouped any-hit flag stream continuation class** only — not to robot-collision wall time, robot-planning speedup, or whole-app acceleration. The coverage upgrade from partial → strong is an operator-level claim, not an app-level claim. The existing `release_gap` and `next_action` in `v4_coverage_audit.py` partially address this but the promotion document must not abbreviate it.

**Amendment 3 (Required in promotion document — catalog path):**
The post-POD promotion document must state that promotion under `rtdl_native_prepared_runner` scope does NOT authorize catalog surface addition and that future catalog promotion of `RAY_TRIANGLE_GROUPED_ANY_HIT_FLAGS_3D` requires a separately-named goal (with a new generic front-door function in `generic_primitives.py`).

**Observation (not a blocker — verify before using gate evidence):**
The traversal floor (3.0x) can only be evaluated if the backend consistently emits `"traversal"` as a key in `phase_timing_seconds`. In `_compare_pair`, the traversal ratio uses `.get("traversal")`, and `_series` silently produces `count: 0, mean: None` if traversal is absent — making the traversal floor vacuously non-evaluable. Confirm that both Embree and OptiX backends reliably emit the traversal phase before treating the traversal aggregate ratio as meaningful evidence.

---

## Non-Authorization Confirmation

This review does not authorize: V4 release, V4 release candidate, broad V4 speedup, whole robot-planning speedup, continuous collision support, exact solid-collision claims, all-benchmark speedup, measured catalog promotion before POD results, CuPy performance, Tier-3 support, public true-zero-copy, C ABI / embedding / non-Python host claims, or robot-collision-native or other app-specific kernels.

---

## Verdict

**`approve_with_required_amendments`**

The operator is genuinely generic at the native level. The continuation class is new. Non-authorization boundaries are structurally enforced and tested. The 3.0x traversal/tail-total floors are material. The native prepared-runner scope is correctly separated from catalog promotion.

Amendments 1–3 are required: the performance-floor enforcement gap must be stated as an explicit post-POD review obligation, the coverage label must be scoped to the operator (not the app), and the catalog resolution path must be named. The POD gate may be run once these amendments are accepted as binding evaluation criteria.
