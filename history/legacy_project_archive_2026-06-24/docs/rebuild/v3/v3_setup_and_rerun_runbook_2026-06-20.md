# V3 Setup And Rerun Runbook

Status: Phoenix V3 current rerun contract for the redo_required runtime surface.

This runbook is the current entry point for reproducing the Phoenix V3 evidence
surface. It is intentionally explicit because dependency drift was one of the
V3 failure sources.

## Current Phoenix Rerun Contract

Run these gates in order:

1. Local source-tree sanity on the checkout you are reviewing.
2. Linux native backend build for Embree and OptiX.
3. Python GPU partner gate for CuPy, PyTorch CUDA, and Numba CUDA.
4. Runtime/language benchmark reruns into fresh artifact directories.
5. Claim classification against the Phoenix row authority.
6. Install/reproducibility classification gate.
7. Secondary-platform classification gate.
8. Next generic-engine work queue gate.
9. Major-version performance mandate gate.
10. Aggregate Phoenix release-readiness gate.

The row-level authority is:

```text
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json
```

The app-level boundary map is:

```text
docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json
```

The wording gate is:

```bash
PYTHONPATH=src:. python scripts/v3_release_wording_gate.py --pretty
```

Expected current wording-gate reading:

- `status: pass`;
- `gate_level: final_public_surface_claim_boundary_gate`;
- `final_public_surface_gate: true`;
- `missing_expected_m7_row_ids: []`;
- `release_authorized: false`;
- `public_speedup_claim_authorized: false`.

The aggregate readiness gate is:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_release_readiness_gate.py --pretty
```

The major-version performance mandate gate is:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_major_performance_mandate_gate.py --pretty
```

Expected current major-performance reading:

- `status: redo_required`;
- `release_authorized: false`;
- `broad_v3_faster_than_v2_claim_authorized: false`;
- `broad_v2x_performance_not_proven`;
- `serious_all_app_paired_evidence_failed_release_bar`;
- `current_scoped_13_row_surface_not_v3_major_release`.

The secondary-platform gate is:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_secondary_platform_gate.py --pretty
```

The install/reproducibility gate is:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_install_reproducibility_gate.py --pretty
```

Expected current install/reproducibility reading:

- `status: staged_pod_gate_present_general_release_installer_not_ready`;
- `staged_gpu_pod_gate_available: true`;
- `release_scope: source_tree_pod_gated_thirteen_row`;
- `general_release_installer_ready: false`;
- `package_install_claim_authorized: false`;
- `source_tree_pod_gated_scoped_release_wording_reviewed: true`;
- `source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true`;
- `aggregate_13_row_installer_scope_review_required: false`;
- `installer_closes_release_blocker: true`;
- `installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row`;
- `release_authorized: false`.

The current release surface is now 13 rows, and the thirteen-row installer
scope extension is reviewed. The reviewed extension packet is:

```text
Phoenix M7-qualified release rows: 13
docs/rebuild/v3/v3_source_tree_pod_gated_thirteen_row_scope_extension_candidate_2026-06-22.md
```

Expected current release-readiness evidence keeps:

- `aggregate_13_row_installer_scope_review_required: false`;
- `current_installer_closure_scope: source_tree_pod_gated_thirteen_row`;
- `proposed_installer_closure_scope: source_tree_pod_gated_thirteen_row`;
- `thirteen_row_scope_extension_reviewed: true`.

The next generic-engine work queue gate is:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_next_engine_work_queue.py --pretty
```

Expected current next-engine reading:

- `status: generic_engine_work_queue_closed_not_release`;
- `existing_evidence_promotable_now: false`;
- `current_m7_qualified_release_rows: 13`;
- `base_m7_packet_rows: 12`;
- `supplemental_m7_rows_from_current_queue: 1`;
- `A 1.01x-style result cannot qualify`;
- closed generic-engine work includes `grouped_reduction_prepare_amortization`
  with two exact device-column M7 rows added;
- closed generic-engine work also includes `contact_aabb_prepare_reuse` with
  two exact AABB native query-handle M7 rows added;
- closed generic-engine work also includes `rtnn_ranked_summary_wall_path` with
  one exact prepared repeat50 M7 row added;
- closed generic-engine work also includes
  `barnes_hut_fused_partner_vector_accumulation` with one exact amended
  fused-partner M7 row added;
- closed generic-engine work also includes
  `spatial_squared_boundary_default_path_topology_stream` with one bounded
  default-path `point_location_topology_stream` supplemental M7 row added;
- active queue ids are empty;
- future research records include `barnes_hut_vector_accumulation_frontier_shape`;
- future research records no longer include
  `spatial_rayjoin_topology_stream_author_gap`, because the default-path
  guarded squared-boundary row is now counted as exactly one bounded
  supplemental release-surface row. This still does not authorize release,
  public speedup, RTDL-beats-RayJoin, true-zero-copy, or broad V3-over-V2
  wording.

Expected current secondary-platform reading:

- `status: compatibility_confirmed_hardware_scope_waiver_reviewed_not_release`;
- `secondary_compatibility_confirmed: true`;
- `secondary_rt_performance_confirmation_authorized: false`;
- `secondary_rt_hardware_scope_waiver_reviewed: true`;
- `secondary_platform_closes_release_blocker: true`;
- `secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver`;
- `secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod`;
- `multi_gpu_performance_portability_claim_authorized: false`.

For an attempted release decision, use strict mode:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_release_readiness_gate.py --strict-release
```

Expected current reading:

- readiness `status: redo_required`;
- `release_authorized: false`;
- `public_speedup_claim_authorized: false`;
- `broad_v3_faster_than_v2_claim_authorized: false`;
- blocking reasons include `broad_v2x_performance_not_proven`,
  `serious_all_app_paired_evidence_failed_release_bar`, and
  `current_scoped_13_row_surface_not_v3_major_release`.

## Local Source-Tree Sanity

From the repository root:

```powershell
py -3 scripts\run_test_matrix.py --group v3_rebuild
py -3 scripts\rtdl_source_tree_doctor.py --json --run-smoke
```

Expected:

- `v3_rebuild` passes;
- required doctor checks pass;
- local Windows may warn about optional CUDA/OptiX/CuPy/Numba components.

## Linux GPU Native Libraries

The 2026-06-20 pod used:

```text
GPU: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
OptiX SDK headers: /workspace/vendor/optix-dev-8.0.0/include/optix.h
```

Native libraries:

```bash
make build-embree
make build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0
```

Required runtime variables:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/path/to/current/build/librtdl_optix.so
export RTDL_OPTIX_LIB=$RTDL_OPTIX_LIBRARY
export RTDL_EMBREE_LIBRARY=/path/to/current/build/librtdl_embree.so
```

## Python GPU Partner Gate

The current Phoenix GPU partner gate uses this package set:

```text
cupy-cuda12x==14.1.1
torch==2.6.0+cu124
numba==0.65.1
nvidia-cuda-nvcc-cu12==12.4.131
nvidia-cuda-nvrtc-cu12==12.9.86
nvidia-cuda-runtime-cu12==12.9.79
```

Staged installer for the tested pod-style environment:

```bash
bash scripts/v3_install_gpu_pod_env.sh --accept-experimental-pod-gate
```

This script installs PyTorch first from the cu124 index, then installs the
CuPy/Numba/CUDA-wheel set required by the repaired pod run, then executes the
GPU environment gate. It is not a general release installer, and passing it is
not release authorization.

Numba compiler path:

```bash
export NUMBA_CUDA_PREFIX=/path/to/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc
export CUDA_HOME=$NUMBA_CUDA_PREFIX
export CUDA_PATH=$NUMBA_CUDA_PREFIX
export PATH=$NUMBA_CUDA_PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$NUMBA_CUDA_PREFIX/nvvm/lib64:/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:${LD_LIBRARY_PATH:-}
```

Verify:

```bash
PYTHONPATH=src:. python scripts/v3_gpu_python_env_gate.py --pretty
```

Expected:

- `cupy_rawkernel`: pass;
- `torch_cuda`: pass;
- `numba_cuda_jit`: pass.

Known warning:

```text
cuda-bindings was built for CUDA major version 13, but the NVIDIA driver only
supports up to CUDA 12.
```

The current Phoenix pod rows passed despite this warning. Keep the warning
visible until the dependency set is quieter.

## Benchmark Reruns

Use separate artifact directories and keep raw summaries.

```bash
PYTHONPATH=src:. python scripts/goal2626_benchmark_embree_optix_baseline.py \
  --scale standard \
  --artifact-dir /tmp/v3_goal2626_standard \
  --case-repeat 1 \
  --timeout-sec 900

PYTHONPATH=src:. python scripts/goal2636_strengthen_benchmark_rows.py \
  --tier standard \
  --artifact-dir /tmp/v3_goal2636_standard \
  --case-repeat 1 \
  --timeout-sec 1200

PYTHONPATH=src:. python scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --output-dir /tmp/v3_goal3828_scale \
  --output-json /tmp/v3_goal3828_scale/summary.json \
  --heartbeat-sec 30 \
  --materialize-rayjoin-public-cdb
```

Compare results against:

```text
docs/rebuild/v3/evidence/v3_current_goal2626_clean_env_20260620_055523
docs/rebuild/v3/evidence/v3_current_goal2636_full_clean_20260620_060726
docs/rebuild/v3/evidence/v3_current_goal3828_full_clean_20260620_060412
```

After benchmark reruns, do not infer app-level release readiness from raw
speedups. Rebuild or inspect the classification artifacts instead:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_m7_row_classification_packet.py
PYTHONPATH=src:. python scripts/v3_release_wording_gate.py --pretty
PYTHONPATH=src:. python scripts/v3_phoenix_install_reproducibility_gate.py --pretty
PYTHONPATH=src:. python scripts/v3_phoenix_secondary_platform_gate.py --pretty
PYTHONPATH=src:. python scripts/v3_phoenix_next_engine_work_queue.py --pretty
PYTHONPATH=src:. python scripts/v3_phoenix_release_readiness_gate.py --pretty
```

Rows may be promoted only when the Phoenix row authority records an exact
row-scoped M7 qualification with row-level evidence, public wording, and 2-AI
review. App-level speedups, hot-path-only speedups, paper-like names, or
backend names are not enough.

## Release Rule

Passing this runbook is not a release by itself. It is a prerequisite for
release review. Public wording must still be checked against:

```text
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json
docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json
docs/rebuild/v3/v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md
```

If those sources disagree, the Phoenix M7 row classification packet wins for
row qualification, and the wording gate must fail until the disagreement is
removed.

The aggregate readiness gate is the current release control surface. Its
expected current status is `blocked_not_release`. A real release attempt must
run `scripts/v3_phoenix_release_readiness_gate.py --strict-release`; with the
current thirteen-row evidence surface, strict mode must exit nonzero.

The secondary-platform strategy is documented at:

```text
docs/rebuild/v3/v3_secondary_platform_strategy_2026-06-21.md
```

`lx1` / `192.168.1.20` is accepted as compatibility evidence only. The recorded
GPU is `NVIDIA GeForce GTX 1070`; it does not provide RT-core performance
confirmation for public V3 speed claims.

The install/reproducibility strategy is documented at:

```text
docs/rebuild/v3/v3_install_reproducibility_strategy_2026-06-21.md
```

`scripts/v3_install_gpu_pod_env.sh` is a staged pod gate that requires
`--accept-experimental-pod-gate`. It reproduces the tested Python GPU package
set and then runs `scripts/v3_gpu_python_env_gate.py --pretty`; it is not a
general release installer.
