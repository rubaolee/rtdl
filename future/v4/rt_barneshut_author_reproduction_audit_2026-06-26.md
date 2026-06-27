# RT-BarnesHut Author Reproduction Audit

Date: 2026-06-26

Status: author source found, author artifact built and run on the NVIDIA POD; past RTDL code is not a full RT-BarnesHut paper reproduction; RTDL V2.14/V3.0.2/V4.0 Barnes-Hut-style routes were compared only within their existing RTDL contract.

## Bottom Line

Past RTDL code did **not** reproduce the full RT-BarnesHut paper program.

The existing RTDL Barnes-Hut benchmark is explicitly labeled as a reconstruction-style benchmark, not an authors-code comparison and not a full paper reproduction. I found, built, patched minimally, and ran the authors' RT-BarnesHut source on the NVIDIA POD. That gives us a real author reference, but RTDL's current V2/V3/V4 Barnes-Hut route is not yet same-semantics with the paper program, so direct speed division between RTDL and the authors' program is not authorized.

## Primary Sources Found

- Paper/artifact PDF: https://vtechworks.lib.vt.edu/server/api/core/bitstreams/a2ca3a26-04b8-4eea-a5d3-39c2df2802a0/content
- ACM DOI page: https://dl.acm.org/doi/10.1145/3710848.3710885
- Authors/source repository: https://github.com/vani-nag/OWLRayTracing
- Author branch used: `BarnesHutRT`
- Author commit used: `2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7`
- Dataset/artifact record: https://zenodo.org/records/14219911
- Treelogy dataset record: https://zenodo.org/records/14220233

The paper reports RT-BarnesHut against GPU Barnes-Hut baselines. The paper's Table 1 reports Treelogy vs RT-BarnesHut on synthetic 10M/25M/50M. Table 2 and Table 3 report ChaNGa vs RT-BarnesHut, including synthetic-25M.

## Past RTDL Code Audit

Current RTDL Barnes-Hut benchmark file:

`examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`

The file's own claim boundary says it is a research reconstruction instrument only:

- `paper_reproduction: False`
- `authors_code_comparison: False`
- `full_rt_barneshut_paper_reproduction: False`
- `This is not a full RT-BarnesHut paper reproduction, not an authors-code comparison`

Supporting tests also preserve that boundary, including:

- `tests/goal2530_barnes_hut_benchmark_app_promotion_test.py`
- `tests/goal2537_barnes_hut_pod_validation_and_authors_code_gate_test.py`
- `tests/goal2540_barnes_hut_benchmark_app_closeout_test.py`

Verdict: the repo already knew this was not a paper reproduction. Treating the existing RTDL Barnes-Hut route as if it were the authors' RT-BarnesHut program would be incorrect.

## Author Artifact Build

POD:

- Host: `root@194.68.245.170 -p 22089`
- GPU: NVIDIA RTX A5000
- Driver: 570.195.03
- Author checkout path on POD: `/root/external/RT-BarnesHut-author`
- Local checkout path: `external/RT-BarnesHut-author`
- Evidence path: `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/`

Build command used on POD:

```bash
cmake -S . -B build \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc \
  -DCMAKE_CUDA_ARCHITECTURES=86 \
  -DOptiX_ROOT_DIR=/workspace/vendor/optix-dev-8.0.0 \
  -DOptiX_INCLUDE=/workspace/vendor/optix-dev-8.0.0/include \
  -DOWL_BUILD_SAMPLES=ON \
  -DOWL_BUILD_ADVANCED_TESTS=OFF
cmake --build build --target rtbarneshut -j$(nproc)
```

Minimal compatibility patches:

1. Added `#include <array>` to `samples/cmdline/s01-rtbarneshut/hostCode.cu` for modern CUDA/GCC compilation.
2. Changed original hard-coded `gpuDeviceID = 1` to `gpuDeviceID = 0` because the POD has one visible GPU.

Patch evidence:

`future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/author_checkout_diff.txt`

No algorithm, force-law, timing, traversal, bucket, OptiX, or data semantics were changed.

## Author Artifact Runs on POD

All rows below are authors' `rtbarneshut` binary on the POD, not RTDL.

| Run | Dataset | Points | Paper comparator | POD preprocessing | POD RT force | POD execution | POD wall | Evidence |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| sanity | `treelogy_synthetic_1M.txt` | 1,000,000 | no paper table row | 0.491527s | 0.136000s | 0.639937s | 5.913498s | `author_1m_*` |
| Table 1 family | `treelogy_synthetic_10M.txt` | 10,000,000 | paper RT-BarnesHut 2.7s execution | 1.779950s | 1.018350s | 3.088180s | 25.369898s | `author_treelogy_10m_*` |
| Table 2/3 family | `synthetic25M.csv` | 25,000,000 | paper synthetic-25M: 1.0s total / 0.7s kernel | 1.593590s | 2.408880s | 4.571780s | 51.503901s | `author_synthetic25m_*` |

Interpretation:

- The author source builds and runs on the POD.
- The 10M Treelogy run is in the same broad range as the paper's Table 1 RT-BarnesHut 10M result, but not identical hardware.
- The synthetic25M CSV run is materially slower than the paper's reported synthetic-25M RT-BarnesHut row. This is not a validated paper-number reproduction yet. Likely contributors include different GPU generation/class (paper: RTX 4070 Ti; POD: RTX A5000), single-run/cold-run protocol, and artifact/runtime version differences. It is still the authors' code, not an RTDL route.

## RTDL V2.14/V3.0.2/V4.0 Barnes-Hut-Style Comparison

Evidence:

- `future/v4/evidence/v4_goal4736_barnes_hut_complete_workflow_focused_pod_2026-06-26.json`
- `future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json`

Focused POD protocol:

- Body count: 32,768
- Correctness body count: 2,048
- Repeats: 7
- Warmup: 2
- Partner: CuPy
- Contract: RTDL generated 2D aggregate-frontier weighted-vector workflow

| Version | Route | Hot seconds | Wall seconds | Hot vs V2.14 | Fair within RTDL contract? | Fair vs author RT-BarnesHut? |
|---|---|---:|---:|---:|---|---|
| V2.14 | `v2_14_optix_host_frontier_numba_cpu_continuation` | 31.579628 | 31.579628 | 1.000x | yes | no |
| V3.0.2 | `v3_0_2_device_columns_explicit_partner_continuation` | 0.112106 | 0.177090 | 281.694x | yes | no |
| V4.0 candidate | `v4_candidate_runner_explicit_partner_continuation` | 0.111799 | 0.154276 | 282.468x | yes | no |

The final matrix row records a similar V4/V2.14 hot speedup of 286.142x, with V4 approximately equal to V3 on hot path.

Interpretation:

- This is a real RTDL V2/V3/V4 comparison for the existing RTDL Barnes-Hut-style workflow.
- The speedup is mainly from removing V2.14 host-frontier materialization and keeping the continuation device/partner resident, a V3/Phoenix-style residency improvement carried into V4.
- It is **not** a speedup over the authors' RT-BarnesHut program.
- It is **not** proof that RTDL has reproduced the paper's full 3D RT-BarnesHut algorithm.

## Why the Comparison Is Not Same-Semantics Yet

Authors' RT-BarnesHut:

- 3D Barnes-Hut inputs from Treelogy/ChaNGa-style datasets.
- Barnes-Hut tree with bucket size 32 in the reported paper evaluation.
- Maps Barnes-Hut tree nodes to triangles and query bodies to rays.
- Uses RT traversal/opening logic for the Barnes-Hut force computation.
- Reports preprocessing and RT force-computation phases.

Current RTDL Barnes-Hut-style route:

- Generated 2D bodies in the RTDL benchmark harness.
- Generic aggregate/opening/frontier workflow.
- Partner continuation for weighted vector reduction.
- Explicit claim boundary says it is not a full paper reproduction and not an authors-code comparison.

The current RTDL route is useful for developing RTDL residency and continuation mechanics. It does not yet implement the same end-to-end author benchmark contract.

## What Must Be Implemented for a True RTDL Paper Reproduction

To honestly say RTDL reproduces RT-BarnesHut, the repo needs a same-semantics route with these gates:

1. Load the authors' Treelogy/CSV datasets directly.
2. Implement or bind the same 3D Barnes-Hut tree construction contract, including bucket behavior used in the paper.
3. Implement the RT-BarnesHut node-to-triangle / body-to-ray mapping in the RTDL route, or explicitly call out an author-binary adapter as reference-only.
4. Preserve the paper's preprocessing/kernel phase split.
5. Compare RTDL V2.14, V3.0.2, and V4.0 on the same input and same semantic output contract.
6. Compare against the authors' `rtbarneshut` binary on the same POD and dataset.
7. Only then publish a paper-reproduction or author-comparison claim.

## Current Verdict

| Question | Answer |
|---|---|
| Did past RTDL code already reproduce RT-BarnesHut? | No. It explicitly did not. |
| Did we find the authors' source? | Yes: `vani-nag/OWLRayTracing`, branch `BarnesHutRT`, commit `2a3c60d...`. |
| Did we build and run authors' code on the NVIDIA POD? | Yes, after two non-algorithmic compatibility patches. |
| Did we test RTDL V2.14/V3.0.2/V4.0 Barnes-Hut-style routes? | Yes, for the existing RTDL 2D aggregate-frontier workflow. |
| Can we directly compare RTDL's current Barnes-Hut result to the authors' program? | No. Different semantics and scale. |
| Can we claim RTDL V4 reproduces RT-BarnesHut now? | No. |
| Is there a clear implementation path? | Yes: implement same-input, same-semantics RT-BarnesHut route, then rerun V2/V3/V4 plus authors' binary. |

## Non-Authorization

This audit does not authorize:

- public RT-BarnesHut paper-reproduction wording,
- public authors-code-comparison wording,
- public RTDL-over-authors speedup wording,
- broad V4 Barnes-Hut speedup wording,
- release claims based on cross-semantics comparisons.

It authorizes only the following internal statement:

> The authors' RT-BarnesHut source was found, built, and run on the NVIDIA POD; RTDL's historical Barnes-Hut benchmark is not a full paper reproduction; the next engineering step is a same-semantics RTDL route before any author comparison can be claimed.
