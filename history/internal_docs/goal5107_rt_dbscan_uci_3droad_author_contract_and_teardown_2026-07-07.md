# Goal5107 - RT-DBSCAN UCI 3DRoad Author Contract And Teardown

Date: 2026-07-07

## Verdict

```text
author_directional_border_contract_explains_1k_mismatch__teardown_skip_patch_clean
```

Goal5107 followed the Goal5106 recommendations:

1. reduce the 1K UCI 3DRoad component mismatch;
2. stabilize the patched AuthorOfficial teardown path;
3. keep exact-paper and RTDL correctness claims bounded until the RTDL route can
   be run against the diagnosed author contract.

The result is a useful contract diagnosis, not a completed exact paper gate.

## Summary

Goal5106 found:

```text
author_signature={core_count=329, component_sizes=[90,168,181], noise_count=561}
cpu_signature={core_count=329, component_sizes=[102,168,181], noise_count=549}
core_flags_matched=true
component_partition_matched=false
```

Goal5107 explains this mismatch. The author call-2 DBSCAN path is
index-directional:

```text
callNum == 2 && xID > primID
```

When the current ray/source point `xID` is core and the intersected primitive
point `primID` is non-core, the author assigns:

```text
frameBuffer[primID].parent = xParent
```

Therefore a non-core point can be absorbed as a border point only through a
higher-index core neighbor. A conventional DBSCAN reference attaches a border
point to any core neighbor.

The 1K UCI 3DRoad mismatch is exactly explained by this rule:

```text
conventional_mismatch_count=12
author_directional_mismatch_count=0
```

The 12 mismatching conventional-reference border points each have lower-index
core neighbors and no higher-index core neighbors. They remain noise under the
author contract.

## New Artifacts

Contract analysis script:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/analyze_uci_3droad_author_contract.py
```

Author teardown patch:

```text
Paper-reproduction-apps/rt-dbscan-paper/author_patches/goal5107_authorofficial_skip_context_destroy_after_payload.patch
```

Clean author outputs:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_author_goal5107_clean.jsonl
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_author_goal5107_clean_stdout.txt
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_16k_author_goal5107_clean.jsonl
```

The 16K raw stdout was intentionally excluded from the source release because
it is a 36.7 MB stream dominated by repeated `callNum` diagnostics. The compact
16K JSONL result above remains the durable evidence artifact.

Contract diagnosis:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_goal5107_contract_analysis.json
```

Regression test:

```text
tests/goal5107_rt_dbscan_uci_3droad_contract_analysis_test.py
```

## Author Teardown Patch

Goal5106 showed that patched AuthorOfficial wrote JSON/timing and then exited
with `SIGSEGV` during teardown. Goal5107 adds a comparator-only patch:

```text
RTDL_AUTHOROFFICIAL_SKIP_CONTEXT_DESTROY=1
```

When the variable is set, the patched author program flushes output and returns
cleanly before `owlContextDestroy(context)`. The patch does not change
`deviceCode.cu`, kernels, DBSCAN union/border logic, payload fields, or timing
fields.

Local patch-stack check:

```text
base patch: goal5092_authorofficial_core_count_output.patch
new patch : goal5107_authorofficial_skip_context_destroy_after_payload.patch
result    : patch_stack_ok
```

POD clean outputs were produced with the new binary:

```text
/root/rtdl_goal5093/Paper-reproduction-apps/rt-dbscan-paper/_authorofficial_goal5107_work/build/sample02-rtdbscan
```

## Clean AuthorOfficial POD Results

### 1K

Input:

```text
Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/uci_3droad_1k_author_2d_zero_z.csv
epsilon=0.05
minPts=100
```

Result:

```text
point_count=1000
core_count=329
component_sizes=[90,168,181]
noise_count=561
cluster_formation_time_sec=0.637012
total_time_sec=1.27797
exit_status=clean with RTDL_AUTHOROFFICIAL_SKIP_CONTEXT_DESTROY=1
```

### 16K

Input:

```text
Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/uci_3droad_16k_author_2d_zero_z.csv
epsilon=0.05
minPts=100
```

Result:

```text
point_count=16000
core_count=12625
component_count=22
noise_count=2347
cluster_formation_time_sec=48.1438
total_time_sec=96.3741
exit_status=clean with RTDL_AUTHOROFFICIAL_SKIP_CONTEXT_DESTROY=1
```

The 16K output is a clean same-source author diagnostic. It is not a performance
comparison and not exact paper reproduction.

## Contract Analysis

Analysis command output:

```text
schema=rtdl.paper_reproduction.rt_dbscan.uci_3droad_contract_mismatch_analysis.v1
point_count=1000
epsilon=0.05
min_points=100
core_count=329
conventional_mismatch_count=12
author_directional_mismatch_count=0
author_noise_conventional_cluster_count=12
```

Signatures:

```text
author_signature={component_count=3, component_sizes=[90,168,181], core_count=329, noise_count=561}
author_directional_signature={component_count=3, component_sizes=[90,168,181], core_count=329, noise_count=561}
conventional_signature={component_count=3, component_sizes=[102,168,181], core_count=329, noise_count=549}
```

First mismatching point records:

```text
point_id=136..146 and 183
core_neighbor_count=8
lower_index_core_neighbor_count=8
higher_index_core_neighbor_count=0
```

Interpretation:

```text
The fixed-radius core predicate is aligned. The remaining difference is the
author's directional border attachment rule. Conventional DBSCAN marks these
12 points as border points; the author contract leaves them as noise because
their core neighbors have lower indices only.
```

## Tests

Command:

```text
py -m unittest tests.goal5107_rt_dbscan_uci_3droad_contract_analysis_test tests.goal5094_rt_dbscan_authorofficial_component_signature_gate_test tests.goal5101_component_partition_helpers_test tests.goal5104_rt_dbscan_author_warm_loop_runner_test
```

Result:

```text
Ran 13 tests in 0.043s
OK
```

Test coverage includes:

- the 1K analysis summary values;
- the first mismatch witness structure;
- teardown patch content and scope;
- clean 1K author output values;
- clean 16K author output values;
- prior component-partition helpers and bounded RT-DBSCAN gates.

## What This Proves

Proved:

- The Goal5106 1K UCI 3DRoad component mismatch is explained by an author
  directional border-assignment contract.
- The author-directional app-side reference matches the clean patched
  AuthorOfficial 1K payload exactly.
- The conventional DBSCAN reference is intentionally not the correct comparator
  for this author binary on this input.
- The AuthorOfficial teardown crash can be avoided with a comparator-only skip
  after payload/timing output.
- Clean AuthorOfficial same-source outputs now exist for 1K and 16K UCI 3DRoad
  candidates.

Not proved:

- exact paper input provenance;
- exact paper dataset reproduction;
- RTDL OptiX+Numba correctness on UCI 3DRoad;
- RTDL performance on UCI 3DRoad;
- full RT-DBSCAN paper reproduction;
- that the public UCI transform is the author's exact `3droad_full.csv`.

## Authorized Claim

Allowed:

```text
Goal5107 diagnosed the 1K UCI 3DRoad same-source mismatch as an author
directional border-assignment contract. Conventional DBSCAN mismatches 12
points, while an author-directional reference mismatches 0 points against the
clean patched AuthorOfficial payload. A comparator-only teardown skip patch
also produced clean 1K and 16K AuthorOfficial outputs.
```

Forbidden:

```text
Exact RT-DBSCAN paper reproduction is complete.
RTDL matches AuthorOfficial on UCI 3DRoad.
UCI 3DRoad public source is proven identical to the paper's author input.
RTDL performance or author parity is established on 3DRoad.
The teardown patch changes DBSCAN semantics.
```

## Next Recommended Goal

Goal5108 should close one of two blockers:

1. update the RTDL same-source component runner/reference to compare against the
   author-directional contract and run the 1K UCI 3DRoad gate; or
2. fix the POD Numba/PTX environment blocker first, then run RTDL OptiX+Numba
   against the author-directional 1K comparator.

Either route must preserve the distinction:

```text
same-source public UCI candidate != exact paper input
author-directional comparator != conventional DBSCAN
clean author output != RTDL correctness gate
```
