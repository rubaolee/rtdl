# Goal3786 Current Benchmark Adequacy After HIPRT Closeout

Status: implemented locally.

## Purpose

Goal3786 refreshes the current benchmark adequacy source of truth after the
v2.10 HIPRT parity closeout. It reconciles two facts that must stay separate:

- the ten benchmark apps have current Numba/reference coverage or primitive-only
  promoted routes, and no app is waiting on a Numba reference;
- the ten benchmark apps are now ready for actual AMD HIPRT functional pod
  validation, but no AMD hardware evidence exists yet.

The source of truth remains:

`src/rtdsl/v2_9_benchmark_adequacy.py`

The current version string is:

`rtdl.v2_10.benchmark_adequacy_after_goal3785.v1`

## Current Matrix

| Benchmark app | Adequacy | Partner/reference status | AMD/HIPRT status |
| --- | --- | --- | --- |
| `hausdorff_xhd` | adequate | Numba exact continuation reference exists; promoted RT path is primitive-first | ready for AMD functional pod; Goal3784 artifact pending |
| `spatial_rayjoin` | strong | no-RawKernel Numba topology reference exists; CuPy remains dense opponent | ready for AMD functional pod; Goal3784 artifact pending |
| `rt_dbscan` | strong | Numba prepared-repeat component continuation is measured | ready for AMD functional pod; Goal3784 artifact pending |
| `robot_collision` | strong | promoted path is primitive-only | ready for AMD functional pod; Goal3784 artifact pending |
| `contact_manifold` | adequate | promoted path is primitive-only | ready for AMD functional pod; Goal3784 artifact pending |
| `raydb_style` | adequate | promoted path is primitive-first grouped reduction | ready for AMD functional pod; Goal3784 artifact pending |
| `barnes_hut` | adequate | Numba exact-force block-reduction reference exists; CuPy remains faster overall | ready for AMD functional pod; Goal3784 artifact pending |
| `librts_spatial_index` | adequate | promoted path is primitive-only | ready for AMD functional pod; Goal3784 artifact pending |
| `rtnn` | adequate | promoted path is prepared primitive/aggregate | ready for AMD functional pod; Goal3784 artifact pending |
| `triangle_counting` | adequate | promoted path is primitive-only | ready for AMD functional pod; Goal3784 artifact pending |

## Interpretation

This refresh does not improve any benchmark performance number. It removes a
stale planning mismatch: previous adequacy wording still said several apps
needed HIPRT mappings, but Goals3763-3785 have already supplied the generic
HIPRT contracts and the fail-closed AMD runner.

The next hardware-dependent step is not more NVIDIA/Orochi proof. It is an
actual AMD functional pod run using the Goal3785 runner, producing:

`docs/reports/goal3784_amd_hiprt_functional_pod_validation.json`

## Boundary

Goal3786 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, true-zero-copy wording, automatic
partner selection, AMD performance wording, paper-reproduction wording, or
app-specific native-engine logic.

It is a consistency refresh for the benchmark adequacy and AMD/HIPRT readiness
story.
