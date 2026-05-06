# Goal1338 v1 Status Summary Label Refresh

Date: 2026-05-05

## Scope

Refresh the active v1.0 RTX status-page generator and regenerated status
artifacts so ANN and Barnes-Hut native-continuation wording uses the current
specific summary labels instead of stale generic `native C++` wording.

Changed wording:

- ANN: native KNN rerank summaries.
- Barnes-Hut: native fixed-radius candidate summaries.

## Boundary

- This is generated status-page wording precision only.
- No new reviewed public wording row is added.
- No new speedup claim is added.
- The existing v1.0 RTX status boundaries remain unchanged.
- No Vulkan, HIPRT, or Apple RT implementation work is added.

## Regeneration

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal947_v1_rtx_app_status_page.py
```

Regenerated:

- `docs/v1_0_rtx_app_status.md`.
- `docs/reports/goal947_v1_rtx_app_status_2026-04-25.json`.

## Local Validation

Commands:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal1010_public_rtx_readme_wording_test
PYTHONPATH=src:. python3 -m unittest $(find tests -maxdepth 1 -name 'goal13*_test.py' -exec basename {} .py \; | sed 's/^/tests./')
git diff --check
```

Result:

- Status/generator/wording tests: 20 tests OK.
- Goal13 sweep: 76 tests OK.
- `git diff --check`: OK.

Additional attempted broader batch:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal1010_public_rtx_readme_wording_test \
  tests.goal1044_public_rtx_cloud_policy_sync_test
```

Result:

- The Goal947/Goal938/Goal1010 portion passed.
- `tests.goal1044_public_rtx_cloud_policy_sync_test` failed six assertions
  because it still expects `Goal1048` in cloud-policy text for rows that now
  carry newer Goal1262/Goal1263/Goal1267 policy text.
- That failure is pre-existing policy-test drift and was not changed in this
  wording-label cleanup.

## Pod Validation

Pending after the source commit is pushed and the pod resets from `origin/main`.
