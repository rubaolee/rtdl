# Goal5402 - Generic Status-State Machine Native Smoke Result

Date: 2026-07-10

## Goal

Goal5402 implements the smallest native synthetic status-state smoke required
by the Goal5401 contract.

The target is deliberately narrow:

```text
prove that a generic native status-state front door can emit raw offload rows
before continuation/reduce and report feedback telemetry on a synthetic
non-app fixture.
```

It is not a full X-HD `-lb` implementation and it does not compare against the
Goal5387 author trace v2 oracle.

## Why This Goal Exists

Goal5398 showed the current native v7 status stream does not match the author
explicit `-lb` trace:

```text
Goal5387 author rows = 27,133,990
Goal5398 RTDL v7 rows = 2,600,727
row_count_parity = false
hash_parity = false
```

Goal5400 showed existing knobs cannot repair that mismatch:

```text
under-counted surfaces = 2,188,225 / 2,600,727 rows
overflow surfaces = 3,102,465,405 / 6,436,445,015 attempted rows
```

Goal5401 therefore defined a generic status-state-machine spike contract. This
Goal5402 result implements and executes the first native synthetic smoke for
that contract.

## Implemented System Additions

Native C ABI symbol:

```text
rtdl_optix_active_query_status_state_machine_smoke_v1
```

Python RTDL front door:

```text
active_query_status_state_machine_smoke_native(...)
```

Runner / POD artifact:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5402_status_state_machine_native_smoke.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5402_status_state_machine_native_smoke_pod.json
```

Focused test:

```text
tests/goal5402_status_state_machine_native_smoke_test.py
```

Files changed:

```text
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_api.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/__init__.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5402_status_state_machine_native_smoke.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5402_status_state_machine_native_smoke_pod.json
tests/goal5402_status_state_machine_native_smoke_test.py
```

## Native Smoke Semantics

The synthetic fixture contains:

```text
active queries = 3
candidate rows = 3
heavy_threshold = 5
heavy candidate rows = 2
feedback rows = 1
```

Expected native status rows:

```text
valid_count = 2
attempted_count = 2
active_queue_indices = [0, 2]
query_row_ids = [10, 12]
source_ids = [100, 102]
cell_ids = [50, 52]
status_codes = [2, 2]
transition_phase_codes = [1, 1]
current_best_before_sq = [5.0, 9.0]
current_best_after_sq = [5.0, 9.0]
```

Expected telemetry:

```text
raw_offload_row_count = 2
status_count_offloading = 2
feedback_update_count = 1
feedback_row_count = 1
overflowed = false
```

The POD artifact matches these expectations:

```text
matched = true
status = native_status_state_machine_smoke_passed
native_generic_symbol = rtdl_optix_active_query_status_state_machine_smoke_v1
contract = generic_active_query_status_state_machine_native_spike_v1
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5402_status_state_machine_native_smoke_pod.json
```

## Validation

Local focused tests:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5402_status_state_machine_native_smoke_test \
  tests.goal5401_status_state_machine_spike_contract_test \
  tests.goal5395_native_status_stream_abi_gate_test \
  tests.goal5379_active_query_status_machine_reference_test \
  tests.goal5380_active_query_frontier_bridge_test

Ran 23 tests in 2.506s
OK
```

Local compile check:

```text
$env:PYTHONPATH='src'; py -m py_compile \
  src\rtdsl\optix_runtime.py \
  src\rtdsl\active_query_status.py \
  tests\goal5402_status_state_machine_native_smoke_test.py \
  Paper-reproduction-apps\x-hd-paper\scripts\run_xhd_goal5402_status_state_machine_native_smoke.py

no compile failure
```

POD preflight:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight

POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

POD focused tests before native smoke:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
python3 -m unittest \
  tests.goal5402_status_state_machine_native_smoke_test \
  tests.goal5401_status_state_machine_spike_contract_test \
  tests.goal5395_native_status_stream_abi_gate_test

Ran 13 tests in 1.560s
OK
```

POD native build:

```text
cd /root/rtdl_goal5093
make build-optix

succeeded
```

POD native smoke:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
export RTDL_OPTIX_LIB=/root/rtdl_goal5093/build/librtdl_optix.so
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5402_status_state_machine_native_smoke.py

matched = true
```

POD focused tests after artifact sync:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
python3 -m unittest \
  tests.goal5402_status_state_machine_native_smoke_test \
  tests.goal5401_status_state_machine_spike_contract_test

Ran 10 tests in 0.507s
OK
```

Artifact JSON validation:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5402_status_state_machine_native_smoke_pod.json

valid JSON
```

## Claim Boundary

What Goal5402 proves:

```text
RTDL has a generic native status-state smoke symbol and Python front door.
The symbol builds on POD.
The symbol executes on POD on a synthetic non-app fixture.
The synthetic smoke emits heavy/offload status rows and feedback telemetry.
Overflow is fail-closed in the Python front door tests.
The new public/native names are app-neutral.
```

What Goal5402 does **not** prove:

```text
explicit X-HD -lb support;
Goal5387 author trace row-count parity;
Goal5387 author trace hash/sample parity;
Figure 7 reproduction;
Figure 11 reproduction;
author RT-core parity;
performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

The POD artifact explicitly records:

```text
explicit_lb_support_claimed = false
row_count_parity_claimed = false
hash_sample_parity_claimed = false
figure7_reproduction_claimed = false
figure11_reproduction_claimed = false
performance_ratio_claimed = false
exact_paper_dataset_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
```

## Next Goal

Goal5403 should not jump directly to a full paper claim. It should use the
Goal5402 native smoke as a building block for the next explicit status-state
gate:

```text
Option A: bounded X-HD app oracle gate if a small status-state oracle is
available.

Option B: full Dragon -> AsianDragon Goal5387 oracle gate if the next native
implementation can consume the real active/candidate data.

Option C: fail-close explicit -lb status-state line if the next gate requires
X-HD-specific native semantics.
```

Any next gate must compare at least:

```text
active count;
raw row count;
raw row hash or deterministic samples when comparable;
status_count_offloading;
feedback_update_count or explicit generic not-applicable rationale;
overflow/fail-closed behavior.
```

## Status

```text
completed_generic_status_state_machine_native_smoke__external_lb_parity_pending
```
