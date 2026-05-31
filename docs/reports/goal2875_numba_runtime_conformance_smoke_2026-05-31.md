# Goal2875 Numba Runtime Conformance Smoke

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Goal2874 closed the remaining Triton preview conformance rows, leaving only
the Numba fallback rows as explicit runtime gaps. Goal2875 installs Numba on
the NVIDIA pod and runs a narrow runtime conformance smoke for the two declared
Numba fallback operations:

- `segmented_count_i64`
- `segmented_sum_f64`

Both compare to `execute_v2_5_partner_continuation_reference(...)`, and the
invalid-group fixture verifies the device-side validation path fails closed
before reduction.

## Implementation

Updated:

- `src/rtdsl/v2_5_partner_conformance_matrix.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2873_v2_5_partner_conformance_matrix_test.py`
- `tests/goal2874_triton_preview_current_pod_conformance_backfill_test.py`

Added:

- `tests/goal2875_numba_runtime_conformance_smoke_test.py`

The partner conformance matrix now reports:

- `preview_runtime_conformance_complete: true`
- `runtime_conformance_gap_count: 0`
- `release_blocker_count: 0`
- `release_conformance_complete: false`

The final field remains false on purpose. Closing the partner-continuation
runtime conformance matrix is not the same thing as authorizing v2.5 release or
public performance wording.

## Pod Setup

The pod initially lacked Numba. System pip is PEP668-protected, so this
ephemeral pod used:

```text
python3 -m pip install --break-system-packages numba
```

Installed runtime:

```text
numba_version 0.65.1
cuda_available True
```

## Pod Smoke

Manual pod probe:

```text
count [2, 1, 2, 0]
sum [7.0, 4.0, 6.0, 0.0]
invalid_group_ids_rejected group_ids must be in [0, group_count)
```

## Validation

Local validation skips CUDA-gated Numba runtime methods when Numba CUDA is not
available:

```text
py -3 -m unittest \
  tests.goal2875_numba_runtime_conformance_smoke_test \
  tests.goal2874_triton_preview_current_pod_conformance_backfill_test \
  tests.goal2873_v2_5_partner_conformance_matrix_test

Ran 18 tests in 0.792s
OK (skipped=2)
```

Expanded local readiness/conformance slice:

```text
Ran 85 tests in 2.577s
OK (skipped=7)
```

Pod validation from pushed `main`:

```text
commit: fc49b01c
scope:
  tests.goal2875_numba_runtime_conformance_smoke_test
  tests.goal2874_triton_preview_current_pod_conformance_backfill_test
  tests.goal2873_v2_5_partner_conformance_matrix_test

Ran 18 tests in 1.024s
OK
```

Expanded pod readiness/conformance slice:

```text
Ran 85 tests in 1.976s
OK
```

## Boundary

Goal2875 is not a v2.5 release authorization, not a public speedup claim, not a
broad RT-core claim, not a whole-app speedup claim, not true-zero-copy wording,
and not package-install wording.

## Codex Verdict

`accept-with-boundary`
