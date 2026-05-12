# Goal1791: Partner Handoff Phase Timing

Status: `accept-with-boundary`

Date: 2026-05-12

## Context

Goal1787 introduced the first v2.0 OptiX partner execution bridge:
partner-owned NumPy, PyTorch, and CuPy columns are validated through
`RtdlTensorDescriptor`, explicitly staged to host arrays, packed through the
existing app-agnostic OptiX 2-D ray/triangle any-hit ABI, and executed by the
prepared OptiX any-hit count path.

Goal1791 adds the timing boundary requested by the Goal1787 review consensus.
This is still a measurement surface, not a performance claim.

## Implementation

Changed file:

- `src/rtdsl/optix_runtime.py`

New test:

- `tests/goal1791_partner_handoff_phase_timing_test.py`

`pack_optix_ray_triangle_any_hit_2d_partner_inputs(...)` now reports:

```text
metadata["partner_phase_timings_s"]["descriptor_validation"]
metadata["partner_phase_timings_s"]["framework_to_host_staging"]
metadata["partner_phase_timings_s"]["packet_packing"]
```

`run_optix_partner_ray_triangle_any_hit_2d(...)` carries those timing buckets
forward and adds:

```text
result["partner_phase_timings_s"]["optix_prepare"]
result["partner_phase_timings_s"]["optix_count_and_scalar_copyback"]
```

The existing backend-provided `phase_timings` value remains separate. The new
Python-side buckets are intentionally named `partner_phase_timings_s` so they do
not masquerade as native OptiX kernel timings.

## Claim Boundary

Goal1791 does not claim:

- true zero-copy;
- direct device-pointer partner ABI;
- RT-core speedup;
- whole-app acceleration;
- final v2.0 readiness.

The scalar result copyback is not separately separable from the prepared OptiX
count call in this first slice, so it is reported as
`optix_count_and_scalar_copyback`.

## Local Windows Validation

Run command:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal1791_partner_handoff_phase_timing_test \
  tests.goal1787_optix_partner_anyhit_host_stage_test \
  tests.goal1783_numpy_cpu_partner_adapter_test \
  tests.goal1781_real_framework_partner_availability_test \
  tests.goal1777_v2_0_partner_protocol_baseline_test \
  tests.goal1675_partner_protocol_substrate_test \
  tests.goal1671_v1_8_v2_0_partner_gate_test
```

Result:

```text
33 tests ran.
24 passed.
9 skipped.
py_compile passed for the touched Python files.
```

The skips are expected on Windows because this environment lacks the local
OptiX shared library and CUDA partner frameworks.

## Linux Validation

Host:

```text
host: 192.168.1.20
user: lestat
checkout: /home/lestat/work/rtdl_v2_partner_check
gpu: NVIDIA GeForce GTX 1070
OptiX SDK: /home/lestat/vendor/optix-dev
partner packages: /home/lestat/work/rtdl_v2_partner_check/.partner_site
```

Build:

```text
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev
```

Result:

```text
build/librtdl_optix.so built successfully.
29 tests ran.
29 passed.
0 skipped.
```

Tiny-fixture timing sample:

```json
{
  "hit_count": 1,
  "partner_phase_timings_s": {
    "descriptor_validation": 0.0002893749624490738,
    "framework_to_host_staging": 0.000005572335794568062,
    "packet_packing": 0.00010913400910794735,
    "optix_prepare": 0.31605498993303627,
    "optix_count_and_scalar_copyback": 0.00012881204020231962
  },
  "phase_timings": {
    "bvh_build": 0.0,
    "copyback": 0.0,
    "traversal": 0.0
  },
  "transfer_mode": "host_stage"
}
```

This sample validates the shape and availability of the timing buckets. It is
not performance evidence because the geometry fixture is intentionally tiny.

## Independent Review

- [Goal1792 Gemini review](../reviews/goal1792_gemini_review_goal1791_partner_handoff_phase_timing_2026-05-12.md): `accept-with-boundary`

## Verdict

`accept-with-boundary`: Goal1791 adds the agreed timing buckets for the first
partner handoff path while preserving the explicit host-stage claim boundary and
leaving native app-agnostic OptiX ABI unchanged.
