# V4 Goal4676 Aggregate-Frontier Protocol Freeze

Date: 2026-06-25

Status:

```text
goal4676_protocol_frozen_pod_smoke_authorized_serious_after_smoke
```

Decision label:

```text
aggregate_frontier_focused_pod_protocol_frozen__same_hardware_smoke_authorized__serious_run_requires_smoke_denominator_success
```

Machine evidence:

```text
future/v4/evidence/v4_goal4676_aggregate_frontier_protocol_freeze_2026-06-25.json
```

## Decision

Goal4676 freezes the focused same-hardware benchmark protocol for:

```text
v4_aggregate_frontier_device_columns_2d_prepared_runner
```

This authorizes a POD smoke run first. A serious run is allowed only if smoke
proves that the V2.14 denominator and V4 runner are actually executable.

## Denominator

V2.14 denominator:

```text
collect_aggregate_frontier_2d_optix if exported by V2.14
+ host-materialized row_offsets/frontier_i64_rows
+ explicit Numba CPU weighted-vector continuation
```

No silent CPU-only fallback is allowed. If the V2.14 OptiX wrapper is not
available on the checked tree/POD, the target must be reclassified or the run
marked inconclusive. It cannot pass by beating a weak denominator.

V3.0.2 is a control because it already has the device-column primitive. V4/V3
parity is not a clean V4 win or failure by itself.

V4 route:

```text
prepare_aggregate_frontier_device_columns_2d_prepared_runner_v4
+ explicit CuPy or Numba downstream weighted-vector continuation
```

## Frozen Bars

| Metric | Bar |
| --- | ---: |
| V4 frontier-only hot over V2.14 | `>= 1.20x` |
| V4 full hot over V2.14 | `>= 1.20x` |
| V4 full wall over V2.14 | `>= 1.10x` |
| Correctness parity | required |
| Large-run checksum parity | required |
| Host frontier materialization in V4 hot path | forbidden |
| Partner migration counts as speed | false |

The frontier-only bar is mandatory. It prevents a CuPy/Numba continuation win
from being mislabeled as a V4 runtime win.

## Entrypoint

```text
scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py
```

Local plan check:

```text
py scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py --print-plan --profile serious --partner cupy
```

Smoke on POD:

```text
python scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py --profile smoke --partner cupy
```

Serious on POD, only after smoke succeeds:

```text
python scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py --profile serious --partner cupy
```

The script writes raw per-version JSON/stderr and `summary.json` under
`future/v4/evidence/`.

## Tests

Passed:

```text
py -m unittest tests.v4_goal4676_aggregate_frontier_protocol_test
```

Result:

```text
Ran 3 tests in 0.000s
OK
```

Passed:

```text
py -m unittest tests.v4_goal4675_aggregate_frontier_prepared_runner_test tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_scope_gate_test
```

Result:

```text
Ran 29 tests in 2.633s
OK
```

Passed:

```text
py -m py_compile scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py src/rtdsl/v4_goal4676_aggregate_frontier_protocol.py
```

## Non-Authorization

This file does not authorize release, public speedup wording, whole-app
high-performance wording, RT-core speedup wording, true-zero-copy wording,
Tier-3 callback support, raw OptiX callbacks, C ABI, embedding, non-Python
hosts, automatic partner selection, or app-identity native kernels.
