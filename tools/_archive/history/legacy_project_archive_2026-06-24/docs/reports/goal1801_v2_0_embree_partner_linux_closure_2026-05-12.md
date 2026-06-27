# Goal1801: v2.0 Embree Partner Linux Closure

Status: `accept-with-boundary`

Date: 2026-05-12

## Scope

This report closes the Embree side of the current v2.0 Python+partner+RTDL lane
on the local Linux validation host.

The closed Embree scope is:

- NumPy CPU partner descriptor support;
- PyTorch CUDA and CuPy CUDA partner descriptors accepted through explicit host
  staging into Embree;
- Embree CPU RT fallback for the first public partner primitive:
  2-D ray/triangle any-hit count;
- learner-facing public dispatch with Embree as the default backend:
  `rt.partner.run_ray_triangle_any_hit_2d(...)` and
  `rt.run_partner_ray_triangle_any_hit_2d(...)`;
- Linux validation from clean `origin/main`.

## Linux Environment

```text
host: 192.168.1.20
user: lestat
checkout: /home/lestat/work/rtdl_v2_partner_check
commit: a78c37f3
partner packages: /home/lestat/work/rtdl_v2_partner_check/.partner_site
torch: 2.5.1+cu121, CUDA available
cupy: 14.0.1, CUDA device count 1
numpy: 2.4.4
```

## Validation

From a clean checkout reset to `origin/main`:

```text
git fetch origin main
git reset --hard origin/main
make build-embree
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev
PYTHONPATH=.partner_site:src:. python3 -m unittest \
  tests.goal1799_partner_anyhit_public_dispatch_test \
  tests.goal1795_embree_partner_anyhit_host_stage_test \
  tests.goal1793_mixed_partner_columns_conformance_test \
  tests.goal1791_partner_handoff_phase_timing_test \
  tests.goal1787_optix_partner_anyhit_host_stage_test \
  tests.goal1781_real_framework_partner_availability_test \
  tests.goal1783_numpy_cpu_partner_adapter_test \
  tests.goal1777_v2_0_partner_protocol_baseline_test \
  tests.goal1675_partner_protocol_substrate_test
```

Result:

```text
40 tests ran.
40 passed.
0 skipped.
```

## Evidence Trail

- [Goal1783 NumPy CPU Partner Adapter](goal1783_numpy_cpu_partner_adapter_2026-05-12.md)
- [Goal1785 Linux PyTorch and CuPy Partner Validation](goal1785_linux_pytorch_cupy_partner_validation_2026-05-12.md)
- [Goal1795 Embree Partner Any-Hit Host-Stage Execution](goal1795_embree_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1797 3-AI Consensus for Goal1795](../reviews/goal1797_3ai_consensus_goal1795_embree_partner_anyhit_host_stage_2026-05-12.md)
- [Goal1799 Partner Any-Hit Public Dispatch](goal1799_partner_anyhit_public_dispatch_2026-05-12.md)
- [Goal1800 Gemini Review of Goal1799](../reviews/goal1800_gemini_review_goal1799_partner_anyhit_public_dispatch_2026-05-12.md)

## Claim Boundary

The Embree v2.0 lane is closed for the current first-wave partner primitive, but
the broader v2.0 release remains blocked.

Accepted claim:

```text
The local Linux validation host proves RTDL's first-wave Python+partner Embree
path: NumPy, PyTorch CUDA, and CuPy CUDA columns can run a 2-D ray/triangle
ANY_HIT count through explicit host staging into the app-agnostic Embree engine.
```

Non-claims:

- no true zero-copy;
- no direct device-pointer partner ABI;
- no RT-core speedup;
- no whole-app acceleration;
- no final v2.0 release readiness.

## Next Non-Embree Gates

The remaining v2.0 work is no longer blocked on Embree. The next gates are:

- OptiX partner evidence on hardware with real RT cores;
- realistic phase timing beyond tiny fixtures;
- decision on whether direct device-pointer handoff belongs in v2.0 or post-v2.0;
- final public docs/tutorial/example pass;
- final 3-AI release consensus.
