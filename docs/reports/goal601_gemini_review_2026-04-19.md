# Goal601 Gemini Review: Apple RT Full-Surface Performance Characterization

Date: 2026-04-19
Verdict: **ACCEPT**

The performance characterization for Apple RT in v0.9.2 is accurate, fair, and honestly distinguishes between native hardware-backed execution and CPU-reference compatibility paths.

### Key Observations

- **Honest Separation:** The characterization explicitly labels workloads as either `native_mps_rt` (hardware-backed) or `cpu_reference_compat` (API compatibility). The script `scripts/goal601_apple_rt_full_surface_perf.py` correctly enforces this distinction.
- **Fair Comparison:** The interpretation sections in both the Goal 601 report and the v0.9.2 release documentation (e.g., `support_matrix.md`) clearly warn that compatibility timings must not be used as evidence of Apple RT hardware speed.
- **Accurate Context:** The report correctly identifies that while all 18 RTDL predicates are now callable through the `run_apple_rt` entry point, only a subset (3D closest-hit, 3D hit-count, and 2D segment-intersection) currently utilizes native Apple Silicon RT acceleration.
- **Evidence-Based:** The results are consistent with the "overhead-characterization" nature of the Goal 601 fixture. The characterization correctly refers users to the scaled Goal 600/595 artifacts for public-facing performance wording.
- **Governance:** The release documentation explicitly lists "Disallowed public wording," preventing misleading claims about broad speedups or general superiority over Embree at this stage.

The Characterization is fit for the v0.9.2 release candidate.
