# V4.0 Clean-Commit Rerun Protocol

Status: reproducibility protocol, not release authorization

This protocol turns the V4.0 release-candidate evidence from a one-time POD
snapshot into a repeatable clean-commit validation route.

## Inputs

- branch: `codex/v4-tier2-section8`
- required native dependency: OptiX headers at `/root/vendor/optix-dev`
- required GPU dependency: CUDA-capable NVIDIA GPU with Torch CUDA available
- required local command runner: Python 3.11 or compatible

## Local No-CUDA Gate

From a clean checkout:

```bash
py -3 -m unittest \
  tests.v4_catalog_regression_gate_test \
  tests.v4_fixed_radius_device_array_api_test \
  tests.v4_fixed_radius_docs_and_example_test \
  tests.v4_frontdoor_test \
  tests.v4_operator_catalog_test \
  tests.v4_ray_triangle_device_array_api_test \
  tests.v4_release_candidate_packet_test \
  tests.v4_scope_gate_test \
  tests.v4_section8_any_hit_flags_device_frontdoor_validation_test \
  tests.v4_section8_closest_hit_grouped_argmin_device_frontdoor_validation_test \
  tests.v4_section8_device_array_frontdoor_validation_test \
  tests.v4_section8_fixed_radius_count_threshold_validation_test \
  tests.v4_section8_route_d_reference_validation_test \
  tests.v4_tier3_numba_ptx_probe_test \
  tests.v4_tier3_optix_module_link_probe_test
```

Expected result:

- 15 modules
- 55 tests
- status: OK

## Scope Gate

```bash
python scripts/v4_scope_gate.py \
  --json-out future/v4/evidence/v4_scope_gate_2026-06-24.json \
  --md-out future/v4/v4_0_scope_gate.md
```

Expected result:

- validation status: `passed`
- `release_authorized: false`
- `cupy_performance_claim_authorized: false`
- `non_python_host_binding_claim_authorized: false`

## POD GPU Gate

From the POD repository root:

```bash
git fetch origin codex/v4-tier2-section8
COMMIT=$(git rev-parse FETCH_HEAD)
WT=/root/rtdl_v4_section8/worktrees/v4_final_validation_YYYYMMDD_HHMM
git worktree add --detach "$WT" "$COMMIT"
cd "$WT"
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY="$PWD/build/librtdl_optix.so"
export RTDL_OPTIX_LIB="$PWD/build/librtdl_optix.so"
export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}
python scripts/v4_catalog_regression_gate.py \
  --mode gpu \
  --copies 32768 \
  --ray-count 32768 \
  --json-out future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_32768_2026-06-24.json \
  --md-out future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_32768_2026-06-24.md
```

Optional smoke rerun:

```bash
python scripts/v4_catalog_regression_gate.py \
  --mode gpu \
  --copies 8192 \
  --ray-count 8192 \
  --json-out future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_2026-06-24.json \
  --md-out future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_2026-06-24.md
```

Expected GPU result:

- status: `passed`
- mode: `gpu`
- git commit matches the selected clean commit
- native library points inside the fresh worktree
- three measured Tier-2 examples pass with `correctness_passed: true`
- Tier-2 planner returns `tier2_measured_ready`
- scalar callback returns `tier3_spike_only_not_v4_0_release_surface`
- complex callback returns `rejected_action_shaped_callback_deferred`
- release, broad speedup, CuPy performance, non-Python host binding, Tier-3,
  and app-specific native-kernel authorization flags remain false

## Non-Authorization

Passing this protocol does not authorize V4 release, broad V4 speedup wording,
whole-application speedup wording, Tier-3 callback/PTX support claims, raw OptiX
callback support, CuPy performance claims, embedding/C-ABI claims, non-Python
host binding claims, or app-specific native engine kernels.
