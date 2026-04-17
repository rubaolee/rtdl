# Goal 53 Bounded Multi-Backend Matrix Closure

## Objective

Use the now-trusted bounded RTDL foundation to close the next major reproduction gap:

- complete a bounded comparison matrix across the accepted real-data workloads
- compare the trusted execution targets:
  - PostGIS
  - C oracle
  - Embree
  - OptiX
- produce a final bounded comparison package that is honest about:
  - correctness
  - performance
  - scope limits

## Why This Goal Is Next

The project has already crossed the foundational correctness threshold:

- C oracle, Embree, and OptiX are internally aligned on the accepted packages
- Goal 50 established PostGIS as an external correctness reference on those same packages

That means the next valuable work is no longer backend bring-up. It is matrix closure:

- same workloads
- same packages
- same host
- same trusted semantics

## Accepted Scope

### Packages

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`

### Workloads

- `lsi`
- `pip`

### Systems Compared

- PostGIS
- C oracle
- Embree
- OptiX

### Host

- `192.168.1.20`

## Main Deliverables

1. A consolidated bounded comparison harness or report input pipeline that can present the four-system matrix clearly.
2. A final report with:
   - exact correctness status
   - timing table
   - interpretation of where each system is faster/slower
   - explicit fairness boundaries
3. An updated reproduction-matrix status note for what is now closed and what still remains open.

## Required Honesty Rules

- No claim of nationwide closure.
- No claim that PostGIS and RTDL execute identical internal algorithms.
- `pip` must explicitly note:
  - PostGIS is measured as an indexed positive-hit query
  - RTDL emits full-matrix truth rows
  - parity is established after expansion into the same truth semantics
- Any cross-round performance comparison must identify when timings come from different rerun phases or different harness structures.

## Proposed Execution Steps

1. Gather the accepted final measurements already produced by the accepted source artifacts and record the exact source report for every row.
2. Prefer a single accepted source of truth per matrix row to avoid cross-phase drift.
3. Apply this rerun rule:
   - if any matrix row would come from a different accepted code state or a different harness structure than the rest of the matrix, rerun that row
   - otherwise do not rerun
4. Run an OptiX preflight check before any refresh rerun:
   - GPU visible
   - driver/runtime visible
   - OptiX library load succeeds
5. Normalize the accepted rows into a single comparison table for both accepted packages.
6. Write the bounded matrix closure report.
7. Send the report to Gemini and Claude.
8. Close only after at least 2-AI consensus.

## Success Condition

Goal 53 succeeds when the repo has one accepted, reviewed, bounded four-system comparison package that clearly states:

- what is closed
- what is correct
- what is fast
- what is still out of scope

## Boundary

This goal is a bounded matrix-closure goal, not a new nationwide execution goal and not a new backend bring-up goal.
