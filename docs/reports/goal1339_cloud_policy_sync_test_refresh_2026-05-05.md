# Goal1339 Cloud Policy Sync Test Refresh

Date: 2026-05-05

## Scope

Refresh `tests.goal1044_public_rtx_cloud_policy_sync_test` so it reflects the
current cloud-policy source of truth after later Goal1262, Goal1263, Goal1264,
and Goal1267 updates.

The test now distinguishes:

- Legacy RTX batch-policy rows that still must mention Goal1048, Goal1058,
  Goal1135, Goal1136, and Goal1177.
- Superseded maturity/status rows whose policy is now owned by newer evidence
  and boundary text:
  `database_analytics`, `graph_analytics`,
  `polygon_pair_overlap_area_rows`, and `polygon_set_jaccard`.

## Boundary

- This is a test-sync change only.
- No status matrix, support matrix, public wording, or runtime behavior is
  changed.
- No new speedup claim is added.
- No Vulkan, HIPRT, or Apple RT implementation work is added.

## Local Validation

Commands:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1044_public_rtx_cloud_policy_sync_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal1010_public_rtx_readme_wording_test
PYTHONPATH=src:. python3 -m unittest $(find tests -maxdepth 1 -name 'goal13*_test.py' -exec basename {} .py \; | sed 's/^/tests./')
git diff --check
```

Result:

- Affected status/cloud-policy tests: 23 tests OK.
- Goal13 sweep: 76 tests OK.
- `git diff --check`: OK.

## Pod Validation

Pod SSH:

```bash
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Validation command after resetting from Git:

```bash
cd /root/rtdl_python_only
git fetch origin main
git reset --hard origin/main
git rev-parse HEAD
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1044_public_rtx_cloud_policy_sync_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal1010_public_rtx_readme_wording_test
```

Result:

- Commit: `4f6ee6644b572ab33223edc75cbf0c4c7f3705ca`.
- Targeted pod tests: 23 tests OK in 0.225s.
