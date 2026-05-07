# Goal 1438 v1.5.1 COLLECT_K_BOUNDED Post-Hardening Closure Snapshot

## Verdict

ACCEPTED as a post-hardening current-state snapshot after a broad Linux GPU-pod rerun.

The first broad pod rerun found one non-collect-k blocker in the Goal15 native helper launch path. The blocker was isolated to `tests.report_smoke_test.ReportSmokeTest.test_full_verification_smoke_path`, fixed by restoring executable bits after Linux/macOS native helper compilation, and then revalidated by focused and broad reruns.

This report does not authorize stable `COLLECT_K_BOUNDED` promotion, public speedup wording, zero-copy wording, whole-app speedup claims, release tags, or release action.

## Fixed Blocker

Initial broad pod rerun at Git HEAD `57241f6d734b946a00b6ef7c3b654cd1ca6ebbc6` on NVIDIA RTX A5000 failed with exactly one error:

```text
ERROR: test_full_verification_smoke_path (report_smoke_test.ReportSmokeTest.test_full_verification_smoke_path)
PermissionError: [Errno 13] Permission denied: '/workspace/rtdl/build/goal15_native/goal15_lsi_native'
Ran 2829 tests in 1214.674s
FAILED (errors=1, skipped=221)
```

The failing subpath was:

```text
tests/report_smoke_test.py
scripts/run_full_verification.py
scripts/goal15_compare_embree.py
subprocess.run([goal15_lsi_native, ...])
```

The fix is in `scripts/goal15_compare_embree.py`: after non-Windows native helper compilation, the helper output path is explicitly marked executable with user/group/other execute bits before it is launched.

## Post-Fix Validation

Windows focused validation after the Goal15 chmod hardening:

```text
py -3 -m unittest tests.report_smoke_test.ReportSmokeTest.test_full_verification_smoke_path
Ran 1 test in 42.116s
OK
```

Linux GPU-pod focused validation after the Goal15 chmod hardening:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIB=/workspace/rtdl/build/librtdl_optix.so python3 -m unittest tests.report_smoke_test.ReportSmokeTest.test_full_verification_smoke_path tests.goal15_compare_test
Ran 2 tests in 25.511s
OK (skipped=1)
```

Linux GPU-pod broad rerun after the Goal15 chmod hardening:

```text
Git HEAD: 57241f6d734b946a00b6ef7c3b654cd1ca6ebbc6 plus working-tree Goal15 chmod hardening
GPU: NVIDIA RTX A5000, driver 580.126.09, 24564 MiB
PYTHONPATH=src:. RTDL_OPTIX_LIB=/workspace/rtdl/build/librtdl_optix.so python3 -m unittest discover -s tests -p '*_test.py'
Ran 2829 tests in 1582.304s
OK (skipped=221)
```

Artifacts:

- `docs/reports/goal1438_v1_5_1_post_hardening_broad_pod_unittest_discover_2026-05-07.txt`
- `docs/reports/goal1438_v1_5_1_post_hardening_broad_pod_unittest_discover_rerun2_2026-05-07.txt`
- `docs/reports/goal1438_v1_5_1_post_hardening_broad_pod_unittest_discover_rerun2_2026-05-07.status`

## Completed v1.5.1 Hardening

- Goal1435 hardened the readiness evidence registry so all six required readiness gates have explicit evidence entries.
- Goal1436 hardened the release-surface proposal so whole-app speedup claim blocking is an explicit proposal-level false flag.
- Goal1437 hardened `validate_collect_k_bounded_result(...)` so missing `capacity` and `valid_count` metadata fails clearly while preserving `valid_count`-only transition compatibility.
- Goal1438 hardened the Goal15 native-helper compile/launch path exposed by the broad pod rerun.

## Remaining Boundaries

- `COLLECT_K_BOUNDED` remains on the v1.5.1 Python+RTDL promotion track, not a stable public primitive.
- The accepted release-surface scope remains documented experimental public-candidate only.
- Public docs changes remain separate from this snapshot and require explicit authorization.
- Stable promotion requires a separate decision package and required review.
- Speedup wording, zero-copy wording, whole-app speedup claims, broad workload claims, release tags, and release action remain blocked.

## Recommendation

Use this package as the post-hardening v1.5.1 current-state evidence base. The next decision should be explicit: either prepare a reviewed public-doc link patch for the documented experimental candidate surface, or keep `COLLECT_K_BOUNDED` internal and move the next technical work to v1.5.2.
