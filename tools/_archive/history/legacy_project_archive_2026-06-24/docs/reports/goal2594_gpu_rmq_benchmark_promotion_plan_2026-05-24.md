# Goal2594 GPU-RMQ Benchmark Promotion Plan

Date: 2026-05-24

Status: candidate benchmark front door. This is not a full paper reproduction,
not pod evidence, and not public speedup wording.

## Paper Target

The target paper is:

- Lara Kreis, Justus Henneberg, Valentin Henkys, Felix Schuhknecht, and Bertil
  Schmidt, **GPU-RMQ: Accelerating Range Minimum Queries on Modern GPUs**,
  arXiv:2604.01811.

The paper matters because it moves beyond the earlier RTXRMQ closest-hit-only
geometric mapping. It uses hierarchical range-minimum summaries and hybrid
query answering across CUDA-core-style scans and RT-core-style traversal.

The authors' repository is `https://github.com/lakreis/GPU-RMQ`. It was
inspected at commit `86fed1c170b7e41e8ec44e461f7220f87f492893`.

## Benchmark Scope

The first RTDL benchmark scope is the exact RMQ contract:

- input: array `A`;
- input: inclusive query intervals `[left, right]`;
- output: one compact row per query containing `query_id`, `left`, `right`,
  leftmost argmin index, and minimum value.

The front door adds:

- a deterministic CPU oracle;
- a dependency-light local hierarchical path using block summaries plus a sparse
  table over block minima;
- a paper-style RT lowering reference that encodes values as triangle
  x/t-distance, maps query intervals to +x rays, and decodes generic
  `ray_triangle_closest_hit` rows back into leftmost-argmin RMQ rows;
- a command plan for pod work.
- authors-code comparison metadata, including algorithm IDs and CSV parsing.
- a reusable `scripts/goal2595_gpu_rmq_author_runner.py` packet for cloning,
  building, patching saved-input paths, and running authors-code matrices on a
  pod.

The authors' repository does not ship fixed static datasets. It generates arrays
and queries from `n`, `q`, `lr`, and `--seed`. Therefore the fair comparison
plan is:

1. Use the paper script workload parameters where possible: `q=2^26`, array
   sizes around `2^20` through `2^31`, and `lr` values `-1`, `-2`, `-3`, and
   `-6`.
2. Run the authors' `./rtxrmq` binary for HRMQ, full GPU scan, RTXRMQ, and
   GPU-RMQ variants such as algorithms `16` and `20`.
3. For exact same-input correctness, patch the authors' hardcoded
   `directory_save_aux_data` path and use `--save-input-data`, then replay the
   saved array/query binaries through RTDL's `author_input_cpu_reference` mode.
4. Compare index build time, query throughput, ns/query, memory footprint, and
   correctness status separately.

## Why This App Is Worth Promoting

GPU-RMQ exercises a different RTDL design area than the current benchmark apps.
The important pressure is not a CUDA-only hierarchy. It is whether a user can
write Python+partner+RTDL code that deliberately routes the RT-suitable part of
RMQ through RT cores while keeping application semantics outside the engine:

- Python owns query semantics and policy.
- A partner such as CuPy owns hierarchy construction and scan-heavy work.
- RTDL exposes generic prepared traversal or closest-hit rows; the local
  `paper_rt_lowering_reference` mode already proves the closest-hit contract on
  CPU.
- Native engines must not know RMQ, GPU-RMQ, or paper-specific formulas.

The current honest gap is native OptiX validation: RTDL has a generic
closest-hit contract surface, Embree has native 3-D closest-hit plumbing, and
the source tree now wires native OptiX generic 3-D closest-hit rows. The app
still needs NVIDIA build/correctness/timing evidence before the OptiX path can
be treated as ready. Therefore CuPy-only results are baseline evidence, not the
benchmark's final RTDL result.

## Current Claim Boundary

Allowed:

- "candidate benchmark front door";
- "exact local CPU oracle";
- "local hierarchy-style RMQ contract";
- "paper-style RT lowering contract over generic `ray_triangle_closest_hit`";
- "planned GPU-RMQ-inspired benchmark track".

Not allowed:

- full GPU-RMQ reproduction claim;
- throughput/speedup claim;
- validated native OptiX RTDL primitive claim;
- OptiX RT-core performance claim for the paper-style lowering;
- paper-code comparison claim;
- public performance wording.

## Next Milestones

1. Add a CuPy hierarchy/scan baseline and measure index-build time, query time,
   and memory on a pod.
2. Build and validate native OptiX execution for generic
   `ray_triangle_closest_hit` rows, then run the existing paper-style RT lowering
   against that path without adding RMQ-specific native code.
3. Build and run the released GPU-RMQ authors code and preserve the exact commit,
   CUDA/OptiX versions, CLI arguments, output CSV, and raw stdout.
4. Write a pod evidence report and require consensus before promoting the app
   from candidate to closed benchmark.

The local `author_style_compare_local` mode is only a distribution-level
analogue of the authors' `lr` classes. It is useful for RTDL-side local
debugging, but not same-input evidence. Same-input evidence must use the
authors' saved binary inputs through `author_input_cpu_reference`.
