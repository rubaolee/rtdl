# Goal 155 OptiX Linux SDK Path Robustness

## Verdict

The Linux OptiX build pipeline is now more robust.

## Trigger

External trigger:

- [Antigravity RTDL test report](/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-07-antigravity-review-rtdl-test-report.md)

The relevant user-visible trigger was:

- the external reviewer excluded OptiX from the Linux run because the native
  dependency appeared to be missing
- follow-up reproduction on the same Linux host confirmed the concrete build
  failure:
  - `fatal error: optix.h: No such file or directory`

## Root Cause

The Linux host already had an OptiX SDK installed, but not at the Makefile's
default path.

Actual host SDK location:

- `/home/lestat/vendor/optix-dev/include/optix.h`

Previous default assumption:

- `/opt/optix/include/optix.h`

So this was not a missing-host-dependency case.
It was a path-discovery robustness gap in RTDL's OptiX build pipeline.

## What Changed

- [Makefile](/Users/rl2025/rtdl_python_only/Makefile)

The Makefile now:

- auto-detects common OptiX SDK roots, including:
  - `/opt/optix`
  - `/usr/local/optix`
  - `$(HOME)/vendor/optix-dev`
  - other common SDK root names
- keeps `OPTIX_PREFIX` override support
- fails with a clearer message if `optix.h` is still missing

## Validation

Remote Linux host:

- `lestat@192.168.1.20`
- repo path:
  - `/home/lestat/work/rtdl_python_only`

Checks:

- host SDK discovery:
  - `/home/lestat/vendor/optix-dev/include/optix.h`
  - `/home/lestat/vendor/optix-dev/include/optix_stubs.h`
- `make build-optix`
  - now succeeds without manual `OPTIX_PREFIX` override
- focused OptiX runtime test:
  - `PYTHONPATH=src:. python3 -m unittest tests.rtdl_sorting_test.RtDlSortingTest.test_optix_small_case_matches_cpu_sort`
  - `Ran 1 test in 0.424s`
  - `OK`

## Important Interpretation

The Antigravity report was directionally right about the failing user
experience, but it did not itself produce the compiler error above. That exact
failure was reproduced in follow-up investigation on the same Linux host.

The exact root cause was narrower than "OptiX SDK entirely missing."

The honest final interpretation is:

- the host already had a usable SDK
- RTDL did not find it automatically
- this goal fixes that robustness problem
