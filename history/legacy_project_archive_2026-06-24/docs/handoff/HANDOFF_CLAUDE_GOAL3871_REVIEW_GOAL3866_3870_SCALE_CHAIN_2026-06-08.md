# Handoff: Claude Review Debt For Goal3866-3870 Scale Chain

Please perform a read-only external review of the RTDL Goal3866-3870 chain and
write the review to:

`docs/reviews/goal3871_claude_review_goal3866_3870_representative_scale_and_barnes_reuse_2026-06-08.md`

## Scope

Review the latest committed chain on `main`:

- Goal3866: representative RayJoin public-CDB mixed route scale profile.
- Goal3867: full 10-app scale refresh after the representative RayJoin row.
- Goal3868: benchmark adequacy update citing the RayJoin representative row.
- Goal3869: Barnes-Hut resident output-column reuse in the no-RawKernel Numba
  exact-force path.
- Goal3870: current 10-app scale refresh after Barnes-Hut output reuse.

Primary artifacts and tests:

- `docs/reports/goal3866_rayjoin_representative_scale_profile_2026-06-08.md`
- `docs/reports/goal3867_full_scale_after_rayjoin_representative_2026-06-08.md`
- `docs/reports/goal3869_barnes_hut_resident_output_reuse_2026-06-08.md`
- `docs/reports/goal3870_current_scale_after_barnes_reuse_2026-06-08.md`
- `docs/reports/goal3866_rayjoin_representative_scale_profile_a5000/`
- `docs/reports/goal3867_full_scale_after_rayjoin_representative_a5000/`
- `docs/reports/goal3869_barnes_hut_resident_output_reuse_a5000/`
- `docs/reports/goal3870_current_scale_after_barnes_reuse_a5000/`
- `tests/goal3866_rayjoin_representative_scale_profile_test.py`
- `tests/goal3867_full_scale_after_rayjoin_representative_test.py`
- `tests/goal3868_current_adequacy_after_rayjoin_representative_test.py`
- `tests/goal3869_barnes_hut_resident_output_reuse_test.py`
- `tests/goal3870_current_scale_after_barnes_reuse_test.py`

Relevant implementation files:

- `scripts/goal3866_rayjoin_representative_scale_profile.py`
- `scripts/goal3869_barnes_hut_resident_output_reuse_probe.py`
- `src/rtdsl/app_adapters/barnes_hut.py`
- `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `src/rtdsl/v2_9_benchmark_adequacy.py`

## Questions To Answer

1. Does Goal3866 provide a valid representative RayJoin mixed route without
   overclaiming paper reproduction, universal PIP dominance, or automatic
   dispatch?
2. Are the Goal3866 measured route choices honestly justified: Numba for
   one-shot PIP, RTDL/OptiX prepared batch executor for repeated PIP,
   RTDL/OptiX prepared segment-pair count for LSI, and RTDL/OptiX prepared
   shape-pair active count for overlay?
3. Does Goal3869 correctly improve Barnes-Hut resident repeated output reuse
   without embedding Barnes-Hut force logic in the native engine or requiring
   user RawKernel code?
4. Is the Goal3869 performance result properly bounded as a resident-repeat
   improvement, especially the `1.162x` Numba 8192-body reuse row and the
   still compute-dominated 16384-body row?
5. Does Goal3870 provide a clean current 10-app scale packet with `all_pass:
   true`, `json_pass_count: 10`, no claim-boundary violations, and source-clean
   nested RayJoin payload?
6. What remains open as the next non-minor performance target, especially for
   Barnes-Hut hierarchical/vector reduction work, cold-process-vs-resident
   benchmark interpretation, and future AMD/HIPRT validation?

## Review Rules

- This is read-only. Do not edit source files except for writing the review
  file above.
- Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
  `reject`.
- Lead with findings and risks. Be precise about evidence, artifact paths, and
  any inconsistencies.
- Do not authorize release, broad speedup claims, broad RT-core claims,
  zero-copy claims, automatic partner selection, RayJoin paper reproduction, or
  Barnes-Hut paper reproduction.
- If tests cannot run due to environment limits, say so explicitly and rely on
  static verification plus artifacts.
