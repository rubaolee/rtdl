# Goal2651 RayDB Reusable Table Descriptor Optimization

Status: internal evidence only. Public speedup wording remains unauthorized pending review.

## Goal

Reduce RayDB non-RT overhead without adding RayDB-specific logic to the RTDL
native engines. The optimization is useful for both OptiX and Embree because it
acts before backend dispatch: app-owned dense predicate/group encoding is
prepared once and reused across query modes.

## Implementation

- Added `prepare_paper_rt_encoded_table_descriptor(...)` in the RayDB benchmark
  app.
- The descriptor computes once:
  - dense scan-field encodings;
  - mixed-radix `Z` scan coordinate;
  - predicate-matching scan values;
  - dense group ids and group tuples.
- `_make_paper_rt_encoded_packed_workload(...)` now accepts the descriptor and
  builds only mode-specific typed buffers: triangles, primitive group ids,
  primitive values, and rays.
- `scripts/goal2646_raydb_prepared_payload_perf_pod.py` now reuses the table
  descriptor across modes by default. `--no-reuse-table-descriptor` preserves
  the old behavior.

The descriptor is explicitly app-owned. RTDL native code still sees only
generic typed rays, triangles, primitive group ids, primitive values, and a
grouped integer reduction.

## Pod Evidence

- Pod: `root@194.68.245.16 -p 22072`
- GPU: NVIDIA RTX A5000, driver `565.57.01`
- Workload: generated deterministic RayDB-style fixture, 2,000,000 rows,
  128 groups, revenue mod 64, one copy.
- Script: `scripts/goal2646_raydb_prepared_payload_perf_pod.py`
- New artifacts:
  - `docs/reports/goal2651_raydb_generated_prepared_optix_host_2m_table_descriptor_2026-05-27.json`
  - `docs/reports/goal2651_raydb_generated_prepared_optix_host_2m_table_descriptor_2026-05-27.md`
  - `docs/reports/goal2651_raydb_generated_prepared_embree_host_2m_table_descriptor_2026-05-27.json`
  - `docs/reports/goal2651_raydb_generated_prepared_embree_host_2m_table_descriptor_2026-05-27.md`
  - `docs/reports/goal2651_raydb_generated_prepared_optix_torch_2m_table_descriptor_2026-05-27.json`
  - `docs/reports/goal2651_raydb_generated_prepared_optix_torch_2m_table_descriptor_2026-05-27.md`

## Host-Ray Prepared Path

| backend | mode | table descriptor s | workload build s | scene/payload s | prepare rays s | query median s | traversal first sample s | RT core |
|---|---|---:|---:|---:|---:|---:|---:|---|
| OptiX before descriptor | count | 0.000000 | 0.530997 | 0.487608 | 0.001732 | 0.000227 | 0.000120 | yes |
| OptiX after descriptor | count | 0.396689 | 0.188318 | 0.504034 | 0.002062 | 0.000213 | 0.000105 | yes |
| OptiX before descriptor | sum | 0.000000 | 0.866114 | 0.117259 | 0.127545 | 0.001155 | 0.000979 | yes |
| OptiX after descriptor | sum | 0.396689 | 0.494867 | 0.130941 | 0.111320 | 0.001064 | 0.000961 | yes |
| Embree before descriptor | count | 0.000000 | 0.500848 | 0.431815 | 0.000010 | 0.006101 | 0.006275 | no |
| Embree after descriptor | count | 0.325410 | 0.179431 | 0.391984 | 0.000008 | 0.005668 | 0.004389 | no |
| Embree before descriptor | sum | 0.000000 | 0.753227 | 0.426226 | 0.000046 | 0.095588 | 0.094187 | no |
| Embree after descriptor | sum | 0.325410 | 0.457015 | 0.463319 | 0.000020 | 0.096972 | 0.096886 | no |

## Interpretation

- Mode-specific workload build improved:
  - OptiX `count`: 2.82x less mode-specific build time.
  - OptiX `sum`: 1.75x less mode-specific build time.
  - Embree `count`: 2.79x less mode-specific build time.
  - Embree `sum`: 1.65x less mode-specific build time.
- The descriptor cost is now visible and paid once per fixture/table descriptor:
  about 0.33-0.40 s in this pod run.
- For a single query mode, total setup is similar because work moved from
  `workload_build_sec` to `table_descriptor_prepare_sec`.
- For multi-query sessions over the same table/predicate/grouping, this is a
  real reduction because the descriptor is reused across modes.
- Prepared query speed remains dominated by backend traversal:
  - OptiX vs Embree after descriptor: 26.6x faster for `count`.
  - OptiX vs Embree after descriptor: 91.2x faster for `sum`.

## Partner-Ray Path

The Torch partner-ray run shows why partner-owned query columns are useful but
must be treated as session-level state:

| mode | table descriptor s | workload build s | partner ray cols s | prepare rays s | query median s |
|---|---:|---:|---:|---:|---:|
| count | 0.339143 | 0.175832 | 2.609264 | 0.005353 | 0.000212 |
| sum | 0.339143 | 0.596869 | 0.002408 | 0.026442 | 0.001074 |

The first Torch mode paid cold-start/import/CUDA initialization. After that,
the `sum` partner-ray path reduced ray preparation from about 111 ms on host
rays to about 26 ms, but this should not yet be claimed as a broad speedup.

## Boundary

This optimization does not claim whole-app speedup. It narrows the next known
bottleneck: table/query-buffer ownership. RT traversal is already fast; the
remaining work is to make descriptor, triangle, payload, and ray buffers more
persistently partner-owned across repeated queries.

## Next Engineering Target

The next clean step is a reusable app-level prepared RayDB session object:

- prepare the table descriptor once;
- prepare one or more mode-specific scenes/payloads once;
- prepare host or partner ray batches once per query shape;
- run many query repetitions without rebuilding Python dictionaries or dense
  encodings;
- keep native engines app-agnostic.
