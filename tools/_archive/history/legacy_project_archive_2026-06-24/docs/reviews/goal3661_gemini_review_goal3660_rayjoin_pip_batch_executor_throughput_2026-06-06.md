# Gemini Review: Goal3660 RayJoin PIP Batch Executor Throughput

Date: 2026-06-06
Verdict: `accept-with-boundary`

## Overview

Goal3660 introduces a reusable generic prepared point/closed-shape count executor
to improve PIP throughput for batched repeated requests. This work builds on the
one-shot improvements from Goal3658 but targets a different timing contract:
`batched_repeated_request_throughput_not_one_shot_latency`.

## Assessment against Questions

### 1. Does the implementation stay generic and app-agnostic?

**Yes.** The implementation follows the established pattern of using generic
primitives. The native runtime handles prepared point-probe columns, a prepared
closed-shape scene, a reusable generic count executor, and a stream policy.
RayJoin-specific logic and CDB interpretation remain confined to the Python
application layer.

### 2. Does the new runner path correctly mark the timing contract?

**Yes.** The runner (`scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`)
and the application helper correctly record the `pip_timing_contract` as
`batched_repeated_request_throughput_not_one_shot_latency`. This explicitly
prevents the throughput measurements from being confused with one-shot latency
or drop-in replacements for RayJoin `query_exec` one-shot timing.

### 3. Does the clean A5000 artifact support the bounded finding?

**Yes.** The artifact in `docs/reports/goal3660_rayjoin_pip_batch_executor_throughput_a5000/summary.json`
provides strong support for the reported results:
- **Environment:** NVIDIA RTX A5000, clean commit `def665eb`, `source_dirty: []`.
- **Workload:** Exact count `1417`, batch size `100`, `auto` stream policy.
- **Timing:** RTDL median `0.034225ms/request` (total `1027.254ms` for `30000` requests).
- **Comparison:** RayJoin `query_exec` reported `0.192133ms`, resulting in a
  ratio of `0.178x`.

### 4. Does the report honestly preserve the Goal3658 one-shot/sequential reading?

**Yes.** The report explicitly acknowledges that while Goal3660 provides a
significant throughput win for batched requests, the one-shot/sequential PIP
route from Goal3658 still trails RayJoin's query timing. This distinction is
maintained in the "Current RayJoin Reading" table.

### 5. Are all claim boundaries intact?

**Yes.** Both the report and the JSON artifact strictly adhere to the claim
boundaries. All relevant flags (release authorization, public speedup, RT-core
claim, etc.) are set to `false`.

## Verdict Rationale

The implementation successfully achieves a major throughput improvement for a
specific, valid internal v2.9 use case without overreaching or compromising the
generic architecture of the system. The evidence is clean, the contracts are
explicit, and the boundaries are respected.

## Boundary

Goal3660 is a valid internal v2.9 batched-throughput performance improvement,
not release/public-speedup/paper-reproduction/one-shot-RayJoin-beating
authorization.
