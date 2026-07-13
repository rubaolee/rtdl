# Call For Review: Goal5397 X-HD Native v7 Active-Query Status Stream Smoke

Please strictly review Goal5397.

## Files Under Review

Result report:

```text
history/internal_docs/goal5397_xhd_native_v7_status_stream_smoke_result_2026-07-10.md
```

Primary implementation:

```text
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_api.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/__init__.py
```

POD smoke:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5397_native_status_stream_smoke.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5397_native_status_stream_smoke_pod.json
```

Tests:

```text
tests/goal5397_native_status_stream_frontdoor_test.py
tests/goal5395_native_status_stream_abi_gate_test.py
tests/goal5396_v6_remap_no_go_test.py
```

## Context

Goal5396 rejected remapping native v6 frontier rows into a fake active-query
status stream. Goal5397 is the first real native v7 attempt:

```text
rtdl_optix_collect_active_query_status_stream_3d_v1
```

This goal claims only:

```text
native v7 symbol exists, builds on POD, and emits synthetic app-neutral status
rows through the Python front door.
```

It does **not** claim:

```text
explicit X-HD -lb support;
row-count parity;
hash/sample parity;
Figure 7 or Figure 11 reproduction;
performance ratio;
full X-HD paper reproduction.
```

## Evidence Summary

Local focused tests:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal5397_native_status_stream_frontdoor_test tests.goal5396_v6_remap_no_go_test tests.goal5395_native_status_stream_abi_gate_test
Ran 14 tests OK
```

POD:

```text
preflight: POD_OK, NVIDIA RTX 4000 Ada Generation, driver 550.127.05
python3 -m unittest tests.goal5397_native_status_stream_frontdoor_test: Ran 5 tests OK
make build-optix: succeeded
run_xhd_goal5397_native_status_stream_smoke.py: matched=true
```

Smoke artifact:

```text
valid_count = 4
attempted_count = 4
status_codes = [2]
source_ids = [100, 101]
cell_ids = [10, 11]
native_generic_symbol = rtdl_optix_collect_active_query_status_stream_3d_v1
contract = generic_active_query_status_stream_native_abi_v1
```

## Review Questions

1. Does Goal5397 implement a real native v7 symbol and Python front door rather
   than merely remapping v6 columns at the app/Python level?
2. Is the native/Python naming app-neutral, with no X-HD option, figure, paper,
   or author semantics promoted into RTDL core/native code?
3. Does the POD smoke prove the narrow claim that the v7 symbol builds and
   emits status rows on a synthetic fixture?
4. Does the result report correctly avoid claiming explicit `-lb` support,
   row-count parity, hash/sample parity, Figure 7/11 reproduction, performance
   parity, or full paper reproduction?
5. Is the Goal5395 test amendment appropriate now that the future v7 symbol has
   intentionally appeared, while still preserving Goal5395 as an ABI/gap gate?
6. Is the current limitation clearly documented: v7 currently emits at existing
   emitted-row points and may still inherit v6-like denominator behavior?
7. Is Goal5398 correctly identified as the next required row/hash/status parity
   gate against the Goal5387 author trace v2 oracle?
8. Are there any blocking issues in lifecycle, row schema, overflow behavior,
   POD evidence, or claim boundary?

## Expected Answer Shape

Please respond with:

```text
Verdict: approve_goal5397_native_v7_status_stream_smoke
```

or:

```text
Verdict: revise_goal5397_native_v7_status_stream_smoke
```

Then list:

```text
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to the 8 review questions:
```

## Requested Claim Boundary

Allowed:

```text
Goal5397 proves a real generic native v7 active-query status-stream symbol can
build on POD and emit synthetic status rows through the Python front door.
```

Forbidden:

```text
RTDL supports explicit X-HD -lb.
Goal5397 matches the author status-stream denominator.
Goal5397 solves the missing 6x-active delta.
Goal5397 reproduces Figure 7 or Figure 11.
Goal5397 authorizes an author-vs-RTDL performance ratio.
Goal5397 completes full X-HD paper reproduction.
```
