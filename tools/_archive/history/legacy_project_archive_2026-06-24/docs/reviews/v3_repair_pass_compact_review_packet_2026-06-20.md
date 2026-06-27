# V3 Repair Pass 1 Compact Review Packet

Date: 2026-06-20.

Purpose: give an external reviewer enough context to audit V3 Repair Pass 1
without reading the full repository.

## Current Decision

```text
V3 should continue.
V3 is not release-authorized.
```

## User Requirement

V3 must solve the V2.x user problem as a Python-hosted independent RTDL
language surface:

- users should not have to write a custom C++/CUDA/OptiX engine for every app;
- users should know which backend/partner route to choose;
- performance claims must be backed by serious pod artifacts;
- docs/tutorials must not send users into old historical material.

## Current Evidence

Pod:

- GPU: NVIDIA RTX 4000 Ada Generation.
- Driver: `550.127.05`.
- V2.x baseline: `v2.14`, commit
  `8384a38376567fe518d89721453eb4433de08312`.

Initial V2.14 comparison artifact:

```text
docs/rebuild/v3/evidence/v2_14_vs_v3_rebuild_non_numba_serious_20260620_051207
```

Repair Pass 1 current-side artifacts:

```text
docs/rebuild/v3/evidence/v3_current_goal2626_clean_env_20260620_055523
docs/rebuild/v3/evidence/v3_current_goal2636_full_clean_20260620_060726
docs/rebuild/v3/evidence/v3_current_goal3828_full_clean_20260620_060412
docs/rebuild/v3/evidence/v3_gpu_python_env_gate_script_20260620_062113
```

Clean current-side results:

| Suite | Result |
| --- | ---: |
| `goal2626_standard_all_rows` | 22 ok / 0 failed |
| `goal2636_standard_all_rows` | 28 ok / 0 failed |
| `goal3828_full_clean` | 10 pass / 0 fail |
| GPU Python environment gate | pass |

Current-side representative OptiX-over-Embree signals:

| Row | Signal |
| --- | ---: |
| `rt_dbscan` standard compact signature | 1599.914x |
| `spatial_rayjoin` overlay strengthened row | 5419.291x |
| `spatial_rayjoin` LSI strengthened row | 365.448x |
| `raydb_style` grouped count | 277.838x |
| `triangle_counting` 20k cliques strengthened row | 114.229x |
| `robot_collision` prepared collision flags | 5.099x |
| `librts_spatial_index` standard row | 0.065x, not an OptiX speedup claim |
| `spatial_rayjoin` standard all-workload row | 0.034x, runs but not an OptiX speedup claim |

V3-over-V2.14 boundary:

- Current V3 does not prove broad raw speed over V2.14 across every shared row.
- The strongest V3-over-V2.14 claim is route health and runability, especially
  triangle-counting OptiX rows that pass in current V3 where matching v2.14 rows
  fail.

## Current Docs Added Or Updated

```text
README.md
docs/rebuild/v3/README.md
docs/rebuild/v3/v3_current_status_2026-06-20.md
docs/rebuild/v3/v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md
docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json
docs/rebuild/v3/v3_gpu_environment_gate_2026-06-20.md
docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
tutorials/current/*.md
scripts/v3_gpu_python_env_gate.py
```

## Current App Classification

| App | Classification |
| --- | --- |
| `hausdorff_xhd` | release-candidate row set |
| `spatial_rayjoin` | split-route release candidate |
| `rt_dbscan` | release-candidate row set |
| `robot_collision` | release-candidate row set |
| `raydb_style` | release-candidate with dependency gate |
| `barnes_hut` | release-candidate row set |
| `librts_spatial_index` | no OptiX speed claim |
| `rtnn` | mixed release candidate |
| `triangle_counting` | release-candidate row set |
| `contact_manifold` | release-candidate row set |

All public claim flags remain false.

## GPU Environment Gate

Reusable checker:

```bash
PYTHONPATH=src:. python scripts/v3_gpu_python_env_gate.py --pretty
```

Gate checks:

- CuPy RawKernel: pass.
- Torch CUDA tensor: pass.
- Numba CUDA JIT: pass.

Package set:

```text
cupy-cuda12x==14.1.1
torch==2.6.0+cu124
numba==0.65.1
nvidia-cuda-nvcc-cu12==12.4.131
nvidia-cuda-nvrtc-cu12==12.9.86
nvidia-cuda-runtime-cu12==12.9.79
```

Caveat: `cuda-bindings` warns that it was built for CUDA major 13 while the
driver supports CUDA 12. Rows pass, but setup docs keep the warning visible.

## Current Tests

```text
py -3 scripts\run_test_matrix.py --group v3_rebuild
```

Latest result: 19 tests OK.

```text
py -3 scripts\rtdl_source_tree_doctor.py --json --run-smoke
```

Latest result: required checks pass; local optional CUDA/OptiX/CuPy/Numba
warnings remain on Windows.

## Current Release Blockers

P0 blockers recorded in
`docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`:

1. external review not accepted;
2. public docs not fully rebuilt;
3. release wording gate missing;
4. setup install path not packaged;
5. second-machine confirmation not done.

## Review Questions

Please review critically:

1. Verdict: `accept-as-repair-base`, `accept-with-P0`, or `reject`.
2. Does Repair Pass 1 justify continuing V3 rather than deleting/restarting it?
3. Does anything overclaim release readiness, V3-over-V2.x speed, broad RT-core
   acceleration, or automatic backend/partner choice?
4. Are the app classifications conservative enough?
5. Is the GPU environment gate sufficiently reproducible?
6. What P0 fixes are required before public release authorization?
7. What test or doc gate is missing?

Do not authorize release unless the current evidence and docs truly justify it.
