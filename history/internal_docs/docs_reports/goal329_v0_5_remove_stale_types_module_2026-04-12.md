# Goal 329 Report: v0.5 Remove Stale Types Module

Date:
- `2026-04-12`

Goal:
- complete the `layout_types` collision fix by removing the still-tracked stale
  `src/rtdsl/types.py`

Why this goal exists:
- Goal 328 updated imports and created `src/rtdsl/layout_types.py`
- but the old `src/rtdsl/types.py` file was still tracked in Git
- that means the repo state was not as clean as the Goal 328 report implied

What changed:
- the stale tracked `src/rtdsl/types.py` file is removed from the repo
- the existing Goal 328 tests are rerun to prove the deletion does not break the
  now-canonical `layout_types.py` path

Verification:
- `python3 -m unittest tests.goal328_v0_5_layout_types_name_collision_test tests.test_core_quality`

Honesty boundary:
- this is a cleanup completion slice for Goal 328
- it does not change public semantics beyond making the repo match the already
  claimed collision fix
