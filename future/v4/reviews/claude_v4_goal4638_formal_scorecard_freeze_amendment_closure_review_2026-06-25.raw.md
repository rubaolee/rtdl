I have everything I need. Writing the verdict.

---

## Amendment Closure Review: V4 Goal4638 Formal Release Scorecard Freeze

**Date:** 2026-06-25
**Reviewer:** Claude (claude-sonnet-4-6)
**Scope:** Required amendment only — not a re-review of already-accepted findings

---

### Verdict

**`approve_goal4638_amendment_closed_continue_goal4639`**

No remaining amendments. One non-blocking observation.

---

### Review Question Findings

**Q1. Does the new floor table close the required amendment from the prior review?**

Yes, cleanly and on all three required axes.

The prior review required: (1) a Performance Floor Reference Table in the freeze markdown doc, (2) at minimum a Python dict in the freeze module, (3) for each of the 8 measured surfaces: a minimum numeric threshold and canonical source.

What was delivered:

- **Freeze doc** (lines 87–101): table exists, explicitly opens with *"Goal4639 pass/fail must use this table. The runner or reviewer must not choose a weaker floor from upstream evidence after seeing the new results."* — the V3 failure mode sentence is correctly embedded.
- **Python module** (`V4_GOAL4638_PERFORMANCE_FLOORS`, lines 36–93): tuple of 8 dicts, each with `floor_kind`, `minimum_floor`, `observed_anchor`, `canonical_source`. All 8 surfaces present, in measured-surface order.
- **Validator** (`validate_v4_goal4638_formal_scorecard_freeze`, lines 175–186): enforces count parity, order match, required keys, and `X.XX` placeholder exclusion. All four structural checks are present.
- **Tests** (`test_freeze_includes_one_numeric_performance_floor_per_surface`, lines 51–66): verifies 8 floors, no `X.XX`, canonical sources start with `future/v4/`, and spot-checks specific numeric strings (`>=1.20x`, `geomean >=1.50x`, `Embree/OptiX query median >=10.0x`, `device_array_to_route_d_rows_gap <=100.0`).
- **Doc test** (`test_freeze_doc_records_correction_and_forbidden_wording`, lines 78–90): asserts the markdown file contains "Performance Floor Reference Table", "Goal4639 pass/fail must use this table", `geomean \`>=1.50x\``, `query median \`264.822x\``, and "No geomean can include partial or deferred rows". All assertions match the actual doc content.

Required amendment: closed.

---

**Q2. Are any floor rows still vague enough to permit post-result reinterpretation?**

No row is fatally vague. Specific assessment per surface:

- `fixed_radius_count_threshold`: Uses ">=2 serious sizes" — this could invite wiggle, but the canonical source document names the frozen sizes explicitly, so reinterpretation requires departing from the named source. Acceptable.
- `closest_hit_grouped_argmin`: "all 3 frozen ray counts; ratio >=1.0x" — explicit count, numeric floor, no ambiguity.
- `any_hit_flags`: "8192-row torch fixture reference ratio >=1.0x; all 3 frozen ray counts must pass correctness and keep `host_materialization_in_hot_path: false`" — the floor applies to one size only; larger sizes are correctness-only. This is explicitly stated, not buried. Cannot be reinterpreted as a performance pass at sizes that don't carry a performance floor.
- `grouped_i64_reduction`: "all 6 frozen rows; ratio >=1.0x" — clear.
- `point_group_nearest_witness`: "repeat-gate and mixed6 rows; ratio >=1.0x at both serious sizes" — "both serious sizes" is bounded by the canonical source.
- `any_hit_weighted_sum`: "each frozen shape ratio >=1.20x and four-shape geomean >=1.50x" — two independent numeric constraints, both binding.
- `component_union`: three named ratio thresholds plus signature match — no interpretation space.
- `aabb_index`: count parity plus two explicit 10.0x thresholds — clear.

No vague row.

---

**Q3. Are the weak/limited surfaces bounded honestly rather than overclaimed?**

Yes, notably the `any_hit_flags` surface. The honest bounding is:

- Performance floor exists only at 8192 rows.
- 32768 and 131072 are correctness-only; the doc explicitly states "reference intentionally skipped by protocol" in the observed anchor column.
- The surface maps to `partial_operator_control` families (`robot_collision`), correctly blocked from contributing to release geomean.

This is the correct posture — a weak surface with limited evidence is stated as limited rather than padded with indirect claims. The prior review's concern about the V3 failure mode (a vague floor defined by reference allows a weaker result to be called "pass") is addressed: the floor for this surface is narrow on purpose, and the narrowness is documented, not obscured.

---

**Q4. Is Goal4639 now allowed to start under the rule that any missing reviewer seat must be recorded as review debt?**

Yes. The conditions are met:

- This review constitutes the Claude reviewer seat for Goal4638.
- The amendment is closed; no further action is required before Goal4639 starts.
- Antigravity's absence must be recorded as explicit review debt for Goal4638 (joining the existing debt for Goals 4633, 4635, 4637) before Goal4639 outputs any release-candidate wording. Goal4639 may run; it may not exit to release-candidate without that debt resolved or explicitly re-affirmed as acceptable accumulation.

---

### Non-Blocking Observation

**Weighted-sum geomean margin is tight.** The `any_hit_weighted_sum` floor requires a four-shape geomean of >=1.50x. The observed anchor is 1.5457x — approximately 3% above floor. Normal run-to-run GPU timing variation on a POD setup is typically 1–5%. Goal4639 should expect this surface to be the most likely to require a rerun call if an initial run comes in just below 1.50x. The threshold itself is appropriate and correctly set from the Goal4633 evidence; this is a heads-up for the runner, not a defect in the freeze.

---

### Summary

The Performance Floor Reference Table closes the one required amendment from the prior review. The table is self-contained, numeric, and non-reinterpretable. All 8 surfaces carry explicit floors with canonical sources. Tests verify both the module content and the doc content against specific numeric strings. 10 tests pass, 154 full-sweep tests pass. The freeze document is now sufficient for an independent Goal4639 reviewer to assess pass/fail without chasing upstream evidence.

**`approve_goal4638_amendment_closed_continue_goal4639`**
