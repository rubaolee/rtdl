# Goal2199 Gemini Review: Goal2198 RayJoin Same-Query RTX Pod Runner

**Date:** 2026-05-17

**Reviewer:** Gemini

**Verdict:** accept-with-boundary

## Summary

This review assesses the `goal2198_rayjoin_same_query_pod_runner.sh` script and associated documentation (`goal2198_rayjoin_same_query_pod_runbook_2026-05-17.md`, `goal2195_rayjoin_query_exec_export_patch_plan_2026-05-17.md`, `goal2195_rayjoin_query_exec_export_patch_2026-05-17.diff`) against the provided review goals. The runner successfully integrates the RayJoin query-stream export with the RTDL same-query consumer, maintains clear separation of concerns between RayJoin and RTDL codebases, and provides adequate infrastructure for an RTX pod run. The claim boundaries are appropriately conservative. One concrete risk regarding `cupy` versioning is identified.

## Review Goals Assessment

### 1. Confirm the runner correctly connects Goal2195 RayJoin query-stream export to the Goal2192 RTDL same-query consumer.

**Assessment:** **Pass.**
The `scripts/goal2198_rayjoin_same_query_pod_runner.sh` orchestrates the entire flow:
- It applies the `goal2195_rayjoin_query_exec_export_patch_2026-05-17.diff` to the cloned RayJoin repository.
- The `run_rayjoin_query` function executes RayJoin's `query_exec` with the `-query_stream_output` flag, directing its query stream to a JSON file in the `OUT_DIR`.
- The `run_rtdl_same_stream` function then invokes `scripts/goal2192_rayjoin_same_query_stream_runner.py` using the generated RayJoin query stream as input.
- The `write_summary` embedded Python script in the runner explicitly checks that the `query_stream_producer` in the RTDL output is `rayjoin_query_exec_export_patch` and that `same_contract_with_rayjoin_query_exec` is `true`, confirming the intended connection.
The `tests/goal2198_rayjoin_same_query_pod_runner_test.py` also contains assertions verifying these connections.

### 2. Confirm it keeps RayJoin changes external to RTDL and does not add app-specific RTDL engine code.

**Assessment:** **Pass.**
The design correctly separates concerns:
- RayJoin-specific modifications (build compatibility fixes, query export patch) are applied directly to the cloned RayJoin repository (`RAYJOIN_DIR`) by the `apply_rayjoin_build_compatibility_fixes` and `apply_goal2195_export_patch` functions. These changes do not affect the RTDL codebase.
- The `scripts/goal2192_rayjoin_same_query_stream_runner.py` acts as a consumer of an *external* data format (the RayJoin-exported stream). It adapts RTDL's existing reference kernels (`rayjoin_point_location_positive_hits_reference`, `county_zip_join_reference`) to process this stream without introducing RayJoin-specific logic into the core RTDL engine or symbols.
The `goal2195_rayjoin_query_exec_export_patch_plan_2026-05-17.md` explicitly states this boundary.

### 3. Check whether progress logging, per-step timeout, CUDA/OptiX setup, RayJoin build fixes, and RTDL Embree/OptiX build steps are adequate for an RTX pod.

**Assessment:** **Pass.**
- **Progress Logging:** The `log()` and `run_step()` functions provide clear, timestamped logging to `progress.log` and individual step logs, which is crucial for monitoring and debugging on a pod.
- **Per-step Timeout:** The `STEP_TIMEOUT_SECONDS` variable and its application via `timeout --preserve-status` in `run_step` correctly implement per-step timeouts, preventing indefinite hangs.
- **CUDA/OptiX Setup:** The script includes robust auto-detection for `CUDA_PREFIX`, exports necessary CUDA environment variables (`CUDA_HOME`, `PATH`, `LD_LIBRARY_PATH`), and handles OptiX SDK installation by cloning a specific tag (`v8.0.0`) if headers are missing. `RTDL_OPTIX_PTX_ARCH` and `RTDL_OPTIX_PTX_COMPILER` are also correctly set.
- **RayJoin Build Fixes:** The `apply_rayjoin_build_compatibility_fixes` Python script applies targeted fixes to RayJoin's CMake configuration and source files (`markers.h`, `output_chain.h`) to ensure compatibility with modern CUDA/OptiX environments (e.g., `nvtx3/nvToolsExt.h`, specific `ENABLED_ARCHS`, `Goal2198Vec2Hash`/`Goal2198Vec2Equal` for `std::unordered_map` compatibility).
- **RTDL Embree/OptiX Build Steps:** The script uses established `make build-embree` and `make build-optix` commands within the RTDL directory, properly passing `OPTIX_PREFIX` and `CUDA_PREFIX`, which are standard and proven build processes for RTDL.
The unit tests also confirm the presence and configuration of these elements.

### 4. Confirm claim boundaries remain conservative: no RTDL-beats-RayJoin claim, no paper-scale claim, no broad RT-core claim, and no v2.0 release claim.

**Assessment:** **Pass.**
The claim boundaries are consistently conservative across all reviewed documents and scripts:
- The `write_summary` function in the runner script explicitly sets `paper_scale_perf_claim_authorized`, `rtdl_beats_rayjoin_claim_authorized`, `broad_rt_core_speedup_claim_authorized`, and `v2_0_release_authorized` to `False` in the `summary.json` output.
- The `goal2198_rayjoin_same_query_pod_runbook_2026-05-17.md` reiterates these conservative claims, explicitly stating that the runbook is "not evidence," "does not prove RTDL beats RayJoin," and "does not authorize a v2.0 release."
- The `goal2192_rayjoin_same_query_stream_runner.py` also propagates these `False` flags into its output payload.
Unit tests specifically check for these conservative assertions in the script and runbook.

### 5. Call out any concrete runner risk that should be fixed before using the next RTX pod.

**Concrete Runner Risk:**
The runner hardcodes the installation of `cupy-cuda12x` in the `install_python_dependencies` function. While `detect_cuda_prefix` attempts to find a compatible CUDA installation, there's no explicit check to ensure that the detected CUDA version (if not 12.x) is compatible with `cupy-cuda12x`. If an older CUDA version is present and detected, `cupy-cuda12x` might install but lead to runtime failures or incorrect behavior in RTDL's CUDA-accelerated Python components.

**Recommendation:**
Add a check in `install_python_dependencies` to verify that the `CUDA_PREFIX` detected is indeed a CUDA 12.x installation if `cupy-cuda12x` is to be installed. If not, either warn the user, skip the `cupy` installation, or attempt to install a `cupy` version compatible with the detected CUDA. For example:

```bash
# ... in install_python_dependencies
if [[ "${CUDA_PREFIX}" != *"/cuda-12"* ]]; then
  log "Warning: Detected CUDA_PREFIX (${CUDA_PREFIX}) is not CUDA 12.x, but installing cupy-cuda12x."
  # Consider adding logic here to install a different cupy version or error out
  # if strict version matching is desired.
fi
run_step pip_install_runtime "${PYTHON_BIN}" -m pip install numpy cupy-cuda12x
# ...
```

This ensures that the `cupy` installation is aligned with the detected CUDA environment, or at least provides an explicit warning.
