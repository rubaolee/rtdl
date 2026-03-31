# Embree Evaluation Plan

## Goal

Goal 9 is to reproduce as much of the RayJoin evaluation structure as practical
on the RTDL Embree baseline engine before the NVIDIA/OptiX phase begins.

Status note:

- Goal 9 itself is complete and published.
- This document now serves as the checked-in foundation for the newer Goal 13 paper-reproduction phase.
- Goal 13 extends the same Embree evaluation machinery toward RayJoin-paper table and figure analogues.

This is not the final RT-core result. It is the local pre-GPU evaluation phase.

The outputs of Goal 9 are:

- a frozen Embree evaluation matrix,
- reproducible benchmark artifacts,
- generated result tables,
- generated figure files,
- and a written gap analysis against the RayJoin paper evaluation.

## Scope

Goal 9 stays within the current RTDL Embree baseline:

- backend: `run_embree(...)`
- semantic reference: `run_cpu(...)`
- precision mode: `float_approx`
- workload surface:
  - `lsi`
  - `pip`
  - `overlay`
  - `ray_tri_hitcount`

The goal is to cover as many RayJoin-aligned workload and dataset combinations as
the current baseline can support honestly.

## Evaluation Principles

The Embree evaluation should:

- reuse the frozen baseline contracts,
- prefer public RayJoin-aligned datasets and derived subsets,
- separate correctness validation from timing runs,
- store raw benchmark outputs in machine-readable form,
- generate human-readable tables and figures from those outputs,
- and label all outputs as Embree-baseline results rather than final RT-core
  figures.

## Workload Tiers

### Tier 1: Required Baseline Workloads

These are required for Goal 9 completion:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`

### Tier 2: Dataset Breadth

Each required workload should be evaluated on:

- authored minimal examples,
- current tiny RayJoin-derived fixtures,
- and at least one larger representative dataset or derived dataset when the
  ingestion path supports it.

## Dataset Plan

The evaluation matrix should use the following dataset categories.

### Authored Minimal

Purpose:

- quick correctness checks,
- smoke tests for runners and plotting,
- and stable examples in docs.

### Tiny RayJoin Fixtures

Current fixture sources:

- `tests/fixtures/rayjoin/br_county_subset.cdb`
- `tests/fixtures/rayjoin/br_soil_subset.cdb`

Purpose:

- deterministic local reproduction,
- cross-backend parity checks,
- and benchmark harness stability.

### Larger Representative Inputs

Goal 9 should add at least one larger representative evaluation path using
RayJoin-aligned data or a documented derived subset of public RayJoin data.

If full-size source datasets are too large or inconvenient for the repository,
the plan should:

- document where they come from,
- document how RTDL derives the local benchmarkable subset,
- and keep the derivation reproducible.

## Deliverables

Goal 9 should produce:

1. A frozen evaluation matrix document.
2. Benchmark runner support for the evaluation matrix.
3. Stored benchmark JSON artifacts under `build/` or `out/`.
4. Generated summary tables in Markdown or CSV form.
5. Generated figure files, preferably PNG plus optional editable sources.
6. Documentation that explains:
   - what matches the RayJoin evaluation structure,
   - what is approximated,
   - what remains NVIDIA-only,
   - and what the current limitations are.

## Implementation Steps

### 1. Freeze the evaluation matrix

Record the exact:

- workloads,
- datasets,
- backends,
- run counts,
- warmup policy,
- and output artifacts.

### 2. Expand the dataset path where needed

Add or document larger representative datasets and their derivation pipeline.

### 3. Extend the benchmark harness

Make the harness capable of:

- selecting evaluation-matrix slices,
- labeling runs consistently,
- saving stable benchmark artifacts,
- and recording enough metadata for figure generation.

### 4. Generate result tables

Add scripts that turn benchmark JSON into compact:

- Markdown tables,
- CSV tables,
- and any supplementary per-workload summaries.

### 5. Generate figures

Add scripts that produce paper-style visual summaries from the benchmark outputs.

Expected figure types:

- grouped workload latency comparisons,
- per-dataset backend comparisons,
- and optional scaling plots if the input matrix supports them.

### 6. Write the evaluation note

Document:

- what the Embree evaluation reproduces,
- where it departs from the RayJoin paper,
- and how it prepares the NVIDIA phase.

## Acceptance Criteria

Goal 9 is complete when:

- every baseline workload appears in the evaluation matrix,
- benchmark artifacts can be regenerated from commands in the repository,
- result tables are generated automatically,
- figures are generated automatically,
- the docs explain the exact meaning of the Embree evaluation,
- and the review round agrees the output is a defensible pre-GPU reproduction.

## Relationship To The Final Goal

Goal 9 is still pre-GPU work.

It does not claim:

- OptiX execution,
- RT-core execution,
- or final paper-performance reproduction.

It does claim:

- an executable local evaluation pipeline,
- a paper-structured Embree baseline,
- and reproducible tables and figures that prepare the final NVIDIA phase.
