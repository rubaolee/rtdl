# Goal4775 - V4 Release Staging Manifest

Status: `release_staging_manifest_created__pathspec_ready__tag_still_requires_clean_commit`

## Summary

- dirty file entries from `git status -uall`: `3`
- stage for V4 release commit: `3`
- exclude from V4 release commit: `0`
- hold V3 history out of V4 tag: `0`
- manual review required: `0`
- pathspec ready: `true`
- direct git tag allowed now: `false`
- clean release commit required before tag: `true`
- POD required for this manifest: `false`
- Claude required for this manifest: `false`

## Bucket Counts

| Bucket | Count |
| --- | ---: |
| `stage_for_v4_release_commit` | `3` |

## Pathspec

- generated pathspec file: `C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/v4_goal4775_release_stage_pathspec_2026-06-27.txt`
- use only after the release owner agrees this exact staging set is the desired V4.0 tag content

## Required Stage Paths

- `README.md`
- `docs/README.md`
- `docs/current_v4_status.md`
- `docs/v4_release_notes.md`
- `docs/v4_engineering_summary.md`
- `docs/app_level_benchmark_summary.md`
- `docs/learn/operator_catalog.md`
- `docs/learn/partner_choice.md`
- `docs/public_documentation_map.md`
- `examples/README.md`
- `examples/current/research_benchmarks/README.md`
- `future/README.md`
- `future/v4/README.md`
- `history/v4_0_release_audit_2026-06-27/README.md`
- `tutorials/current/06_benchmark_apps.md`
- `tutorials/current/07_partner_choice.md`
- `future/v4/V4_CURRENT_AGENT_REFRESH_RUNBOOK_2026-06-25.md`
- `future/v4/reviews/v4_gemini_full_coverage_review_debt_for_antigravity_2026-06-27.md`
- `future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md`
- `future/v4/v4_goal4773_antigravity_review_intake_and_release_owner_status_2026-06-27.md`
- `future/v4/v4_goal4779_pre_release_items_1_to_5_completion_2026-06-27.md`
- `future/v4/reviews/antigravity_v4_pre_release_items_1_to_5_completion_2026-06-27.md`
- `future/v4/reviews/call_for_review_v4_pre_release_items_1_to_5_completion_2026-06-27.md`
- `future/v4/reviews/forward_message_v4_pre_release_items_1_to_5_completion_2026-06-27.txt`
- `future/v4/evidence/v4_goal4774_release_packaging_audit_2026-06-27.json`
- `future/v4/v4_goal4774_release_packaging_audit_2026-06-27.md`
- `future/v4/evidence/v4_goal4775_release_staging_manifest_2026-06-27.json`
- `future/v4/v4_goal4775_release_staging_manifest_2026-06-27.md`
- `future/v4/v4_goal4775_release_stage_pathspec_2026-06-27.txt`
- `src/rtdsl/v4_goal4773_release_authorization_status.py`
- `src/rtdsl/v4_goal4774_release_packaging_audit.py`
- `src/rtdsl/v4_goal4775_release_staging_manifest.py`
- `scripts/v4_goal4775_release_staging_manifest.py`
- `scripts/v4_release_clean_checkout_gate.py`
- `tests/v4_goal4773_release_authorization_status_test.py`
- `tests/v4_goal4774_release_packaging_audit_test.py`
- `tests/v4_goal4775_release_staging_manifest_test.py`
- `tests/v4_release_clean_checkout_gate_test.py`

## V3 History Held Out

These paths are not staged for the V4 public tag. They can remain as workspace history
or be archived separately, but they must not be silently bundled into the V4 release commit.


## Excluded Raw Or External Artifacts


## Goal-Level Decision Audit

1. 我是否愚蠢了？没有继续 `git add .`，这是正确的；但 Goal4774 的候选分桶过宽，若直接使用会愚蠢。
2. 如果是，我做了哪些动作使决策愚蠢？把所有 `tests/`、`scripts/` 粗略视为候选，会把 V3 Phoenix 历史混进 V4 tag。
3. 是否有别的路径避免卡在坏思路？有：逐文件展开 `git status -uall`，把 V3 history、raw logs、external/build artifacts 独立排除。
4. 是否可以尝试不同路径真正解决问题？可以，下一步只用这份 pathspec 做可审 staging，不直接打 tag。

## Next Step

Run the manifest tests and full V4 tests. If they pass, the release owner can inspect
the generated pathspec before any staging or commit. A public V4.0 tag still requires
a clean release commit; this file does not create the tag.
