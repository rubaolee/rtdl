# Goal 18: Low-Overhead Runtime Continuation

Goal 17 proved the key architecture point:

- the Python-like DSL can stay
- the expensive part is the current runtime data path
- packed inputs plus prepared execution plus a thin raw-row result path can materially reduce the gap to native on Embree

Goal 18 continues that work.

## Goal

Turn the low-overhead runtime from an experimental side path into a more first-class RTDL runtime mode, and extend it beyond the first two workloads.

## Required Direction

Goal 18 should:

1. keep the Python-like DSL unchanged
2. make the low-overhead path easier to use directly from `run_embree(...)`
3. extend prepared/raw execution support beyond:
   - `lsi`
   - `pip`
4. keep correctness parity with the current RTDL Embree behavior
5. preserve honest wording about where native C++ comparisons do and do not exist

## First-Slice Continuation Scope

The continuation slice should include:

- a first-class `result_mode` or equivalent execution option so users can request thin native result views directly
- prepared/raw support for the remaining Embree-backed local workloads where practical
- packed input support for the remaining geometry kinds needed by those workloads
- regression tests for the extended prepared/raw path
- a benchmark/update report showing:
  - current RTDL Embree
  - prepared/raw RTDL Embree
  - native Goal 15 baseline where available

## Acceptance Criteria

This continuation slice is acceptable only if:

1. existing DSL kernels remain valid without syntax changes
2. the low-overhead mode becomes easier to use than the Goal 17 experimental path
3. correctness parity is preserved on the extended workload set
4. the report clearly separates:
   - native-comparison workloads
   - non-native-comparison workloads
5. no performance claim exceeds the measured evidence

## Non-Goals

This round still does not require:

- OptiX/NVIDIA work
- full elimination of Python from all result paths
- performance parity claims for workloads without a native comparison baseline
