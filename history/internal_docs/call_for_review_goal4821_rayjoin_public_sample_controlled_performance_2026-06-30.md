# Call For Review — Goal4821 RayJoin Public Sample Controlled Performance Smoke

Date: 2026-06-30

## Requested Verdict Labels

- `approve_goal4821_bounded_public_sample_performance_smoke`
- `approve_with_required_amendments`
- `fail_redo_goal4821`

## Files To Review

- `history/internal_docs/goal4821_rayjoin_public_sample_controlled_performance_2026-06-30.md`
- `history/internal_docs/goal4820_artifacts_2026-06-30/goal4821_perf_clean_compat_summary.json`
- `history/internal_docs/goal4820_artifacts_2026-06-30/goal4821_author_clean_compat.patch`
- `history/internal_docs/goal4820_core_directed_segment_point_location_sos_fix_2026-06-30.md`
- `history/internal_docs/antigravity_goal4820_core_directed_segment_point_location_and_overlay_midpoint_fix_review_2026-06-30.md`

## Summary

Goal4820 repaired correctness for the RayJoin author public sample. Goal4821
then ran a narrow performance smoke on the same input:

- author answer byte equality required for every run;
- author clean-compat binary: 3/3 byte-equal;
- repaired RTDL OptiX helper: 3/3 byte-equal;
- median wall:
  - author clean-compat: `7.702967159450054s`;
  - repaired RTDL OptiX: `4.510876469314098s`;
  - bounded ratio: `1.7076431181058986x`.

The claim is intentionally narrow:

- County x Soil public sample only;
- no eight-pair Section 5.7 claim;
- no broad RTDL performance claim;
- author binary is clean-compat because pristine author build failed under the
  current CUDA 12.8 / GCC 13 environment.

## Review Questions

1. Is it acceptable to use the author clean-compat binary for this bounded smoke,
   given that the compatibility patch only disables NVTX markers and adds
   `double2` hash/equality support, without changing author algorithm logic?

2. Does the artifact prove both routes produced byte-identical output to the
   author answer on every run?

3. Is the reported `1.7076431181058986x` ratio properly bounded to this public
   County x Soil sample?

4. Does the document avoid overclaiming full Section 5.7, eight-pair, or broad
   RTDL performance?

5. Should the next goal expand to additional Section 5.7 pairs only if exact
   author inputs and answer files are available?

6. If exact additional inputs/answers are not available, should the line close
   at bounded public-sample reproduction plus documented input gap?

## Non-Authorization

This review does not authorize:

- full RayJoin Section 5.7 paper reproduction claims;
- broad RTDL speedup claims;
- Embree work;
- V3/V4 public release resurrection;
- app-specific hidden native kernels.
