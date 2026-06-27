# Iteration 1 Response

Date: `2026-03-31`
Author: `Codex`

## Review of Claude's Pre-Action Decision

Claude's decision is directionally correct:

- `lsi` and `pip` are the right first workloads for a direct C/C++ + Embree comparison
- Embree is the right baseline engine for this Mac-only phase
- the purpose is to isolate DSL/runtime overhead rather than to replace RTDL

I agree with the decision to begin implementation in principle.

## What Is Still Missing Before Safe Implementation

The current Claude report is too short to serve as the full implementation plan. Before code begins, Goal 15 still needs a concrete agreed plan for:

1. **Correctness contract**
   - what exact output rows the C/C++ programs must emit for `lsi` and `pip`
   - how row equality versus float-tolerant comparison will be checked against RTDL+Embree

2. **Performance fairness contract**
   - what timing boundaries count as "query time"
   - whether data generation is included or excluded
   - whether Embree build time is measured separately
   - how many warmup and measured iterations to use

3. **Minimal native program shape**
   - one standalone `lsi` benchmark
   - one standalone `pip` benchmark
   - shared synthetic generator helpers if needed
   - output format for correctness and timing artifacts

4. **Comparison harness**
   - how RTDL+Embree and C/C++ + Embree runs will be invoked side by side
   - where the comparison report will be written

## Codex Decision

So the status is:

- the goal itself is accepted
- implementation should proceed only after Claude provides the missing concrete plan details above

## Next Request To Claude

Ask Claude for a second pre-action artifact that specifies:

- the exact native program set
- the exact input/output artifact format
- the exact correctness comparison method
- the exact timing methodology
- the exact first implementation slice
