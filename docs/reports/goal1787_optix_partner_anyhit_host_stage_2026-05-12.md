# Goal1787: OptiX Partner Any-Hit Host-Stage Execution

Status: `accept-with-boundary`

Date: 2026-05-12

## Context

Goal1785 proved the v2.0 partner protocol against real PyTorch CUDA, CuPy CUDA,
and NumPy CPU tensors on the local Linux validation host. Goal1787 wires the
first narrow OptiX execution path through partner descriptors.

This is intentionally the smallest app-agnostic RT path:

```text
2-D ray/triangle ANY_HIT count
```

It does not add a native partner ABI. Partner-owned columns are validated
through `RtdlTensorDescriptor`, explicitly staged to host arrays, packed through
the existing app-agnostic OptiX ray/triangle ABI, and executed by the existing
prepared OptiX any-hit count path.

## Implementation

Changed files:

- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `tests/goal1787_optix_partner_anyhit_host_stage_test.py`

New public helpers:

```text
pack_optix_ray_triangle_any_hit_2d_partner_inputs(ray_columns, triangle_columns)
run_optix_partner_ray_triangle_any_hit_2d(ray_columns, triangle_columns)
```

Accepted ray columns:

```text
ids, ox, oy, dx, dy, tmax
```

Accepted triangle columns:

```text
ids, x0, y0, x1, y1, x2, y2
```

For each column, the helper calls `rt.partner.auto(...).tensor(...)`, verifies
that the descriptor is one-dimensional, records source protocol/device metadata,
and host-stages the column:

- NumPy: `numpy.asarray(...)`
- PyTorch: `tensor.detach().cpu().numpy()`
- CuPy: `cupy.asnumpy(...)`

The staged arrays then flow into existing packet builders:

```text
pack_rays_2d_from_arrays(...)
pack_triangles_2d_from_arrays(...)
```

The execution helper then calls:

```text
prepare_optix_ray_triangle_any_hit_2d(...).count(...)
```

## Claim Boundary

This is a partner execution bridge, not a zero-copy bridge.

The returned metadata explicitly records:

```text
transfer_mode = "host_stage"
true_zero_copy_authorized = False
partner_tensor_handoff_authorized = True
rt_core_speedup_claim_authorized = False
```

The native engine remains app-agnostic. No PyTorch, CuPy, NumPy, or app-specific
vocabulary is added to native code or native exported symbols.

## Local Windows Validation

Run command:

```text
PYTHONPATH=src py -3 -m unittest \
  tests.goal1787_optix_partner_anyhit_host_stage_test \
  tests.goal1783_numpy_cpu_partner_adapter_test \
  tests.goal1781_real_framework_partner_availability_test \
  tests.goal1777_v2_0_partner_protocol_baseline_test

PYTHONPATH=src py -3 -m py_compile \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/__init__.py \
  tests/goal1787_optix_partner_anyhit_host_stage_test.py
```

Result:

```text
21 tests ran.
13 passed.
8 skipped.
py_compile passed.
```

Skips are expected on Windows because this environment has no local PyTorch,
CuPy, or OptiX shared library.

## Linux Validation

Host:

```text
host: 192.168.1.20
user: lestat
checkout: /home/lestat/work/rtdl_v2_partner_check
base git commit: 57848676a2618b2fd6e8d7f525741f4c83696d96
gpu: NVIDIA GeForce GTX 1070
driver: 580.126.09
nvcc: CUDA 12.0
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
```

Run command:

```text
PYTHONPATH=.partner_site:src:. python3 -m unittest \
  tests.goal1787_optix_partner_anyhit_host_stage_test \
  tests.goal1781_real_framework_partner_availability_test \
  tests.goal1783_numpy_cpu_partner_adapter_test \
  tests.goal1777_v2_0_partner_protocol_baseline_test \
  tests.goal1675_partner_protocol_substrate_test
```

Result:

```text
27 tests ran.
27 passed.
0 skipped.
```

The suite includes actual execution from:

- NumPy CPU columns;
- PyTorch CUDA columns;
- CuPy CUDA columns.

## Concrete Output

The same triangle/ray fixture was executed through NumPy, PyTorch CUDA, and
CuPy CUDA partner columns. Expected hit count is `1`.

Observed:

```json
{
  "numpy": {
    "source_protocols": ["numpy"],
    "source_devices": ["cpu:0"],
    "transfer_mode": "host_stage",
    "hit_count": 1,
    "true_zero_copy_authorized": false,
    "rt_core_speedup_claim_authorized": false
  },
  "torch_cuda": {
    "source_protocols": ["torch"],
    "source_devices": ["cuda:0"],
    "transfer_mode": "host_stage",
    "hit_count": 1,
    "true_zero_copy_authorized": false,
    "rt_core_speedup_claim_authorized": false
  },
  "cupy_cuda": {
    "source_protocols": ["cupy"],
    "source_devices": ["cuda:0"],
    "transfer_mode": "host_stage",
    "hit_count": 1,
    "true_zero_copy_authorized": false,
    "rt_core_speedup_claim_authorized": false
  }
}
```

The tiny fixture reports zero-valued phase timings from the existing timing hook;
that is not used as performance evidence.

## Non-Claims

Goal1787 does not claim:

- true zero-copy;
- direct device-pointer partner ABI;
- broad PyTorch/CuPy acceleration;
- RT-core speedup;
- final v2.0 release readiness.

## Next Step

The next v2.0 slice should add phase timing around the partner handoff itself:

- descriptor validation;
- framework-to-host staging;
- packet packing;
- OptiX BVH/build/traversal;
- copyback.

After that, a larger pod run can decide whether direct device-pointer handoff is
worth starting before v2.0 or should remain a post-v2.0 optimization.

## Independent Review

- [Goal1788 Claude review](../reviews/goal1788_claude_review_goal1787_optix_partner_anyhit_host_stage_2026-05-12.md): `accept-with-boundary`
- [Goal1789 Gemini review](../reviews/goal1789_gemini_review_goal1787_optix_partner_anyhit_host_stage_2026-05-12.md): `accept-with-boundary`
- [Goal1790 3-AI consensus](../reviews/goal1790_3ai_consensus_goal1787_optix_partner_anyhit_host_stage_2026-05-12.md): `accept-with-boundary`

## Verdict

`accept-with-boundary`: the first OptiX partner-descriptor execution path works
for NumPy CPU, PyTorch CUDA, and CuPy CUDA columns through explicit host
staging. v2.0 remains blocked until phase timing, larger hardware evidence, and
final release consensus exist.
