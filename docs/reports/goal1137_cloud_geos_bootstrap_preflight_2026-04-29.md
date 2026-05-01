# Goal1137 Cloud GEOS Bootstrap Preflight

Date: 2026-04-29

## Problem

The RTX pod workflow repeatedly hit this failure during strict graph/spatial
gates:

```text
cannot find -lgeos_c
```

This is not an OptiX workload failure. It is a pod bootstrap gap: strict
correctness gates may build RTDL's native CPU/oracle reference path, and that
path links GEOS C. Previously `scripts/goal763_rtx_cloud_bootstrap_check.py`
validated OptiX/CUDA readiness but did not validate GEOS/pkg-config readiness,
so the failure appeared later inside paid workload execution.

## Changes

- `scripts/goal763_rtx_cloud_bootstrap_check.py`
  - Adds GEOS preflight metadata:
    - `pkg_config_exists`
    - pkg-config probes for `geos` and `geos_c`
    - selected usable GEOS pkg-config package
    - `ctypes.util.find_library("geos_c")`
    - Linux install hint
  - Treats missing `pkg-config`, missing GEOS pkg-config package, or missing
    `libgeos_c` as non-dry-run preflight blockers.
- `docs/rtx_cloud_single_session_runbook.md`
  - Adds the standard pod install step:
    `apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libgeos-dev pkg-config`
  - Explains why this is required before running strict graph/spatial gates.
- Tests:
  - `tests/goal763_rtx_cloud_bootstrap_check_test.py`
  - `tests/goal829_rtx_cloud_single_session_runbook_test.py`

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal763_rtx_cloud_bootstrap_check_test \
  tests.goal829_rtx_cloud_single_session_runbook_test -v
```

Result: 11 tests OK.

Additional dry-run:

```bash
PYTHONPATH=src:. python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --dry-run --skip-build --skip-tests \
  --output-json /tmp/goal763_dry_run_geos.json
```

Result: status `ok`; GEOS preflight fields are emitted.

## Boundary

This is a cloud bootstrap reliability fix. It does not run benchmarks, does not
change public RTX wording, and does not authorize release or public RTX speedup
claims.
