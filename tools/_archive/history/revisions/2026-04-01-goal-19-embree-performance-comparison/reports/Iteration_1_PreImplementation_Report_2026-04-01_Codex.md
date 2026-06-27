# Goal 19 Pre-Implementation Report

## Proposed Scope

Goal 19 should answer the project-critical performance question:

Can the current RTDL runtime be considered performance-comparable to pure C/C++ + Embree for the workloads it supports?

The comparison should be staged:

1. deterministic fixture comparison
2. larger matched profile comparison

The default local package should be tuned to finish in about `5–10 minutes` total. That means `lsi` and `pip` should be allowed to use different larger-profile sizes.

## Proposed Work

### 1. Reuse and extend Goal 15 native baselines

Current native baselines already exist for:

- `lsi`
- `pip`

These should be reused where possible, then extended to larger matched profiles.

### 2. Compare all current RTDL runtime modes

For each workload/profile:

- current dict-return `run_embree(...)`
- first-class raw `run_embree(..., result_mode="raw")`
- prepared raw path
- pure native executable path

### 2.5 Keep the run length bounded

Before final timing runs, calibrate the larger profiles so that:

- `lsi` larger-profile comparison stays in a practical local window
- `pip` larger-profile comparison also stays practical
- the full default package remains in the `5–10 minute` target range

### 3. Keep correctness first

No timing claim should be accepted unless:

- RTDL dict rows match native
- RTDL raw rows match dict rows
- prepared raw rows match dict rows

### 4. Report honestly

The final report should distinguish:

- small fixture host-overhead comparisons
- larger-profile comparisons
- workloads with native baselines
- workloads without native baselines
- why the chosen `lsi` and `pip` profile sizes fit the intended local runtime budget

## Expected Outcome

Goal 19 should end with a direct architectural conclusion:

- RTDL is close enough to native for the current Embree phase
or
- RTDL still needs another runtime redesign slice before the project can claim comparable performance.
