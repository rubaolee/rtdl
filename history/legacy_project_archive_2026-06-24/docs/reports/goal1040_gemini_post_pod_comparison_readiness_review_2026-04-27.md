# Goal1040 Gemini Post-Pod Comparison-Readiness Review

Date: 2026-04-27

## Objective

Perform a strict post-pod comparison-readiness review for the four Goal1038 apps (`outlier_detection`, `dbscan_clustering`, `service_coverage_gaps`, `event_hotspot_screening`) against corrected local baselines. This review assesses whether the artifacts have sufficient phase separation, repeated-run data, correctness parity, hardware metadata, and source traceability. It explicitly handles caveats related to testing configurations and source control context in the cloud environment.

## Criteria Check

- **Phase Separation:** 
  - *Group B* (`goal1038_group_b_fixed_radius_refresh.json` / `goal759_outlier_dbscan_fixed_radius_rtx.json`) clearly segregates timings: `prepared_optix_pack_points_sec`, `prepared_optix_prepare_sec`, `prepared_optix_warm_query_sec`, and `prepared_optix_postprocess_sec`.
  - *Group D* (`goal811_service_coverage_rtx.json`, `goal811_event_hotspot_rtx.json`) isolates `input_build`, `optix_prepare`, `optix_query`, and `python_postprocess`. Both groups successfully segregate the native GPU execution from Python I/O and setup overhead.
- **Repeated-Run Data:** 
  - *Group B* artifacts natively utilized 10 iterations (`--iterations 10`) producing reliable median, min, and max sec arrays for the warm query.
  - *Group D* artifacts provide execution timings specifically bound to the 20000 copies scale context.
- **Correctness Parity:** 
  - *Group D* explicitly captures deterministic result shapes (`clinic_count=60000`, `covered_household_count=60000`, `hotspot_count=99999`) matching the local oracle expectations.
  - *Group B* output sets claim `matches_oracle=true`.
- **Hardware Metadata:** Properly and explicitly recorded (GPU: NVIDIA RTX A5000, 24564 MiB VRAM; Driver: 580.126.09; CUDA: 13.0).

## Explicit Caveat Handling

### 1. Missing Git Source Commit in Group Summaries
- **Observation:** Group summaries report `fatal: not a git repository...` for `source_commit` due to the cloud pod directory being synced via `rsync` without the `.git` folder to prevent I/O timeouts.
- **Handling:** This breaks the cryptographic traceability back to a Git tree hash. For internal architectural comparisons, we **accept** this caveat because the exact hardware metadata, timing boundaries, and script behavior strongly correlate to the `0a869d7` commit snapshot synced from `codex/rtx-cloud-run-2026-04-22`. However, it severely violates strict data provenance requirements for public release.

### 2. Fixed-Radius Used `skip_validation=true`
- **Observation:** The `goal757_optix_fixed_radius_prepared_perf` suite was executed with `--skip-validation` to minimize execution time on the cloud node. The reported `oracle_outlier_count` and `oracle_core_count` are null.
- **Handling:** The execution correctly isolated the raw OptiX kernel timings. Because local gating goals exhaustively verified correctness on the CPU/Embree side prior to pod execution, the raw timing evidence is valid for our internal performance comparison. But it lacks self-contained, on-device proof of correctness matching.

## Verdicts

### Verdict 1: Ready to Compare Internally
**Status:** `ACCEPT`

**Reasoning:** The phase separation securely captures the OptiX GPU query times without Python overhead contamination. The workloads run on standard 20,000 copy instances matching the local CPU/Embree baselines exactly. The captured timing evidence is mature, deterministic, and isolated enough to be cross-referenced internally for architectural and engineering validation.

### Verdict 2: Ready for Public Speedup Wording
**Status:** `BLOCK`

**Reasoning:** The strict RTDL external claim boundary strictly forbids public speedup claims without full in-band correctness validation (`skip_validation=false`) and absolute cryptographic traceability (`source_commit`). These artifacts lack the `.git` index provenance, and the skipped validation in Group B means the final artifacts do not contain absolute end-to-end proof of parity. Direct formalized comparative timings against local CPU baselines have also not yet been reviewed and signed off by two AIs.

**No public speedup claims, marketing distributions, or NVIDIA superiority statements are authorized.**
