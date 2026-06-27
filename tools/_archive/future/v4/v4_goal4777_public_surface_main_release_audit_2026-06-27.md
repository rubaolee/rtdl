# Goal4777 - V4.0.0 Main Release Public-Surface Audit

Date: 2026-06-27

Status: `public_v4_0_0_surface_aligned_with_published_tag__external_review_requested`

## Purpose

V4.0.0 is a main RTDL release, not only a development checkpoint. After the
bounded public `v4.0.0` tag was created and pushed, the user-facing surface had
to stop saying "release candidate" or "tag target ready" in current docs and
examples.

Goal4777 updates the current public surface to say the exact published release
truth:

```text
V4.0.0 published, complete 10-app RT-core matrix, external public-tag review
approved under bounded framing, clean wheel smoke passed.
```

The same update keeps all performance and future-work boundaries locked.

## Files Audited

Current public user path:

- `README.md`
- `docs/README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/public_documentation_map.md`
- `docs/learn/performance_wording.md`
- `docs/learn/source_tree_doctor.md`
- `tutorials/current/*.md`
- `examples/README.md`
- `examples/v4/README.md`
- `examples/v4/*.py`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`

Reviewer/internal V4 records updated for release truth:

- `future/v4/v4_goal4773_antigravity_review_intake_and_release_owner_status_2026-06-27.md`
- `future/v4/v4_goal4776_clean_checkout_wheel_smoke_2026-06-27.md`
- `src/rtdsl/v4_goal4773_release_authorization_status.py`

## Corrections Made

1. Replaced current public "release candidate" wording with published
   `V4.0.0` wording.
2. Replaced "tag target ready" wording with the actual published tag:

   ```text
   v4.0.0 -> 1c8f63cbadbb1edfc994c1c2477a94a7f00a8639
   ```

3. Updated the quickstart front-door JSON to expose:

   - `public_release_status: published`
   - `public_release_tag: v4.0.0`
   - `public_release_commit: 1c8f63cbadbb1edfc994c1c2477a94a7f00a8639`
   - `v4_0_0_public_tag_created: true`
   - `bounded_public_release_authorized: true`

4. Preserved the forbidden-claim flags:

   - broad V4 speedup remains unauthorized;
   - broad V4-over-V2.14 speedup remains unauthorized;
   - whole-app speedup remains unauthorized;
   - public true-zero-copy remains unauthorized;
   - Tier-3 callback/PTX public support remains unauthorized;
   - raw OptiX callback support remains unauthorized;
   - broad CuPy performance claims remain unauthorized;
   - embedding/C ABI/non-Python host claims remain unauthorized;
   - app-specific native engine/kernel claims remain unauthorized.

## Public Example Verification

The following current public examples were run from the source tree with
`PYTHONPATH=src;.` and passed:

```text
examples\v4\v4_frontdoor_quickstart.py
examples\v4\operator_callback_planning.py --case complex-callback
examples\v4\custom_predicate_early_exit_planning.py
examples\v4\fixed_radius_torch_device_arrays.py --dry-run
examples\v4\closest_hit_grouped_argmin_torch_device_arrays.py --dry-run
examples\v4\point_group_nearest_witness_torch_device_arrays.py --dry-run
examples\v4\primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
examples\v4\ray_triangle_any_hit_flags_torch_device_arrays.py --dry-run
examples\v4\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
examples\v4\aabb_index_all_ops_count.py --dry-run
```

Result:

```text
all public examples passed
```

## Test Verification

Focused public-surface and release-gate tests:

```text
Ran 23 tests in 31.007s
OK
```

Full V4 local discovery:

```text
Ran 645 tests in 92.488s
OK (skipped=1)
```

## Current Quickstart Shape

The current front-door quickstart now returns the published release state and
keeps claim boundaries closed:

```json
{
  "public_release_status": "published",
  "public_release_tag": "v4.0.0",
  "public_release_commit": "1c8f63cbadbb1edfc994c1c2477a94a7f00a8639",
  "v4_0_0_public_tag_created": true,
  "bounded_public_release_authorized": true,
  "measured_surface_count": 10,
  "candidate_surface_count": 0,
  "complete_rt_core_app_matrix_app_count": 10,
  "complete_rt_core_app_matrix_row_count": 30,
  "broad_v4_speedup_claim_authorized": false,
  "whole_app_speedup_claim_authorized": false,
  "true_zero_copy_authorized": false,
  "tier3_callback_claim_authorized": false,
  "raw_optix_callback_claim_authorized": false
}
```

## Important Boundary

This audit does not move or rewrite the already pushed `v4.0.0` tag. It aligns
the live branch public surface and review records with the published tag. Moving
the remote tag would be the wrong release-management action.

This audit also does not authorize:

- a broad all-app speedup headline;
- a formal app-level high-performance claim;
- V4-over-V3 broad speedup wording;
- Tier-3 callback/PTX public support;
- raw OptiX callback support;
- true-zero-copy wording;
- paper-reproduction speedup wording.

## Goal-Level Decision Audit

1. 我是否愚蠢了？
   - 这一步没有。愚蠢会是打完 tag 以后还让用户入口说
     "release candidate" 或 "tag target ready"。
2. 如果是，我做了哪些动作使得我的决策成为愚蠢的？
   - 已避免：没有改写远端 tag，没有把 release 事实和 broad speedup
     claim 混成一个 flag。
3. 是不是有别的可能性使得我不用愚蠢在某一个思路上？
   - 有：把 public tag state 和 performance claim state 分开。发布事实为
     true，过度性能 claim 仍为 false。
4. 我是否可以开始尝试不同路径，而真正解决问题？
   - 可以。当前路径是主发布公共面审计、示例运行验证、完整 V4 测试、
     外部 AI 审核，而不是继续加新功能逃避发布质量。
