# Goal1799: Partner Any-Hit Public Dispatch

Status: `accept-with-boundary`

Date: 2026-05-12

## Context

Goals 1787 and 1795 proved backend-specific first-wave partner execution
bridges for 2-D ray/triangle any-hit:

- OptiX: `run_optix_partner_ray_triangle_any_hit_2d(...)`
- Embree: `run_embree_partner_ray_triangle_any_hit_2d(...)`

Goal1799 adds the learner-facing dispatch surface so users can call one partner
API and choose a backend explicitly.

## Public API

New calls:

```text
rt.partner.run_ray_triangle_any_hit_2d(ray_columns, triangle_columns, backend="embree")
rt.run_partner_ray_triangle_any_hit_2d(ray_columns, triangle_columns, backend="embree")
```

Supported first-wave backends:

```text
embree
optix
```

The default is `embree`, because the local CPU RT path is the reliable fallback
for learner/developer workflows and does not require NVIDIA RT hardware.

## Claim Boundary

The dispatcher does not add a native ABI. It only routes to the existing
app-agnostic backend bridges. The returned backend result still reports:

```text
transfer_mode = "host_stage"
true_zero_copy_authorized = False
rt_core_speedup_claim_authorized = False
```

Goal1799 does not claim true zero-copy, direct device-pointer handoff, RT-core
speedup, whole-app acceleration, or v2.0 release readiness.

## Validation

Windows command:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal1799_partner_anyhit_public_dispatch_test \
  tests.goal1795_embree_partner_anyhit_host_stage_test \
  tests.goal1793_mixed_partner_columns_conformance_test \
  tests.goal1791_partner_handoff_phase_timing_test \
  tests.goal1787_optix_partner_anyhit_host_stage_test
```

Result:

```text
18 tests ran.
9 passed.
9 skipped.
py_compile passed for the touched Python files.
```

The skips are expected on Windows because this environment lacks local PyTorch,
CuPy, and OptiX for the companion backend tests.

Linux command:

```text
PYTHONPATH=.partner_site:src:. python3 -m unittest \
  tests.goal1799_partner_anyhit_public_dispatch_test \
  tests.goal1795_embree_partner_anyhit_host_stage_test \
  tests.goal1793_mixed_partner_columns_conformance_test \
  tests.goal1791_partner_handoff_phase_timing_test \
  tests.goal1787_optix_partner_anyhit_host_stage_test
```

Result on `192.168.1.20` after rebuilding both Embree and OptiX:

```text
18 tests ran.
18 passed.
0 skipped.
```

## Independent Review

- [Goal1800 Gemini review](../reviews/goal1800_gemini_review_goal1799_partner_anyhit_public_dispatch_2026-05-12.md): `accept-with-boundary`

## Verdict

`accept-with-boundary`: the first v2.0 partner any-hit bridge now has a stable
public dispatch surface with Embree as the default CPU RT fallback and OptiX as
an explicit backend, while preserving the host-stage and no-overclaim boundary.
