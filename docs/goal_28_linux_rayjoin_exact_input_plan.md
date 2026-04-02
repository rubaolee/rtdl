# Goal 28: Linux Exact-Input RayJoin-on-Embree Feasibility and Reproduction

Date: 2026-04-02

## Goal

Use the Linux host `192.168.1.20` as the next Embree performance platform and attempt the closest practical reproduction of the RayJoin paper workloads and datasets on CPU/Embree, replacing the current Mac-only reduced local profiles where feasible.

This goal is still pre-NVIDIA and still Embree-only.

## Important Reality Check

The Linux host is more suitable than the local Mac for long-running Embree tests, but it is not an unlimited paper-scale machine.

Observed host capacity:

- CPU: Intel Core i7-7700HQ
- Threads: `8`
- Memory: `15 GiB`
- Storage free on `/`: about `186 GiB`

Therefore Goal 28 cannot honestly start from the assumption that every RayJoin paper dataset can be executed unchanged at full paper scale on this host. The first step must be a feasibility gate.

## Updated Objective

The correct objective is:

1. acquire the same RayJoin dataset families wherever possible
2. stage them on `192.168.1.20`
3. test which workloads and dataset sizes are actually feasible on that host
4. run exact-input or near-exact-input Embree experiments where the host can sustain them
5. fall back to documented bounded reductions only when exact-input execution is not feasible

## Goal Structure

### Goal 28A: Exact-Input Acquisition and Host Feasibility Audit

Deliverables:

- staged dataset inventory on `192.168.1.20`
- exact-input vs derived-input classification per RayJoin dataset family
- host memory/runtime feasibility notes for:
  - Table 3 families
  - Figure 13 / Figure 14 profiles
  - Table 4 / Figure 15 analogue paths
- explicit run budget policy for Linux host experiments

Closure condition:

- the repo contains a serious Linux-host feasibility report that says which paper-scale or exact-input cases are truly runnable

### Goal 28B: Linux Embree Exact-Input Execution Slice

Deliverables:

- Linux-host benchmark runners for the feasible exact-input cases
- collected runtime artifacts
- CPU vs Embree parity checks where applicable
- honest reporting of which exact-input cases executed successfully

Closure condition:

- at least one meaningful exact-input RayJoin family is executed on the Linux host and reported honestly

### Goal 28C: Linux Embree Reproduction Report

Deliverables:

- tables/figures/report updated for Linux-host runs
- explicit comparison against the previous Mac bounded-local slice
- clear labels:
  - `exact-input`
  - `derived-input`
  - `bounded-reduction`
  - `not-feasible-on-current-host`

Closure condition:

- the report makes clear what was really reproduced on Linux and what still remains blocked by hardware scale

## Co-Working Rule

This goal follows the current project rule:

- Codex writes plans and implementation
- Gemini monitors each step
- Claude reviews and must approve before closure

## Immediate Next Step

Start Goal 28A:

- acquire or stage RayJoin dataset families on `192.168.1.20`
- measure host feasibility before promising paper-scale execution
