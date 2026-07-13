# Call For Review - Goal5107 RT-DBSCAN UCI 3DRoad Author Contract And Teardown

Please strictly review Goal5107:

```text
history/internal_docs/goal5107_rt_dbscan_uci_3droad_author_contract_and_teardown_2026-07-07.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/analyze_uci_3droad_author_contract.py
Paper-reproduction-apps/rt-dbscan-paper/author_patches/goal5107_authorofficial_skip_context_destroy_after_payload.patch
tests/goal5107_rt_dbscan_uci_3droad_contract_analysis_test.py
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_goal5107_contract_analysis.json
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_author_goal5107_clean.jsonl
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_16k_author_goal5107_clean.jsonl
Paper-reproduction-apps/rt-dbscan-paper/data/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
history/internal_docs/rt_dbscan_review_opinions_register_2026-07-07.md
```

## Context

Goal5106 pinned the public UCI 3DRoad source and generated author-format
same-source candidates. It found that 1K AuthorOfficial and a conventional CPU
DBSCAN reference matched on core flags/core count but diverged on component
partition/signature. It also found that the patched AuthorOfficial wrote
payload/timing but exited with `SIGSEGV` during teardown.

Goal5107 claims to resolve both issues at the diagnostic/comparator level:

- the component mismatch is explained by the author's index-directional border
  assignment contract;
- a comparator-only teardown patch produces clean 1K and 16K AuthorOfficial
  outputs without changing DBSCAN kernels or payload semantics.

## Claimed Outcome

```text
author_directional_border_contract_explains_1k_mismatch__teardown_skip_patch_clean
```

The report claims:

- Author call-2 only attaches/merges through the branch guarded by
  `callNum == 2 && xID > primID`.
- Therefore a non-core point can be attached as a border point only by a
  higher-index core neighbor.
- The 12 conventional-reference mismatches are exactly points with lower-index
  core neighbors and no higher-index core neighbors.
- Conventional DBSCAN mismatch count is 12, but author-directional mismatch
  count is 0 against clean patched AuthorOfficial.
- `RTDL_AUTHOROFFICIAL_SKIP_CONTEXT_DESTROY=1` cleanly returns after payload and
  timing output and does not modify `deviceCode.cu` or algorithm semantics.
- Clean 1K and 16K same-source AuthorOfficial outputs are now available.
- This still does not close exact paper input reproduction or RTDL 3DRoad
  correctness.

## Key Evidence

1K contract analysis:

```text
author_signature={core_count=329, component_sizes=[90,168,181], noise_count=561}
conventional_signature={core_count=329, component_sizes=[102,168,181], noise_count=549}
conventional_mismatch_count=12
author_directional_mismatch_count=0
```

Mismatch witnesses:

```text
point_id=136..146 and 183
core_neighbor_count=8
lower_index_core_neighbor_count=8
higher_index_core_neighbor_count=0
```

Clean AuthorOfficial 1K:

```text
point_count=1000
core_count=329
component_sizes=[90,168,181]
noise_count=561
total_time_sec=1.27797
```

Clean AuthorOfficial 16K:

```text
point_count=16000
core_count=12625
component_count=22
noise_count=2347
total_time_sec=96.3741
```

Regression:

```text
py -m unittest tests.goal5107_rt_dbscan_uci_3droad_contract_analysis_test tests.goal5094_rt_dbscan_authorofficial_component_signature_gate_test tests.goal5101_component_partition_helpers_test tests.goal5104_rt_dbscan_author_warm_loop_runner_test
Ran 13 tests OK
```

## Review Questions

1. Does the author-source contract interpretation (`callNum == 2 && xID >
   primID`) correctly explain why some conventional DBSCAN border points remain
   noise in AuthorOfficial?
2. Does the 1K analysis convincingly show that the Goal5106 mismatch is a
   contract mismatch rather than a core predicate mismatch?
3. Is `author_directional_mismatch_count=0` sufficient to replace the
   conventional CPU reference as the correct app-side comparator for this pinned
   author binary?
4. Are the 12 mismatch witnesses (lower-index core neighbors only, no
   higher-index core neighbors) strong enough evidence for the directional
   border rule?
5. Is the teardown skip patch correctly scoped as comparator/runtime stability
   only, with no DBSCAN semantic change?
6. Are the clean 1K and 16K AuthorOfficial outputs valid same-source diagnostic
   artifacts after the teardown patch?
7. Does the packet correctly avoid claiming exact paper input reproduction,
   RTDL 3DRoad correctness, or performance?
8. Does the manifest/register update preserve all carry-forward boundaries?
9. Are the tests sufficient for this diagnostic goal?
10. Should the next goal target RTDL 1K UCI 3DRoad correctness against the
    author-directional comparator, after or alongside fixing the POD Numba/PTX
    blocker?

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to the 10 review questions:
```

Preferred verdict label if approved:

```text
approve_goal5107_author_directional_border_contract_and_teardown_patch
```
