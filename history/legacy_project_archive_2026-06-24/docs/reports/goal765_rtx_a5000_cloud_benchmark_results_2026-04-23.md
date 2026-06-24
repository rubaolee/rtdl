# Goal 765: RTX A5000 Cloud Benchmark Results

Date: 2026-04-23

## Verdict

`RTX_CLOUD_RUN_COMPLETE_WITH_BOUNDED_CLAIMS`

The restarted RunPod RTX A5000 pod successfully ran the Goal761/Goal762 RTX cloud benchmark pipeline after replacing the floating OptiX 9.1 headers with driver-compatible OptiX 9.0 headers from NVIDIA's `optix-dev` `v9.0.0` tag.

This is the first RTX-class cloud evidence for the selected RTDL OptiX app paths. It does not by itself authorize broad public speedup claims because the results still need independent review and explicit baseline comparison.

## Environment

- Cloud provider: RunPod
- SSH target: `n8tpfheut85rz1-64411542@ssh.runpod.io`
- GPU: `NVIDIA RTX A5000`
- Driver: `580.126.09`
- GPU memory: `24564 MiB`
- CUDA toolkit: `/usr/local/cuda`
- NVCC: `/usr/local/cuda/bin/nvcc`
- NVCC version: `Cuda compilation tools, release 12.4, V12.4.131`
- OptiX headers: `/root/vendor/optix-dev-9.0.0`
- OptiX header version: `OPTIX_VERSION 90000`
- OptiX ABI version: `OPTIX_ABI_VERSION 105`
- RTDL branch: `codex/rtx-cloud-run-2026-04-22`
- RTDL commit: `e74c54e89e3548627b69b24a73d36870b7b6d08e`

## Bootstrap Result

Goal763 passed after installing OptiX 9.0 headers:

| Gate | Result |
|---|---:|
| `nvidia-smi` detects RTX A5000 | OK |
| CUDA headers present | OK |
| `nvcc` present | OK |
| OptiX 9.0 headers present | OK |
| `make build-optix` | OK |
| Focused native OptiX tests | 24 tests OK |

The previous blocker was real: the public floating `optix-dev` mirror currently points at OptiX 9.1 (`OPTIX_ABI_VERSION 118`), which requires an R590+ driver. This pod uses R580, so OptiX 9.0 headers are the correct target.

## Benchmark Results

All five Goal759 manifest entries completed successfully under Goal761, and Goal762 reported `Status: ok`.

| App | RTX path | Scale | Native/prepared warm query median | Other major phase | Current bounded interpretation |
|---|---|---:|---:|---:|---|
| `database_analytics` | prepared DB session, sales risk | 120k rows | 0.137131 s | prepare total 0.818879 s | Prepared-session reuse is strong; still not a SQL/DBMS or broad RT-core speedup claim. |
| `database_analytics` | prepared DB session, regional dashboard | 140k rows | 0.204094 s | prepare total 1.046027 s | Prepared-session reuse is strong; Python/result materialization and exact filtering remain in scope for optimization. |
| `outlier_detection` | prepared fixed-radius threshold summary | 160k points | 0.490954 s | postprocess median 0.137718 s | Valid RTDL OptiX prepared-summary evidence; not a whole anomaly-system speedup claim. |
| `dbscan_clustering` | prepared fixed-radius core flags | 160k points | 0.482424 s | postprocess median 0.137738 s | Valid core-flag traversal evidence; Python DBSCAN expansion remains outside the native claim. |
| `robot_collision_screening` | prepared ray/triangle pose flags | 200k poses, 800k edge rays, 2048 obstacle triangles | 0.240423 s | input construction 3.038428 s; prepare scene 0.942048 s; prepare rays 1.893762 s | Strong flagship candidate for RT traversal; app-level timing is dominated by Python input/ray-buffer construction. |

## Important Fix During The Run

The original robot cloud command accidentally included full CPU oracle validation for `200000` poses. That made the benchmark CPU-bound and not useful as a clean RTX timing. After Goal763 focused correctness passed, the manifest was corrected to add `--skip-validation` for the robot performance run.

Committed fix:

- `e74c54e89e3548627b69b24a73d36870b7b6d08e`
- Commit message: `Skip robot oracle during RTX cloud timing`

## Artifacts

- `/Users/rl2025/rtdl_python_only/docs/reports/goal763_rtx_cloud_bootstrap_check_runpod_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal761_rtx_cloud_run_all_summary_runpod_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal762_rtx_cloud_artifact_report_runpod_2026-04-23.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal762_rtx_cloud_artifact_report_runpod_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal759_db_sales_risk_rtx.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal759_db_regional_dashboard_rtx.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal759_outlier_dbscan_fixed_radius_rtx.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal759_robot_pose_flags_phase_rtx.json`

## Claim Boundary

Allowed internal statement:

RTDL's selected OptiX app paths build and run on real RTX-class hardware with native OptiX focused tests passing and benchmark artifacts generated successfully.

Not allowed yet:

- Broad "RTDL apps are faster on RTX" claim.
- SQL/database-system performance claim.
- Full DBSCAN clustering speedup claim.
- Whole robot collision application speedup claim.
- Claim that Python input construction, postprocess, or validation are accelerated by RT cores.

## Next Engineering Conclusions

1. Robot collision is the best NVIDIA flagship candidate because the native prepared pose-flag warm query is `0.240423 s` for `800000` edge rays, while Python construction and ray-buffer preparation dominate total time.
2. The next robot optimization target is not OptiX traversal; it is moving pose/ray-buffer construction out of Python into native packed buffers or reusable generated poses.
3. DB prepared-session reuse is valuable, but broad performance claims need direct baselines against CPU/Embree/PostgreSQL-style alternatives with phase separation.
4. Fixed-radius outlier/DBSCAN summary paths now have real RTX run evidence, but postprocess and full app semantics remain outside the native traversal claim.
