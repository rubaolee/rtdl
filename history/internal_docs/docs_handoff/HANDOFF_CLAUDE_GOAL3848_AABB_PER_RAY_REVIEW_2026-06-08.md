# Handoff: Claude Review Goal3848 AABB Per-Ray Count Optimization

Please perform an independent read-only review of Goal3848 and save your review
to:

`docs/reviews/goal3849_claude_review_goal3848_aabb_per_ray_count_optimization_2026-06-08.md`

Scope:

- `docs/reports/goal3848_aabb_count_per_ray_device_accumulation_2026-06-08.md`
- `docs/reports/goal3848_aabb_per_ray_device_a5000/librts_131k_repeat10_per_ray_device_defaults.json`
- `docs/reports/goal3848_aabb_per_ray_device_a5000/librts_131k_repeat10_per_ray_device_defaults.stderr.txt`
- `docs/reports/goal3846_stress_probe_candidates_a5000/librts_131k_repeat10.json`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `tests/goal3848_aabb_count_per_ray_device_accumulation_test.py`

Review questions:

1. Does Goal3848 preserve exact `AABB_INDEX_QUERY_2D` counts versus the
   Goal3846 default-width baseline?
2. Is the new per-ray device-counter design generic and app-agnostic, with no
   LibRTS-specific native symbol or app logic in the engine?
3. Is row collection still protected by the old row-slot atomic path while
   count-only queries use the new intersection-program counter path?
4. Are the reported A5000 speedups (`0.646092751` to `0.563984715`, about
   `1.145x`) supported by the artifacts without overclaiming public release,
   paper reproduction, broad RT-core speedup, or whole-app acceleration?
5. Does the report clearly explain the earlier command mismatch
   (`0.005` README smoke widths versus Goal3846 default widths) without
   confusing the accepted evidence?

Expected verdict values: `accept`, `accept-with-boundary`, `needs-more-evidence`,
or `reject`.

Please lead with findings ordered by severity, then answer the review questions.
