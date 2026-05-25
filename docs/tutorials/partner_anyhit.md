# Python Partner Any-Hit

This tutorial shows the first Python+partner+RTDL shape for the v2.x-facing
track.

Use this as the first partner tutorial before the OptiX-specific column path.

The idea is:

```text
partner-owned columns -> RTDL partner descriptor -> explicit host staging
-> app-agnostic ray/triangle ANY_HIT backend
```

Use Embree first. It is the CPU RT fallback and works on the local Linux
development host without a pod or hardware RT cores.

## Run It

From the repository root:

```bash
PYTHONPATH=src:. python examples/v2_0/partners/rtdl_partner_anyhit.py --partner numpy --backend embree
```

Expected shape:

```json
{
  "backend": "embree",
  "example": "rtdl_partner_anyhit",
  "hit_count": 1,
  "partner_input": "numpy",
  "ray_count": 2,
  "rt_core_speedup_claim_authorized": false,
  "source_devices": ["cpu:0"],
  "source_protocols": ["numpy"],
  "transfer_mode": "host_stage",
  "triangle_count": 1,
  "true_zero_copy_authorized": false
}
```

If PyTorch CUDA or CuPy CUDA is installed, the same example can use partner-owned
CUDA columns:

```bash
PYTHONPATH=src:. python examples/v2_0/partners/rtdl_partner_anyhit.py --partner torch-cuda --backend embree
PYTHONPATH=src:. python examples/v2_0/partners/rtdl_partner_anyhit.py --partner cupy-cuda --backend embree
```

Those runs still report `transfer_mode = "host_stage"` because Embree is a CPU
backend. Use the OptiX partner-column tutorial for the GPU device-column shape.

## The Code Shape

The example builds column dictionaries:

```python
rays = {
    "ids": ...,
    "ox": ...,
    "oy": ...,
    "dx": ...,
    "dy": ...,
    "tmax": ...,
}

triangles = {
    "ids": ...,
    "x0": ...,
    "y0": ...,
    "x1": ...,
    "y1": ...,
    "x2": ...,
    "y2": ...,
}
```

Then it calls:

```python
result = rt.run_partner_ray_triangle_any_hit_2d(
    rays,
    triangles,
    backend="embree",
)
```

You can also call the namespaced form:

```python
result = rt.partner.run_ray_triangle_any_hit_2d(
    rays,
    triangles,
    backend="embree",
)
```

## Why Embree First?

Embree is the CPU RT backend. It gives learners and developers a real native RT
path without needing NVIDIA hardware. That makes it the best local development
platform for the partner protocol and descriptor contract.

OptiX is selectable:

```bash
PYTHONPATH=src:. python examples/v2_0/partners/rtdl_partner_anyhit.py --partner numpy --backend optix
```

But selecting `backend="optix"` is not a public speedup claim. RT-core claims
require separate hardware evidence on a Turing-or-newer NVIDIA GPU and reviewed
phase timing.

## Boundaries

This bridge is deliberately conservative:

- partner frameworks stay in Python adapter code;
- the native engine remains app-agnostic;
- data moves through explicit host staging;
- `true_zero_copy_authorized` remains `false`;
- `rt_core_speedup_claim_authorized` remains `false`;
- timing fields show phase shape, not benchmark evidence;
- public speedup claims still require exact evidence and release-boundary review.

That boundary is what lets RTDL support partner frameworks without turning the
engine into a PyTorch-, CuPy-, or app-specific runtime.
