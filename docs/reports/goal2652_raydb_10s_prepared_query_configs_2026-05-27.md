# Goal2652 RayDB 10s Prepared Query Config Comparison

Status: internal evidence only. Public speedup wording remains unauthorized pending review.

## Purpose

Short prepared-query runs can be noisy because the OptiX query phase is
sub-millisecond. This run uses a duration-driven protocol: after table
descriptor, workload, scene/payload, and ray-batch preparation are complete, the
runner repeats the prepared query until measured query time reaches about 10
seconds per mode/configuration.

This is the cleanest current way to compare steady-state prepared query
throughput.

## Configurations

- `embree_host`: Python + RTDL + Embree, host packed rays.
- `optix_host`: Python + RTDL + OptiX, host packed rays uploaded/prepared once.
- `optix_torch`: Python + Torch partner + RTDL + OptiX, Torch CUDA ray columns
  packed into a prepared generic ray batch.

All configurations use the same app-owned RayDB lowering, same generated
2,000,000-row fixture, same triangle encoding, same ray encoding, same primitive
group ids, same primitive payload values, same grouped reduction contract, and
same CPU correctness oracle.

## Pod Evidence

- Pod: `root@194.68.245.16 -p 22072`
- GPU: NVIDIA RTX A5000, driver `565.57.01`
- Script: `scripts/goal2646_raydb_prepared_payload_perf_pod.py`
- Common arguments:
  - `--fixture-kind generated`
  - `--generated-rows 2000000`
  - `--generated-groups 128`
  - `--generated-revenue-mod 64`
  - `--modes count,sum`
  - `--warmup 5`
  - `--target-query-seconds 10`

Artifacts:

- `docs/reports/goal2652_raydb_10s_embree_host_2m_2026-05-27.json`
- `docs/reports/goal2652_raydb_10s_embree_host_2m_2026-05-27.md`
- `docs/reports/goal2652_raydb_10s_optix_host_2m_2026-05-27.json`
- `docs/reports/goal2652_raydb_10s_optix_host_2m_2026-05-27.md`
- `docs/reports/goal2652_raydb_10s_optix_torch_2m_2026-05-27.json`
- `docs/reports/goal2652_raydb_10s_optix_torch_2m_2026-05-27.md`

## Results

| config | mode | measured iterations | query total s | query median ms | query mean ms | queries/s | prepare rays ms | partner ray cols ms | correct |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| embree_host | count | 2,062 | 10.002 | 4.7154 | 4.8505 | 206.2 | 0.023 | 0.000 | yes |
| embree_host | sum | 104 | 10.077 | 98.5329 | 96.8945 | 10.3 | 0.012 | 0.000 | yes |
| optix_host | count | 56,418 | 10.000 | 0.1704 | 0.1772 | 5,641.8 | 1.765 | 0.000 | yes |
| optix_host | sum | 10,499 | 10.000 | 0.9476 | 0.9525 | 1,049.9 | 115.330 | 0.000 | yes |
| optix_torch | count | 53,248 | 10.000 | 0.1798 | 0.1878 | 5,324.7 | 7.704 | 1,672.460 | yes |
| optix_torch | sum | 10,392 | 10.001 | 0.9560 | 0.9624 | 1,039.1 | 22.964 | 2.537 | yes |

## Interpretation

- For steady-state prepared queries, `optix_host` beats `embree_host` by:
  - 27.7x for `count`;
  - 104.0x for `sum`.
- `optix_torch` has nearly identical prepared-query throughput to
  `optix_host`; this is expected because both use the same prepared OptiX RT
  kernel after ray-batch preparation.
- Torch helps setup for large ray batches: in `sum`, prepared ray-batch setup is
  about 23.0 ms with Torch columns vs 115.3 ms with host rays.
- Torch hurts or obscures small cases if cold start is included: in `count`, the
  first Torch partner-column build paid about 1.67 s.

## Fairness Boundary

The fair Embree-vs-RT claim is:

> For the same app-owned RayDB lowering and same generic RTDL grouped
> ray/triangle reduction contract, steady-state prepared OptiX RT queries are
> much faster than steady-state prepared Embree queries on this 2M-row generated
> fixture.

The unfair claim would be:

> Whole-app RayDB speedup is 27x-104x.

That is not supported because setup remains significant: table descriptor,
workload buffer construction, scene/GAS build, payload preparation, and ray
batch preparation are outside the prepared-query timing row.

## Partner Boundary

The primary RT-vs-Embree comparison should use `embree_host` vs `optix_host`
because neither uses Torch/CuPy as an app partner. `optix_torch` should be
reported separately as a Python + partner + RTDL path. It is useful for reducing
large ray-batch preparation, not for changing the already-prepared RT query
kernel.
