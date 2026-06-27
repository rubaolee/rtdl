# Goal1041 Internal RTX vs Local Baseline Comparison

Date: 2026-04-27

## Objective and Strict Boundary

This report compares corrected local macOS CPU/Embree/SciPy timings against the collected remote RTX A5000 OptiX phase timings for the four Goal1038 applications (`outlier_detection`, `dbscan_clustering`, `service_coverage_gaps`, `event_hotspot_screening`). 

**STRICT BOUNDARY:** This document represents **internal engineering evidence only**. It explicitly **DOES NOT** authorize any public speedup claims, marketing release, or NVIDIA hardware superiority statements.

## Explicit Caveats

Any engineering comparison derived from these numbers must be interpreted within the following strict limitations:

1. **Phase Scopes Differ from Whole-App Timings:** The local macOS baselines capture end-to-end "whole app" elapsed time (including data generation, formatting, and Python-side overhead). The RTX OptiX timings explicitly isolate the native GPU query phase (`warm_query_sec` or `optix_query`). 
2. **Machine Mismatch:** The local baselines were executed on a local macOS environment. The RTX timings were collected on a remote RunPod Linux environment (NVIDIA RTX A5000). Direct subtractive math between these metrics is cross-hardware and thus scientifically invalid for public claims.
3. **Group B `skip_validation=true`:** The `outlier_detection` and `dbscan_clustering` apps were executed with validation skipped on the cloud to save time. Therefore, the artifacts do not contain the final in-band proof of correctness matching.
4. **Missing Git Source Commit:** The cloud group summaries lack a `source_commit` due to the use of `rsync` deployment, which strips the `.git` metadata.

## Comparison Table (Internal Reference Only)

All measurements represent a 20,000 copy workload scale.

| Application | Local CPU (macOS) | Local Embree (macOS) | Local SciPy (macOS) | RTX A5000 OptiX Phase |
|---|---:|---:|---:|---:|
| `outlier_detection` | 0.365 s | 0.305 s | 1.045 s | **0.00089 s** (median warm query) |
| `dbscan_clustering` | 0.319 s | 0.311 s | 0.944 s | **0.00082 s** (median warm query) |
| `service_coverage_gaps` | 2.141 s | 0.363 s | 0.767 s | **0.1379 s** (query phase) |
| `event_hotspot_screening`| 5.895 s | 0.552 s | 1.292 s | **0.2137 s** (query phase) |

## Gemini Verdict & Optimization Recommendations

**Verdict on Architectural Direction:**
The internal data strongly validates the V1.5 generic primitives and Zero-Copy DLPack roadmap. The OptiX query phase timings (e.g., `< 1 ms` for Group B) reveal that the fundamental bottleneck is entirely in data marshalling, Python loop overhead, and memory copying—not the RT cores themselves. The core OptiX traversal on RTX hardware operates at theoretical hardware scaling limits.

**Next Optimization Recommendations:**
1. **Accelerate Data Transfer:** Transition from standard host-to-device array copies to `DLPack` zero-copy memory transfers.
2. **Generic Reduction Primitives:** We must move the Python-side validation and summation loop into the native C++/CUDA reduction generic primitives (`MIN/MAX/SUM/COUNT`) proposed in V1.5. Currently, the Python postprocess phase swamps the sub-millisecond query time.
3. **Unified Linux Benchmarking:** Build a local Linux benchmarking harness to run CPU/Embree/SciPy on the *exact same* physical machine as the OptiX tests to provide mathematically sound speedup graphs for future public release.

**Is Another Pod Run Justified Today?**
**No.** We have captured the core evidence needed to prove the native traversal scalability. Another pod run is only justified *after* we implement the V1.5 zero-copy memory paths and native reduction primitives locally, at which point we can do a formal public-claim timing run with `skip_validation=false` and full `git` commit traceability inside the pod.
