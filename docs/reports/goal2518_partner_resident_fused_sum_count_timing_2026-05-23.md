# Goal2518: Partner-Resident Fused `sum_count` Timing

## Purpose

Goal2517 changed the experimental partner-resident `avg_as_sum_count` execution
path from two native launches (`sum` plus `count`) to one generic fused
`sum_count` grouped reduction. Goal2518 measures that exact engineering effect
on a synthetic CUDA tensor fixture.

This is internal timing evidence only. It is not a public speedup claim.

## Method

- Build the OptiX backend on the repaired pod.
- Prepare one partner-resident CUDA tensor descriptor.
- Run the old two-launch path: grouped `sum`, grouped `count`, then Python
  boundary merge.
- Run the new one-launch path: grouped `sum_count`.
- Compare canonical `(region_id, sum, count)` rows for correctness.
- Report min/median/mean/max wall time over repeated synchronized CUDA calls.

## Environment Boundary

- Pod: `ssh root@213.173.108.13 -p 15902 -i ~/.ssh/id_ed25519`; actual local key
  used from this Mac: `~/.ssh/id_ed25519_rtdl_codex`.
- Driver: 550.127.05.
- CUDA toolkit: 12.8.
- CUDA compatibility package: `cuda-compat-12-8=570.211.01-0ubuntu1`.
- Required runtime library path:
  `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda/lib64:$LD_LIBRARY_PATH`.
- OptiX headers: NVIDIA `optix-dev` `v8.0.0`.

## Claim Boundary

- No native average ABI is added.
- No public speedup claim is authorized.
- No SQL, DBMS, authors-code, or full RayDB claim is authorized.
- No true zero-copy claim is authorized; compact grouped output is still
  materialized at the Python boundary.

## Evidence

- Pod timing runner:
  `scripts/goal2518_partner_resident_fused_sum_count_timing_pod.py`.
- Pod artifact:
  `docs/reports/goal2518_partner_resident_fused_sum_count_timing_pod_2026-05-23.json`.
- Observed fixture: 200,000 rows, 1,024 group capacity, 512 emitted groups,
  5 warmup iterations, 30 timed iterations.
- Correctness: fused rows match the two-launch `sum` plus `count` reference.
- Observed internal timing on this pod:
  - two-launch `sum` plus `count` mean: 4.8185 ms.
  - fused `sum_count` mean: 0.9602 ms.
  - internal mean ratio: 5.018x.
- Interpretation: this supports the engineering decision to fuse the composite
  grouped reduction for the partner-resident path. It still does not authorize
  public speedup wording because it is one synthetic subpath, not a reviewed
  whole-app or external-system benchmark.
