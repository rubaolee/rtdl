# Goal3786 Current Benchmark Adequacy After HIPRT Closeout

Status: implemented locally.

## Purpose

Goal3786 refreshes the current benchmark adequacy source of truth after the
v2.10 HIPRT parity closeout. Goal3822 then layers in the Goal3818-3820
benchmark front-door hardening without changing the HIPRT closeout boundary.
Together they reconcile three facts that must stay separate:

- the ten benchmark apps have current Numba/reference coverage or primitive-only
  promoted routes, and no app is waiting on a Numba reference;
- the ten benchmark apps are now ready for actual AMD HIPRT functional pod
  validation, but no AMD hardware evidence exists yet.
- the ten benchmark apps have current executable benchmark-front-door evidence
  after Goal3818, with RTNN promoted from plan/evidence mode to an executable
  prepared OptiX app mode and triangle counting documented with explicit native
  mode for route-selection timing.

The source of truth remains:

`src/rtdsl/v2_9_benchmark_adequacy.py`

The current version string is:

`rtdl.v2_10.benchmark_adequacy_after_goal3820.v2`

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
| `rtnn` | adequate | promoted path is executable through `prepared_optix_ranked_summary` | ready for AMD functional pod; Goal3784 artifact pending |
| `triangle_counting` | adequate | promoted path is primitive-only; explicit native mode avoids the slow auto fallback for current timing probes | ready for AMD functional pod; Goal3784 artifact pending |

## Interpretation

Goal3786 itself did not improve any benchmark performance number. It removed a
stale planning mismatch: previous adequacy wording still said several apps
needed HIPRT mappings, but Goals3763-3785 have already supplied the generic
HIPRT contracts and the fail-closed AMD runner.

Goal3822 is also not a release claim. It updates the same source of truth after
the current benchmark-front-door pass:

- Goal3818 records a bounded A5000 smoke command for all ten promoted benchmark
  apps and repairs the Hausdorff/contact command contracts.
- Goal3819 records that triangle counting should use explicit
  `--optix-graph-mode native` for the current native timing route; it still
  reports no RT-core triangle-count authorization.
- Goal3820 adds the executable RTNN
  `--mode prepared_optix_ranked_summary` app front door with A5000 JSON evidence
  at 4096 and 65536 points.

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
