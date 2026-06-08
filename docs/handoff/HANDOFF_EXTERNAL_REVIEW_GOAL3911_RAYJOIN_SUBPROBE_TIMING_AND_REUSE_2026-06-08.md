# Handoff: External Review Goal3911 RayJoin Subprobe Timing And Reuse

Please perform an independent read-only review of the recent Goal3909/Goal3910 RayJoin benchmark-layer work.

## Context

Recent commits:

- `84cdc82e` Goal3909 add RayJoin subprobe phase timing
- `53379125` Goal3910 reuse loaded RayJoin cases in subprobe

Goal3908 showed the representative RayJoin wrapper was dominated by the combined LSI/overlay subprobe, while the RTDL/OptiX hot scalar-count routes were already fast. Goal3909 added nested per-case phase timing to `scripts/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py`. Goal3910 then changed the same script to load each CDB-derived case once and feed that loaded app input to both the Numba same-contract baseline and the RTDL/OptiX prepared route.

## Files To Inspect

- `scripts/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py`
- `tests/goal3909_rayjoin_lsi_overlay_subprobe_phase_timing_test.py`
- `tests/goal3910_rayjoin_lsi_overlay_shared_case_reuse_test.py`
- `docs/reports/goal3909_rayjoin_lsi_overlay_subprobe_phase_timing_2026-06-08.md`
- `docs/reports/goal3910_rayjoin_lsi_overlay_shared_loaded_case_reuse_2026-06-08.md`

Helpful context:

- `scripts/goal3866_rayjoin_representative_scale_profile.py`
- `docs/reports/goal3908_rayjoin_wrapper_phase_timing_a5000_2026-06-08.md`
- `tests/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline_test.py`

## Review Questions

1. Does Goal3909 expose useful, machine-checkable nested timing without changing benchmark semantics?
2. Does Goal3910 keep the engine app-agnostic by limiting shared loaded-case reuse to Python/app benchmark orchestration?
3. Does the loaded-case path preserve same-contract count validation between Numba and RTDL/OptiX?
4. Are the payload/report boundaries honest, especially no release, whole-app speedup, RayJoin reproduction, broad RT-core, or true-zero-copy claim?
5. Are there any correctness, lifecycle, resource-close, or artifact-shape risks before the next A5000 pod timing run?

## Required Output

Write a review to:

`docs/reviews/goal3911_external_review_goal3909_3910_rayjoin_subprobe_timing_reuse_2026-06-08.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`. Keep it read-only except for the review file. If tests are run, report the exact command and result. If tests are not run, say so explicitly.
