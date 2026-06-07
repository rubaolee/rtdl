# Goal3784 AMD HIPRT Functional Validation Runbook

Status: implemented and validated on the current NVIDIA pod as a runbook/gate;
actual AMD pod evidence pending.

## Purpose

Goal3784 turns the Goal3783 NVIDIA CUDA/Orochi HIPRT closeout into a concrete
AMD-functional validation contract. The current implementation phase is closed:
all ten promoted benchmark lanes have app-agnostic HIPRT generic contracts.
The next hardware question is narrower and stricter:

Can those contracts build and pass on actual AMD hardware?

## Current Position

The machine-readable parity map reports `10 / 10` promoted benchmark apps at
`ready_for_amd_functional_pod`:

| App | AMD functional state |
| --- | --- |
| `hausdorff_xhd` | ready for AMD functional pod |
| `spatial_rayjoin` | ready for AMD functional pod |
| `rt_dbscan` | ready for AMD functional pod |
| `robot_collision` | ready for AMD functional pod |
| `contact_manifold` | ready for AMD functional pod |
| `raydb_style` | ready for AMD functional pod |
| `barnes_hut` | ready for AMD functional pod |
| `librts_spatial_index` | ready for AMD functional pod |
| `rtnn` | ready for AMD functional pod |
| `triangle_counting` | ready for AMD functional pod |

Goal3783 proves this implementation shape on the NVIDIA CUDA/Orochi HIPRT
route. That evidence is useful implementation evidence, but it is not AMD
hardware evidence. Goal3784 therefore defines a separate artifact contract:

`docs/reports/goal3784_amd_hiprt_functional_pod_validation.json`

## Machine Gate

The runbook is exposed by:

`src/rtdsl/v2_10_amd_hiprt_functional_validation.py`

It records:

- the required AMD hardware vendor;
- the exact focused test module list;
- the required artifact fields;
- the ten ready apps expected in the artifact;
- the required stage counts;
- the fail-closed claim boundary.

The validator deliberately rejects the Goal3783 A5000 closeout artifact as AMD
evidence because that artifact identifies an NVIDIA GPU and says it is not AMD
hardware evidence.

## AMD Pod Acceptance

An accepted AMD functional artifact must satisfy all of the following:

- `hardware_vendor` is `amd`;
- `focused_tests_passed` is `true`;
- every ready app is present in `functional_results_by_app` with value `pass`;
- `stage_counts.ready_for_amd_functional_pod` is `10`;
- `stage_counts.needs_generic_hiprt_extension` is `0`;
- `stage_counts.compatibility_only_not_amd_perf_ready` is `0`;
- `parity_validation.status` is `accept`;
- `scoped_source_dirty` is `false`;
- every claim-boundary flag remains `false`.

## Boundary

Goal3784 does not authorize AMD performance claims, public speedup wording,
whole-app acceleration wording, broad RT-core wording, paper-reproduction
claims, release claims, zero-copy claims, or app-specific native-engine logic.

It authorizes only one future operation: when actual AMD hardware is available,
run the focused HIPRT parity suite and save the resulting functional artifact
under the path above.

## Validation

Local validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3784_amd_hiprt_functional_validation_runbook_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test tests.goal3783_v2_10_hiprt_parity_closeout_packet_test
```

Clean pod validation of the runbook/gate:

- SSH target used: `root@69.30.85.203 -p 22057`.
- Clean checkout workdir: `/root/rtdl_goal3783_clean_1780855862`.
- Source commit: `f8b316d9`.
- Python: `3.12.3`.
- Command:
  `PYTHONPATH=src:. python3 -m unittest tests.goal3784_amd_hiprt_functional_validation_runbook_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test tests.goal3783_v2_10_hiprt_parity_closeout_packet_test`.
- Result: `Ran 23 tests`, `OK`.

This pod validation proves the runbook and fail-closed gate are executable. It
does not change the AMD evidence status, because the pod is still NVIDIA
hardware.
