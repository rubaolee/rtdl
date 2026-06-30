# Goal1793: Mixed Partner Columns Conformance

Status: `accept-with-boundary`

Date: 2026-05-12

## Context

Goal1787 accepted the first OptiX partner host-stage execution bridge for
single-protocol inputs: NumPy CPU, PyTorch CUDA, or CuPy CUDA. Goal1791 added
the timing buckets required before future device-pointer decisions.

Goal1793 closes the small conformance gap called out during review: mixed
partner protocols in one call.

## Test Coverage

New test:

- `tests/goal1793_mixed_partner_columns_conformance_test.py`

Covered cases:

- NumPy ray columns plus CuPy triangle columns at the pack boundary;
- PyTorch CUDA ray columns plus NumPy triangle columns at the execution boundary.

The expected metadata is intentionally conservative:

```text
source_protocols = sorted unique protocols
source_devices = sorted unique devices
transfer_mode = "host_stage"
true_zero_copy_authorized = False
rt_core_speedup_claim_authorized = False
```

## Claim Boundary

Goal1793 does not add a native ABI and does not claim zero-copy or performance.
It only proves that the existing Python-side descriptor/staging bridge handles
mixed partner frameworks without changing the app-agnostic OptiX primitive path.

## Validation

Windows command:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal1793_mixed_partner_columns_conformance_test \
  tests.goal1791_partner_handoff_phase_timing_test \
  tests.goal1787_optix_partner_anyhit_host_stage_test
```

Result:

```text
9 tests ran.
3 passed.
6 skipped.
py_compile passed.
```

The skips are expected on Windows because this environment lacks local PyTorch,
CuPy, and OptiX.

Linux command:

```text
PYTHONPATH=.partner_site:src:. python3 -m unittest \
  tests.goal1793_mixed_partner_columns_conformance_test \
  tests.goal1791_partner_handoff_phase_timing_test \
  tests.goal1787_optix_partner_anyhit_host_stage_test
```

Result:

```text
9 tests ran.
9 passed.
0 skipped.
```

## Independent Review

- [Goal1794 Gemini review](../reviews/goal1794_gemini_review_goal1793_mixed_partner_columns_conformance_2026-05-12.md): `accept-with-boundary`

## Verdict

`accept-with-boundary`: mixed partner-protocol inputs are a supported conformance
case for the first host-stage OptiX partner bridge, still under the same bounded
v2.0 non-claims.
