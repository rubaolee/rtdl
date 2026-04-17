## Goal 78: Vulkan Positive-Hit Sparse Redesign

### Objective

Replace the current Vulkan positive-hit `pip` path that falls back to dense host full-scan exact finalization with a sparse GPU-candidate generation path plus host exact finalize on candidates only.

### Why

The current Goal 72 result is dominated by waste:

- dense `point_count × poly_count` output allocation
- dense output download
- host exact full-scan over all pairs

That defeats the purpose of the positive-hit contract on long workloads.

### Required Outcome

- keep exact parity
- preserve the public RTDL positive-hit `pip` contract
- generate sparse GPU candidates
- host exact finalize only on those candidates

### Non-Goals

- no weakening of parity
- no broadened performance claim before measurement
- no change to full-matrix semantics
