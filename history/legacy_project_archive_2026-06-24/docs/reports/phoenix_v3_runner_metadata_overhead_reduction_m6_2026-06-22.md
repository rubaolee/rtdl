# Phoenix V3 Runner Metadata Overhead Reduction M6

Date: 2026-06-22
Status: `local_shared_runtime_overhead_fix_not_release`

## Purpose

Hausdorff M5 showed a useful negative result: the productized
`prepared_execution_session_runner` executes the route correctly, but its
wrapper/session/reporting tax is enough to lose by about 2-3% against the legacy
prepared OptiX front door. That makes generic runner overhead a V3 trunk issue,
not a Hausdorff-specific issue.

This M6 pass reduces reusable overhead in the shared prepared-session and
prepared-execution metadata path. It does not add an app-specific fast path.

## Code Changes

Changed:

- `src/rtdsl/prepared_session_residency.py`
- `src/rtdsl/prepared_execution.py`

Generic changes:

1. `RtdlPreparedSessionCacheKey.stable_id` is now computed once during key
   construction and cached in the frozen key object.
2. `PreparedExecutionPhaseTiming.to_dict()` no longer uses
   `dataclasses.asdict()`, avoiding recursive dataclass-copy overhead on every
   runner report.
3. `PreparedExecutionReport.to_dict()` now builds phase payloads and summary
   seconds in one pass instead of rebuilding phase dictionaries and rescanning
   phases through multiple properties.

Unchanged boundaries:

- explicit backend/partner required
- prepared-session cache remains explicit and caller-owned
- full report metadata remains present
- release/public/broad V3-over-V2/true-zero-copy/V4 flags remain false
- no app-specific native-engine logic was added

## Local Micro Evidence

Same local Windows Python environment, `PYTHONPATH=src;.`, before and after the
shared-runtime patch:

| Operation | Before | After | Change |
| --- | ---: | ---: | ---: |
| 20k `stable_id` reads | 2.1060653 s | 0.0034586 s | about 609x faster |
| 20k phase `to_dict()` calls | 0.8431725 s | 0.0153132 s | about 55x faster |

Additional after-only sanity measurement:

```text
20k full PreparedExecutionReport.to_dict() calls: 0.2040724 s
```

Reusable local microbench artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_runner_overhead_microbench_m6_20260622.json
```

Artifact result:

```text
stable_id_read: 0.000000187 s/call
phase_to_dict: 0.000000706 s/call
report_to_dict: 0.000013152 s/call
noop_runner_call: 0.000799197 s/call
```

These are metadata-path improvements. They do not by themselves prove V3
release performance. They are intended to reduce the fixed runner tax that
showed up in RTDBSCAN and Hausdorff runner-vs-legacy comparisons.

## Local Gates

Compile:

```text
PYTHONPATH=src;. py -3 -m py_compile \
  src/rtdsl/prepared_execution.py \
  src/rtdsl/prepared_session_residency.py

OK
```

Focused runner/app/wording gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_rtdbscan_component_signature_optimization_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_aabb_prepare_reuse_pod_runner_test \
  tests.v3_phoenix_librts_aabb_count_runner_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test \
  tests.v3_release_wording_gate_test

50 tests OK
```

Earlier focused subset:

```text
tests.v3_phoenix_prepared_execution_session_runner_test
tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test
tests.v3_phoenix_aabb_prepare_reuse_pod_runner_test
tests.v3_phoenix_librts_aabb_count_runner_test

38 tests OK
```

Microbench gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_runner_overhead_microbench_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.goal3873_prepared_session_residency_contract_test \
  tests.goal3877_explicit_prepared_session_reuse_helper_test

41 tests OK
```

## What This Does Not Authorize

This report does not authorize:

- V3 release.
- all-app pod rerun.
- public speedup wording.
- broad V3-over-V2 wording.
- whole-app, whole-Hausdorff, whole-RTDBSCAN, or whole-AABB speedup claims.
- true-zero-copy wording.
- V4 / external device-buffer wording.

## Proposed Next Step

Seek bounded external review. If accepted, run a focused pod no-regression
validation on the affected productized runner route, starting with the smallest
route that can expose the same tax:

1. Hausdorff M5 runner-vs-legacy no-regression rerun, or
2. RTDBSCAN repeated runner-vs-legacy parity rerun, or
3. AABB runner route sanity rerun if the reviewer thinks AABB is the better
   low-risk canary.

Do not run all-app yet.

## Goal-Level Decision Audit

Decision: implement a shared metadata/cache-key overhead reduction before
spending pod time.

1. Was I foolish?

   No for this decision. The failed Hausdorff M5 gate and earlier RTDBSCAN
   parity recovery both point at shared runner tax.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be to make a Hausdorff-only or
   RTDBSCAN-only workaround and call it V3 core.

3. Was there another path that would have avoided getting stuck?

   Yes. A fresh third Set-A family could be chosen immediately, but it would run
   through the same taxed runner and could repeat the same ambiguity.

4. Can I now try a different path that actually solves the problem?

   Yes. This patch reduces overhead in the shared execution trunk, so every
   productized runner route can benefit without changing app semantics.
