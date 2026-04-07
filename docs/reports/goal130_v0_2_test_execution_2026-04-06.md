# Goal 130 Report: v0.2 Test Execution

Date: 2026-04-06
Status: accepted

## Summary

Goal 130 closed the current v0.2 test-plan-and-execution line.

The accepted package covers:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- the narrow generate-only workflow

The work was done in four stages:

1. Claude-authored initial v0.2 test plan
2. repo-accuracy review and repair of that plan
3. practical local test execution and Linux/PostGIS large-scale execution
4. external review of the finished Goal 130 package

## Real problems found

### Plan accuracy

The initial Claude-authored plan referenced:

- `tests.plan_schema_test`

That file does not exist in the repo. The accepted plan removes that reference
and stays bounded to the real test surface.

### Stale test runner coverage

The repo test-matrix runner:

- [run_test_matrix.py](/Users/rl2025/rtdl_python_only/scripts/run_test_matrix.py)

did not expose an explicit v0.2 runner path. That meant the v0.2 package could
be tested manually, but the canonical runner surface had drifted behind the
actual feature set.

Accepted repair:

- add `v0_2_local`
- add `v0_2_linux`
- add `v0_2_full`

and keep those groups disjoint from the older broad `unit/integration/system`
groups.

### Misleading prepared-path rendering

The large-scale markdown renderers for the two workload families were rendering
unsupported prepared modes as:

- `0.000000`

That looked like a real measured zero rather than an unsupported mode.

Accepted repair:

- render unsupported prepared means as `n/a`

in:

- [goal118_segment_polygon_linux_large_perf.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal118_segment_polygon_linux_large_perf.py)
- [goal128_segment_polygon_anyhit_postgis.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal128_segment_polygon_anyhit_postgis.py)

## Local execution

### Compile pass

Command:

```bash
python3 -m compileall src examples scripts tests
```

Result:

- clean compile pass

### Focused local v0.2 regression

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal110_segment_polygon_hitcount_closure_test \
  tests.goal128_segment_polygon_anyhit_postgis_test \
  tests.goal111_generate_only_mvp_test \
  tests.goal113_generate_only_maturation_test \
  tests.goal129_generate_only_second_workload_test
```

Result:

- `20` tests
- `OK`
- `7` skipped

This Mac is only a local limited platform for:

- Python reference
- C/oracle
- Embree

The skips are the known environment-gated native/GEOS limitations on this Mac.
Linux remains the primary v0.2 development and validation platform.

### Canonical v0.2 local matrix

Command:

```bash
python3 scripts/run_test_matrix.py --group v0_2_local
```

Result:

- `28` tests
- `OK`
- `3` skipped

This runner group is the accepted local v0.2 unittest surface. It does not
include the large Linux/PostGIS performance scripts.

## Linux/PostGIS large-scale execution

The large-scale package was executed on:

- `lestat@192.168.1.20`

This Linux host is the primary v0.2 development and validation platform for:

- PostGIS-backed correctness
- OptiX
- Vulkan
- large deterministic performance rows

Artifacts are saved under:

- [goal130_v0_2_large_scale_artifacts_2026-04-06](/Users/rl2025/rtdl_python_only/docs/reports/goal130_v0_2_large_scale_artifacts_2026-04-06)

### `segment_polygon_hitcount`

Key rows:

These figures are the current-run timings from the PostGIS-backed validation
scripts, not isolated micro-benchmark means.

- `x64`
  - PostGIS `0.008281 s`
  - CPU `0.010713 s`
  - Embree `0.009943 s`
  - OptiX `0.006013 s`
  - Vulkan `0.002166 s`
  - parity `true`
- `x256`
  - PostGIS `0.050084 s`
  - CPU `0.008556 s`
  - Embree `0.007390 s`
  - OptiX `0.007281 s`
  - Vulkan `0.007637 s`
  - parity `true`
- `x1024`
  - PostGIS `0.312690 s`
  - CPU `0.031800 s`
  - Embree `0.028724 s`
  - OptiX `0.029008 s`
  - Vulkan `0.038824 s`
  - parity `true`

### `segment_polygon_anyhit_rows`

Key rows:

These figures are the current-run timings from the PostGIS-backed validation
scripts, not isolated micro-benchmark means.

- `x64`
  - PostGIS `0.003299 s`
  - CPU `0.011075 s`
  - Embree `0.009967 s`
  - OptiX `0.006157 s`
  - Vulkan `0.003111 s`
  - parity `true`
- `x256`
  - PostGIS `0.014823 s`
  - CPU `0.008495 s`
  - Embree `0.011838 s`
  - OptiX `0.007223 s`
  - Vulkan `0.007199 s`
  - parity `true`
- `x1024`
  - PostGIS `0.054162 s`
  - CPU `0.033502 s`
  - Embree `0.029918 s`
  - OptiX `0.036233 s`
  - Vulkan `0.029532 s`
  - parity `true`

## Findings from the large-scale run

### Correctness

No correctness mismatch was found in the accepted Linux/PostGIS large rows for
either workload family.

### Performance

The main performance findings are:

- small-row overhead still leaves RTDL behind PostGIS on several `x64` rows
- the large-row crossover is strong for both workload families
- OptiX is no longer a correctness risk here, but for `anyhit_rows` at `x1024`
  it is slightly behind Embree and Vulkan
- Vulkan is acceptable under the current product rule:
  - must work
  - must not be very slow
  - does not need to be the fully optimized flagship backend

## Final state

Goal 130 is accepted because it produced:

- a repo-accurate v0.2 test plan
- real repairs to test/process/reporting drift
- a practical local v0.2 runner surface
- Linux/PostGIS-backed large-scale correctness and performance evidence

Two documentation boundaries should be kept explicit when citing this package:

- the quoted large-row timing figures are validation-script timings, not the
  isolated means from the standalone perf renderers
- `python3 scripts/run_test_matrix.py --group v0_2_full` is not a full
  reproduction of the Linux performance evidence, because the large PostGIS/perf
  scripts remain separate environment-gated execution steps

This goal did not reveal a new blocking correctness defect in the current v0.2
surface. The remaining issues are about:

- small-row overhead
- backend ordering and maturity differences
- continued Linux large-scale observation as v0.2 expands
