# Goal2184 RayJoin Full Reproduction Project Goal

Date: 2026-05-17

Status: project goal defined; local source/protocol/sample execution completed
in `docs/reports/goal2184_rayjoin_phase0_protocol_and_sample_evidence_2026-05-17.md`.
Full paper-scale reproduction remains blocked pending RTX pod evidence and
3-AI consensus.

## Purpose

Goal2184 starts a serious RayJoin reproduction and performance-competition
lane for RTDL v2.0.

The target is not another small demo. The target is to use RTDL v2.0 as a
programming language/runtime to implement RayJoin-style workloads and then
participate in the same performance fight as the ICS 2024 RayJoin paper, as
faithfully as practical.

Source project:

- `https://github.com/rubaolee/RayJoin`

The RayJoin repository describes RayJoin as a framework that uses GPU ray
tracing hardware, including NVIDIA RT Cores, to accelerate high-performance
spatial join processing. Its README identifies two key query types, line
segment intersection (LSI) and point-in-polygon (PIP), and says polygon overlay
is supported by combining LSI and PIP results. The README reports `3.0x` to
`28.3x` speedups over highly optimized methods, lists `query_exec` and
`polyover_exec` binaries, and exposes modes including `grid`, `lbvh`, and `rt`.

## Core Question

Can RTDL v2.0 reproduce RayJoin-style workloads with:

- Python orchestration
- partner GPU code for non-RT work
- generic RTDL Embree/OptiX primitives for RT work
- no app-customized native engine code

and then produce fair, correctness-checked performance comparisons against the
RayJoin paper code and its grid/LBVH/RT modes?

## Non-Negotiable Architecture Boundary

The RTDL native engine remains app-agnostic.

Allowed:

- generic segment/shape/point traversal primitives
- generic prepared build-side state
- generic row/flag/output contracts
- Python app policy
- CuPy/PyTorch partner code for compaction, prefix sums, filtering, batching,
  reductions, and other non-RT GPU work
- optional user-level CuPy RawKernel code when reported as application/partner
  code, not as native-engine customization

Not allowed:

- native symbols named after RayJoin, county, soil, overlay policy, paper
  dataset names, or app-specific continuation names
- hidden RayJoin-only native code paths used as evidence for the generic RTDL
  engine
- whole-paper or v2.0 release claims before correctness, baseline, hardware,
  and external-review gates pass

## Project Phases

### Phase 0: Source Provenance and Buildability

1. Clone `https://github.com/rubaolee/RayJoin` into an external comparison
   workspace, not into the RTDL source tree.
2. Record commit hash, license, build dependencies, and any local patches.
3. Build RayJoin in release mode with OptiX and CUDA.
4. Run the repository's sample `test` workflow before any paper-scale claim.
5. Save a build report under `docs/reports/`.

Pass condition:

- RayJoin paper code builds and its sample test works on a pod.

### Phase 1: Paper Protocol Reconstruction

Extract and document:

- exact query types: LSI, PIP, polygon overlay
- binaries and modes: `query_exec`, `polyover_exec`, `grid`, `lbvh`, `rt`
- parameters: `-poly1`, `-poly2`, `-mode`, `-query`, `-xsect_factor`,
  `-warmup`, `-repeat`, `-check`, `-serialize`
- dataset requirements and CDB conversion path
- warmup/repeat timing semantics
- correctness comparison semantics
- paper hardware and driver/toolchain assumptions where available

Pass condition:

- A protocol document exists and external review confirms that we are not
  comparing against an invented version of RayJoin.

### Phase 2: Dataset Reproduction

Use the RayJoin dataset path as the primary source of truth:

- CDB format
- included small sample dataset under `test`
- linked public sources for USCounty, Zipcode, BlockGroup, WaterBodies, Lakes
  and Parks
- linked preprocessed datasets when legally and technically available

Pass condition:

- At least one sample dataset and one larger public dataset pair can be run
  through both RayJoin and RTDL.

### Phase 3: RTDL v2.0 RayJoin Implementation

Implement a real RTDL v2.0 RayJoin app, not just isolated microbenchmarks.

Required RTDL app components:

- PIP path over generic RTDL point/polygon primitives
- LSI path over generic RTDL segment/segment primitives
- overlay seed/dependency path combining LSI/PIP-style results
- partner-side compaction and batching
- shared reference/correctness rows
- cold-start, warm-hot, and repeated-call timing modes
- no app-customized native engine code

Pass condition:

- RTDL PIP, LSI, and overlay outputs match the selected correctness oracle for
  sample and larger datasets.

### Phase 4: Fair Baselines

Compare against:

- RayJoin `grid`
- RayJoin `lbvh` where applicable
- RayJoin `rt`
- RTDL Embree
- RTDL OptiX one-shot
- RTDL OptiX prepared/reused-state paths
- RTDL+CuPy brute force where useful
- RTDL+CuPy spatially filtered baselines before making RT-core-vs-CUDA-core
  claims

Pass condition:

- Baseline rows clearly identify what is being compared and whether the
  comparison is fair, partial, or diagnostic.

### Phase 5: Performance Evidence

Each accepted artifact must record:

- repo commit
- RayJoin commit
- pod host/port and GPU model
- driver, CUDA, OptiX SDK, compiler
- dataset paths and sizes
- query type and mode
- warmup count
- repeat count
- median/mean/min/max when relevant
- correctness/parity result
- whether timing is cold-start, warm-hot, or repeated prepared-state timing
- claim boundary flags

Pass condition:

- A table can compare RayJoin paper-code modes and RTDL v2.0 modes without
  hidden timing or correctness gaps.

### Phase 6: External Review and Claim Gate

This is a key performance and public-claim lane.

Required reviews:

- Codex implementation/report
- Gemini review
- Claude review when available

Final public claims require 3-AI consensus. Gemini alone is not enough for a
release or paper-competition claim.

Pass condition:

- A consensus report explicitly states which claims are accepted, which are
  accepted-with-boundary, and which remain blocked.

## Relationship to Current Evidence

Current RTDL evidence already shows useful subproblem behavior:

- sparse LSI can strongly favor RTDL/OptiX over brute-force CuPy
- larger overlay dependency rows show a widening OptiX-over-Embree trend
- bounded PIP is parity-clean but Embree-favored at the measured scale

Those are encouraging but not sufficient. They do not reproduce the RayJoin
paper protocol and do not authorize paper-scale or whole-app claims.

Goal2184 turns those partial observations into a structured reproduction
project.

## Success Criteria

Minimum success:

- Build and run RayJoin paper code on a pod.
- Run RTDL v2.0 PIP, LSI, and overlay on at least the same sample datasets.
- Produce correctness-checked comparisons against RayJoin `grid` and `rt`.

Strong success:

- Run larger public CDB datasets through both systems.
- Produce fair tables for LSI, PIP, and overlay.
- Show where RTDL matches, wins, loses, or needs more primitives.

Excellent success:

- RTDL v2.0 is competitive with RayJoin paper code on at least one serious
  workload without violating the app-agnostic engine boundary.
- The report gives clear design lessons for v2.x/v3.0 without overclaiming.

## Open Design Questions

1. Which RayJoin datasets can be legally downloaded and preprocessed on our pod
   timeline?
2. How much of RayJoin's precision strategy must be reproduced in RTDL partner
   code for a fair comparison?
3. What is the right spatially filtered CUDA/CuPy baseline to compare against
   RTDL/OptiX?
4. When should RTDL choose one-shot OptiX versus prepared OptiX automatically?
5. Does RTDL need a stronger generic compact-row or streaming-output primitive
   for overlay continuation?

## Claim Boundary

This goal authorizes starting a serious reproduction project.

This goal does not authorize:

- claiming RTDL reproduces RayJoin results
- claiming RTDL beats RayJoin
- claiming broad RT-core speedup
- claiming v2.0 release readiness
- adding app-specific native engine code

## Immediate Next Actions

1. Clone and build the RayJoin repo on a pod or local Linux host with OptiX.
2. Run its sample workflow.
3. Write a RayJoin build/protocol report.
4. Implement a first RTDL-vs-RayJoin same-dataset sample runner.
5. Ask Gemini and Claude for external review of the protocol before using any
   numbers as public evidence.
