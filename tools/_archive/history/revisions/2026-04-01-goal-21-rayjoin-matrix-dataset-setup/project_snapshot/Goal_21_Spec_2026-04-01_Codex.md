# Goal 21 Spec

## Title

RayJoin Matrix and Dataset Reproduction Setup

## Motivation

The project now needs a disciplined pre-NVIDIA program for reproducing the RayJoin workload and experiment structure on Embree. The first necessary step is to freeze the exact artifact matrix, dataset provenance, and reduced-size local profile policy before implementing more reproduction-specific code.

## Goal

Define the full RayJoin-on-Embree reproduction matrix, document dataset provenance and substitution status, and define `5–10 minute` local experiment profiles that later goals will execute.

## Position In The Program

This is the first goal in a larger reproduction program:

- Goal 21: matrix + dataset setup
- Goal 22: workload/runtime gap closure
- Goal 23: bounded local reproduction runs and reports

## Acceptance Bar

1. every target paper artifact is mapped to RTDL workloads and datasets
2. provenance and fidelity labels are explicit
3. default local profiles are bounded to `5–10 minutes`
4. unresolved blockers are named explicitly for Goal 22
5. Gemini approves the setup and Claude agrees the setup is technically honest
