# Goal1795: Embree Partner Any-Hit Host-Stage Execution

Status: `accept-with-boundary`

Date: 2026-05-12

## Context

Goal1787 added the first OptiX partner execution bridge. Goal1795 adds the same
first-wave host-stage partner boundary for Embree, giving the v2.0 Python+partner
surface a CPU RT fallback for the same 2-D ray/triangle any-hit count shape.

## Implementation

Changed files:

- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/__init__.py`
- `tests/goal1795_embree_partner_anyhit_host_stage_test.py`

New public helpers:

```text
pack_embree_ray_triangle_any_hit_2d_partner_inputs(ray_columns, triangle_columns)
run_embree_partner_ray_triangle_any_hit_2d(ray_columns, triangle_columns)
```

The column schema matches Goal1787:

```text
rays: ids, ox, oy, dx, dy, tmax
triangles: ids, x0, y0, x1, y1, x2, y2
```

Each column is validated through `RtdlTensorDescriptor`, explicitly host-staged,
packed into existing Embree-compatible `PackedRays` / `PackedTriangles`, and run
through the existing app-agnostic Embree `ray_triangle_any_hit` primitive. The
same helper accepts NumPy CPU, PyTorch CUDA, and CuPy CUDA columns; CUDA partner
columns are copied back to host before Embree execution.

## Claim Boundary

Goal1795 does not add a native ABI and does not introduce partner vocabulary into
native engine symbols. It does not claim:

- true zero-copy;
- direct device-pointer partner ABI;
- RT-core speedup;
- whole-app acceleration;
- final v2.0 readiness.

The helper reports `transfer_mode = "host_stage"` and keeps
`true_zero_copy_authorized = False`.

## Validation

Windows command:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal1795_embree_partner_anyhit_host_stage_test \
  tests.goal1793_mixed_partner_columns_conformance_test \
  tests.goal1791_partner_handoff_phase_timing_test \
  tests.goal1787_optix_partner_anyhit_host_stage_test
```

Result:

```text
14 tests ran.
6 passed.
8 skipped.
py_compile passed for the touched Python files.
```

The skips are expected on Windows because this environment lacks local PyTorch,
CuPy, and OptiX for the companion partner tests.

Linux command:

```text
PYTHONPATH=.partner_site:src:. python3 -m unittest \
  tests.goal1795_embree_partner_anyhit_host_stage_test \
  tests.goal1793_mixed_partner_columns_conformance_test \
  tests.goal1791_partner_handoff_phase_timing_test \
  tests.goal1787_optix_partner_anyhit_host_stage_test
```

Result:

```text
14 tests ran.
14 passed.
0 skipped.
```

Tiny-fixture Embree output sample:

```json
{
  "backend": "embree",
  "hit_count": 1,
  "partner_phase_timings_s": {
    "descriptor_validation": 0.00028238643426448107,
    "framework_to_host_staging": 0.000006219022907316685,
    "packet_packing": 0.00008441193494945765,
    "embree_anyhit_count": 0.015332907903939486
  },
  "partner_tensor_handoff_authorized": true,
  "ray_count": 2,
  "row_count": 2,
  "rt_core_speedup_claim_authorized": false,
  "source_devices": ["cpu:0"],
  "source_protocols": ["numpy"],
  "transfer_mode": "host_stage",
  "triangle_count": 1,
  "true_zero_copy_authorized": false
}
```

This sample validates the shape and availability of the Embree partner bridge.
It is not performance evidence because the fixture is intentionally tiny.

## Independent Review

- [Goal1796 Claude review](../reviews/goal1796_claude_review_goal1795_embree_partner_anyhit_host_stage_2026-05-12.md): `accept-with-boundary`
- [Goal1798 Gemini review](../reviews/goal1798_gemini_review_goal1795_embree_partner_anyhit_host_stage_2026-05-12.md): `accept`
- [Goal1797 3-AI consensus](../reviews/goal1797_3ai_consensus_goal1795_embree_partner_anyhit_host_stage_2026-05-12.md): `accept-with-boundary`

## Verdict

`accept-with-boundary`: Embree now has a matching first-wave partner host-stage
any-hit bridge for the same Python+partner column contract as OptiX, while the
native engine boundary remains app-agnostic.
