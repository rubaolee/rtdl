# Goal 1438 External Review Request

Please review the current uncommitted Goal1438 patch and report package.

## Scope

Goal1438 is a post-hardening v1.5.1 current-state package for `COLLECT_K_BOUNDED` plus one broad-regression blocker fix.

The first broad Linux GPU-pod rerun at HEAD `57241f6d734b946a00b6ef7c3b654cd1ca6ebbc6` found one exact blocker outside collect-k:

```text
PermissionError: [Errno 13] Permission denied: '/workspace/rtdl/build/goal15_native/goal15_lsi_native'
Ran 2829 tests in 1214.674s
FAILED (errors=1, skipped=221)
```

The patch updates `scripts/goal15_compare_embree.py` so non-Windows native helper outputs are explicitly marked executable after compilation.

## Files To Review

- `scripts/goal15_compare_embree.py`
- `docs/reports/goal1438_v1_5_1_post_hardening_closure_snapshot_2026-05-07.md`
- `docs/reports/goal1438_v1_5_1_post_hardening_broad_pod_unittest_discover_2026-05-07.txt`
- `docs/reports/goal1438_v1_5_1_post_hardening_broad_pod_unittest_discover_rerun2_2026-05-07.txt`
- `docs/reports/goal1438_v1_5_1_post_hardening_broad_pod_unittest_discover_rerun2_2026-05-07.status`

## Validation

Windows focused validation after the chmod hardening:

```text
py -3 -m unittest tests.report_smoke_test.ReportSmokeTest.test_full_verification_smoke_path
Ran 1 test in 34.159s
OK
```

Linux GPU-pod focused validation after the chmod hardening:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIB=/workspace/rtdl/build/librtdl_optix.so python3 -m unittest tests.report_smoke_test.ReportSmokeTest.test_full_verification_smoke_path tests.goal15_compare_test
Ran 2 tests in 25.511s
OK (skipped=1)
```

Linux GPU-pod broad rerun after the chmod hardening:

```text
Ran 2829 tests in 1582.304s
OK (skipped=221)
```

`git diff --check` passed with only expected Windows LF-to-CRLF warnings.

## Review Questions

1. Is the Goal15 chmod hardening an appropriate fix for the isolated permission blocker?
2. Does the Goal1438 report accurately distinguish the initial broad failure from the passing rerun?
3. Does the package preserve the v1.5.1 claim boundary: no stable `COLLECT_K_BOUNDED` promotion, no speedup wording, no zero-copy wording, no whole-app claims, no release tags, and no release action?

Please answer with `ACCEPT`, `ACCEPT WITH NOTES`, or `REJECT`, and list precise blockers if rejected.
