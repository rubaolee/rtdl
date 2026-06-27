# Goal 507: Hausdorff Linux Large-Scale Performance

Date: 2026-04-17

Status: accepted by external AI review and Codex consensus

Version line: `v0.8` app-building performance evidence

## Purpose

Goal507 measures the paper-derived Hausdorff app on the canonical Linux host
using RTDL Embree, OptiX, and Vulkan backends, then compares the same two-pass
1-nearest-neighbor Hausdorff reduction against established nearest-neighbor
libraries.

## Baseline Libraries

The comparison libraries were selected from public/official documentation:

- SciPy `cKDTree.query`: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.cKDTree.query.html
- scikit-learn `NearestNeighbors`: https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestNeighbors.html
- FAISS `IndexFlatL2`: https://faiss.ai/

These are nearest-neighbor libraries, not Hausdorff-specific RT systems. The
comparison is therefore honest only at the app contract level: two directed
exact 1-NN passes plus a Python max reduction.

## Code Changes

- `/Users/rl2025/rtdl_python_only/examples/rtdl_hausdorff_distance_app.py`
  now exposes `optix` and `vulkan` in addition to `cpu_python_reference`, `cpu`,
  and `embree`.
- The app-level `matches_oracle` tolerance is now `1e-5`, which matches the
  float-approximate RT backend boundary. The earlier `1e-12` tolerance was too
  strict for OptiX/Vulkan float output.
- `/Users/rl2025/rtdl_python_only/scripts/goal507_hausdorff_linux_perf.py`
  adds a reproducible Linux benchmark harness.
- `/Users/rl2025/rtdl_python_only/tests/goal507_hausdorff_perf_harness_test.py`
  checks that the app exposes GPU backend choices and that the harness can run a
  tiny CPU case when numpy is available.

## Linux Environment

- Host: `lx1`
- Platform: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Python: `3.12.3`
- GPU/driver: `NVIDIA GeForce GTX 1070, 580.126.09`
- Embree: `(4, 3, 0)`
- OptiX: `(9, 0, 0)`
- Vulkan: `(0, 1, 0)`
- Python libraries: `{'faiss': '1.13.2', 'numpy': '2.4.4', 'scipy': '1.17.1', 'sklearn': '1.8.0'}`

Important hardware boundary: the GTX 1070 is a pre-RTX GPU with no NVIDIA RT
cores. These OptiX/Vulkan numbers test RTDL GPU backend paths on this host, not
hardware RT-core acceleration.

## Commands Run On Linux

Backend build/probe:

```text
make build-embree
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
PYTHONPATH=/home/lestat/work/rtdl_goal507_pydeps:src:. python3 - <<'PY'
import rtdsl as rt
print(rt.embree_version())
print(rt.optix_version())
print(rt.vulkan_version())
PY
```

Correctness smoke:

```text
PYTHONPATH=/home/lestat/work/rtdl_goal507_pydeps:src:. python3 examples/rtdl_hausdorff_distance_app.py --backend embree --copies 4
PYTHONPATH=/home/lestat/work/rtdl_goal507_pydeps:src:. python3 examples/rtdl_hausdorff_distance_app.py --backend optix --copies 4
PYTHONPATH=/home/lestat/work/rtdl_goal507_pydeps:src:. python3 examples/rtdl_hausdorff_distance_app.py --backend vulkan --copies 4
```

Result: all three reported `matches_oracle: true` after the app-level float
approximation tolerance fix.

Performance matrix:

```text
PYTHONPATH=/home/lestat/work/rtdl_goal507_pydeps:src:. python3 scripts/goal507_hausdorff_linux_perf.py --sizes 1000,5000,10000 --iterations 3 --backends embree,optix,vulkan --output docs/reports/goal507_hausdorff_linux_perf_raw_2026-04-17.json
PYTHONPATH=/home/lestat/work/rtdl_goal507_pydeps:src:. python3 scripts/goal507_hausdorff_linux_perf.py --sizes 20000 --iterations 1 --backends embree,optix,vulkan --output docs/reports/goal507_hausdorff_linux_perf_20k_raw_2026-04-17.json
```

Raw result files copied into this repo:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal507_hausdorff_linux_perf_raw_2026-04-17.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal507_hausdorff_linux_perf_20k_raw_2026-04-17.json`

## Results: 1k, 5k, 10k Per Side

| Points per side | Engine/library | Median sec | Correct vs reference | Hausdorff distance |
| ---: | --- | ---: | --- | ---: |
| 1000 | `rtdl_embree` | 0.112694 | True | 0.004043809016 |
| 1000 | `rtdl_optix` | 0.004199 | True | 0.004043782596 |
| 1000 | `rtdl_vulkan` | 0.008748 | True | 0.004043782596 |
| 1000 | `scipy_ckdtree` | 0.001827 | True | 0.004043782540 |
| 1000 | `sklearn_nearest_neighbors` | 0.003518 | True | 0.004043782540 |
| 1000 | `faiss_index_flat_l2` | 0.000821 | True | 0.004048614297 |
| 5000 | `rtdl_embree` | 2.837216 | True | 0.001856324263 |
| 5000 | `rtdl_optix` | 0.017398 | True | 0.001856352086 |
| 5000 | `rtdl_vulkan` | 0.021788 | True | 0.001856352086 |
| 5000 | `scipy_ckdtree` | 0.009148 | True | 0.001856352091 |
| 5000 | `sklearn_nearest_neighbors` | 0.014205 | True | 0.001856352091 |
| 5000 | `faiss_index_flat_l2` | 0.004445 | True | 0.001859319629 |
| 10000 | `rtdl_embree` | 11.465858 | True | 0.001299540505 |
| 10000 | `rtdl_optix` | 0.034364 | True | 0.001299524214 |
| 10000 | `rtdl_vulkan` | 0.039181 | True | 0.001299524098 |
| 10000 | `scipy_ckdtree` | 0.019025 | True | 0.001299524140 |
| 10000 | `sklearn_nearest_neighbors` | 0.028810 | True | 0.001299524140 |
| 10000 | `faiss_index_flat_l2` | 0.011657 | False | 0.001314737485 |

## Results: 20k Per Side

| Points per side | Engine/library | Median sec | Correct vs reference | Hausdorff distance |
| ---: | --- | ---: | --- | ---: |
| 20000 | `rtdl_embree` | 45.769132 | True | 0.000982673293 |
| 20000 | `rtdl_optix` | 0.654443 | True | 0.000982688041 |
| 20000 | `rtdl_vulkan` | 0.422478 | True | 0.000982688041 |
| 20000 | `scipy_ckdtree` | 0.271509 | True | 0.000982688115 |
| 20000 | `sklearn_nearest_neighbors` | 0.648797 | True | 0.000982688115 |
| 20000 | `faiss_index_flat_l2` | 0.058284 | True | 0.000976562500 |

## Readout

- Correctness: Embree, OptiX, Vulkan, SciPy, scikit-learn, and FAISS all matched
  the selected reference distance within the benchmark tolerance except FAISS at
  10k under the strict `1e-5` check. FAISS uses float32 flat L2 search here; its
  reported distance was still close and matched at 20k.
- RTDL GPU path: OptiX and Vulkan are much faster than Embree for this app on
  Linux. At 20k points per side, Embree took `45.769132 s`, OptiX took
  `0.654443 s`, and Vulkan took `0.422478 s`.
- External baselines: FAISS `IndexFlatL2` was the fastest measured option at all
  sizes in this exact 2D benchmark. SciPy `cKDTree` was also faster than RTDL
  OptiX/Vulkan at 20k on this host.
- Honest claim: RTDL has a working multi-backend Hausdorff app path and the GPU
  backends are credible relative to Embree, but this evidence does not show RTDL
  beating mature nearest-neighbor libraries for low-dimensional exact 1-NN on
  this GTX 1070 host.

## What This Means For v0.8

The v0.8 app-building story remains valid: RTDL can express the Hausdorff app as
existing `knn_rows(k=1)` row production plus Python reduction, and the same app
now runs on Embree, OptiX, and Vulkan. The performance story is bounded:

- claim: multi-backend RTDL execution works and scales to 20k points per side on
  Linux for this app;
- claim: OptiX/Vulkan strongly outperform RTDL Embree for this app on this host;
- do not claim: RTDL is faster than SciPy, scikit-learn, or FAISS for exact 2D
  nearest-neighbor Hausdorff distance;
- do not claim: RT-core acceleration, because the measured GPU is GTX 1070.

## Validation

Local validation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal507_hausdorff_perf_harness_test tests.goal208_nearest_neighbor_examples_test tests.goal505_v0_8_app_suite_test -v
Ran 12 tests in 0.753s
OK (skipped=1)
```

```text
PYTHONPATH=src:. python3 -m py_compile examples/rtdl_hausdorff_distance_app.py scripts/goal507_hausdorff_linux_perf.py tests/goal507_hausdorff_perf_harness_test.py
git diff --check
OK
```

The skipped local test requires numpy and is exercised by the Linux benchmark
environment where numpy is installed in `/home/lestat/work/rtdl_goal507_pydeps`.

## Verdict

Goal507 is accepted.

External AI reviews:

- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal507_claude_review_2026-04-17.md`
  - Verdict: PASS
  - Finding: all report table entries match the raw JSON, the GTX 1070
    non-RT-core boundary is disclosed, and the performance claims do not
    overstate RTDL relative to SciPy, scikit-learn, or FAISS.
- Gemini review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal507_gemini_review_2026-04-17.md`
  - Verdict: ACCEPT

Codex consensus:

- `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-17-codex-consensus-goal507-hausdorff-linux-perf.md`
