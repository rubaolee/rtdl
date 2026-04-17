# Goal 38 Large-Scale Embree Feasibility

Date: 2026-04-02

## Goal

Establish whether `192.168.1.20` can sustain a serious large-scale Embree-only spatial join run that approaches the nationwide or paper-scale RayJoin setting for the current RTDL v0.1 workload surface.

This is a feasibility-first goal, not a paper-claim goal.

## Motivation

Current RTDL status on the Linux Embree track is strong for:

- exact-source regional slices
- parity-clean `lsi` and `pip`
- representative real-family performance ladders

What is still unknown is whether the current Linux host can honestly sustain a much larger:

- `County ⊲⊳ Zipcode`
- or `BlockGroup ⊲⊳ WaterBodies`

execution package without:

- conversion collapse
- memory exhaustion
- unbounded runtime
- or correctness drift under scale

## Scope

Goal 38 should:

- stay Embree-only
- use `192.168.1.20` as the sole large-scale host
- use already-proven public-source families before introducing new ones
- focus first on one family with the best chance of scaling on this machine
- measure feasibility before attempting any final nationwide claim
- exclude the Python CPU simulator from the main large-scale timing path

## Primary Candidate Family

Primary first family:

- `County ⊲⊳ Zipcode`

Reason:

- full raw-source staging is already complete
- exact-source conversion already exists
- the family is smaller and operationally cleaner than `BlockGroup ⊲⊳ WaterBodies`
- it is the best first step toward a broader nationwide-style Embree run on the current host

Secondary follow-on family:

- `BlockGroup ⊲⊳ WaterBodies`

Reason:

- it is more demanding and paper-representative
- but it has much higher feature counts and higher risk of host exhaustion

## Planned Execution Strategy

The goal should proceed in staged scaling tiers instead of jumping directly to nationwide execution.

### Tier 1: Broad Regional Expansion

Use deterministic multi-county or multi-bbox exact-source slices that are materially larger than the current accepted regional ladders.

Deliverables:

- frozen larger slice definitions
- parity check for `lsi` and `pip`
- runtime and row-count report

### Tier 2: State-Level or Multi-State Expansion

Attempt one substantially larger bounded package, ideally by geographic aggregation rather than arbitrary chain truncation.

Deliverables:

- host memory/runtime measurements
- conversion cost summary
- Embree-only timing result
- explicit statement that the Python simulator is not part of the large-scale benchmark path
- optional note on whether a future native C/C++ checker would be needed for larger-scale correctness validation

### Tier 3: Nationwide Feasibility Probe

Attempt a full-family or near-full-family Embree run only if Tier 2 remains tractable.

Deliverables:

- full-package runtime
- host resource summary
- explicit success/failure boundary
- honest statement on whether a nationwide Embree join is now feasible on this host

## Required Measurements

For each accepted point:

- feature counts
- chain counts
- segment counts where applicable
- conversion time
- Embree time
- row counts

For each rejected point:

- exact failure mode
  - runtime too long
  - memory pressure
  - conversion failure
  - parity failure
  - source instability

## Acceptance

Goal 38 is accepted only if it produces:

- a frozen scaling ladder toward large-scale execution
- at least one materially larger accepted Linux-host exact-source run than current regional slices
- a measured statement about whether nationwide-scale Embree execution is feasible on `192.168.1.20`
- an honest stop boundary if full nationwide execution is still not supportable

## Non-Goals

Goal 38 does not require:

- full RayJoin GPU-equivalent reproduction
- OptiX/CUDA work
- new DSL surface expansion
- introducing unsupported source claims
- a Python-oracle large-scale comparison

## Large-Scale Validation Policy

For Goal 38 and later large-scale feasibility rounds:

- the main measurement path is Embree-only
- the Python simulator is not included in the primary large-scale runtime numbers
- if a larger-scale correctness oracle becomes necessary, it must be a separate native C/C++ checker or another explicitly bounded validation path

## Expected Output

The final report for this goal should answer:

1. Can this Linux host sustain a much larger exact-source Embree join than the current regional slices?
2. Which family is the right first nationwide-feasibility candidate?
3. How far toward nationwide scale did the host get before the first hard boundary appeared?
4. Is a true nationwide Embree run now justified as the next goal, or is another scaling/engineering round still required?
