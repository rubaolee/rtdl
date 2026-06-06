# Goal3554 Contact-Manifold Phase Probe On A5000

Date: 2026-06-06

## Purpose

Goal3553 made `contact_manifold_optix_aabb_broadphase_collect_k` the apparent weakest row in the full 11-row packet at `0.846x`. Goal3554 checks whether that is a stable AABB traversal regression or a phase/measurement artifact.

Artifacts:

- `docs/reports/goal3554_contact_manifold_probe_a5000/`
- `docs/reports/goal3554_contact_manifold_probe_repeat_a5000/summary.json`

Hardware:

- NVIDIA RTX A5000
- Driver 580.126.09

## Probe Design

The probe reruns the same contact-manifold contract on the same dataset shape used by Goal3553:

- dataset: `grid`
- grid count: `4096`
- witness capacity: `4096`
- discovery backend: `optix`
- discovery row capacity: `8192`
- discovery warmup: `2`
- discovery repeat: `800`

It alternates v2.3 and v2.8 for three trials and records:

- prepared AABB broadphase median time;
- `collect_k_bounded_rows` time;
- prepare time.

## Result

| Phase | v2.3 median | v2.8 median | v2.8/v2.3 |
| --- | ---: | ---: | ---: |
| Prepared AABB broadphase row output | `0.023200494` | `0.023035823` | `1.007x` |
| `collect_k_bounded_rows` | `0.008786325` | `0.017767604` | `0.495x` |
| Prepare AABB index | `0.414543913` | `0.349915161` | `1.185x` |

## Interpretation

The Goal3553 contact-manifold full-packet row should not be treated as a stable AABB traversal regression. The repeated targeted probe shows the prepared AABB broadphase itself is essentially parity to slightly faster in v2.8.

The stable weakness is the generic bounded witness collection step:

- v2.3 `collect_k_bounded_rows`: `0.008786s`
- v2.8 `collect_k_bounded_rows`: `0.017768s`

That is about a `0.495x` ratio for this contact path. If we want to improve the contact-manifold app rather than just the published primary metric, the next target should be the generic bounded row collector.

## Boundary

This is diagnostic evidence only. It does not authorize public speedup, whole-app speedup, broad RT-core, zero-copy, paper-reproduction, release, or package-install claims.

## Next Engineering Target

Investigate the v2.8 generic `collect_k_bounded_rows` path for small fixed-width int64 rows:

- compare the v2.3 and v2.8 Python/runtime implementations;
- identify added validation, conversion, allocation, or sorting overhead;
- preserve the app-agnostic bounded row contract;
- optimize only the generic collector, not contact-manifold-specific logic;
- rerun this same contact probe after any change.
