# Embree RayJoin Reproduction Program

## Purpose

This program defines the next pre-NVIDIA phase of RTDL.

The goal is to reproduce as much of the RayJoin workload and experiment surface as possible on top of the current Embree backend, while keeping each local experiment bounded to roughly `5 minutes` and never more than `10 minutes` by default on this Mac.

This program treats the lack of an NVIDIA GPU as a temporary backend constraint, not as a reason to delay semantic and evaluation work.

## Program Goal

Use RTDL plus the current Embree backend to:

- support every RayJoin workload requirement that matters for the paper-level evaluation,
- acquire or reconstruct the paper datasets where feasible,
- define reproducible reduced-size local experiment profiles,
- run those profiles within a practical local runtime budget,
- and generate the corresponding tables, figures, and reports.

## Constraints

- backend: Embree only
- semantic reference: `run_cpu(...)`
- local runtime budget: default experiment packages should stay in the `5–10 minute` range
- `lsi` and `pip` may use different scaled profiles
- substitutions, derivations, and synthetic reductions must be documented explicitly

## Program Structure

### Goal 21: Matrix and Dataset Reproduction Setup

Freeze the RayJoin reproduction matrix and build the dataset-provenance / local-profile plan.

Deliverables:

- exact paper artifact mapping (`Table 3`, `Table 4`, `Figure 13`, `Figure 14`, `Figure 15`)
- workload-to-RTDL mapping
- dataset provenance and acquisition status
- reduced local profile definitions bounded to `5–10 minutes`
- explicit fidelity labels:
  - `exact-input`
  - `derived-input`
  - `synthetic-input`

### Goal 22: Workload and Runtime Completion for RayJoin-on-Embree

Fill the RTDL/runtime gaps that block honest RayJoin-style reproduction on Embree.

Potential work includes:

- any missing workload semantics needed for the paper targets
- any missing evaluation runner support
- any required reporting or parity scaffolding
- any blocking limitations discovered during Goal 21 dataset/matrix work

This goal does **not** imply adding random new features. It is tightly scoped to what the RayJoin reproduction matrix requires.

### Goal 23: 5-Minute Embree Reproduction Runs

Execute the frozen reduced-size experiment matrix and generate:

- benchmark artifacts
- table outputs
- figure outputs
- a final Embree reproduction report

This goal closes only when the report states clearly:

- what was reproduced directly
- what was reproduced via reduced-size profiles
- what remains impossible or deferred until the NVIDIA phase

## Co-Working Rules

Each goal in this program uses the same review model:

1. Codex writes the plan and implementation reports.
2. Gemini reviews every plan/code/doc transition.
3. Claude audits each goal before closure.
4. No goal is closed until Codex and Claude agree, with Gemini monitoring the process.

## Success Condition

This program succeeds when RTDL has a defensible Embree-based reproduction package for the RayJoin workload and experiment structure, under clearly documented local scaling limits, and the repo contains the corresponding tables, figures, and reports.
