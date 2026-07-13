# Call For Review - Goal5109 RT-DBSCAN UCI 3DRoad OptiX+CuPy Semantic Gap

Please strictly review Goal5109:

```text
history/internal_docs/goal5109_rt_dbscan_uci_3droad_optix_cupy_semantic_gap_2026-07-07.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py
tests/goal5109_rt_dbscan_optix_cupy_author_contract_gap_test.py
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_optix_cupy_author_directional_gate_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_author_goal5107_clean.jsonl
Paper-reproduction-apps/rt-dbscan-paper/data/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
history/internal_docs/rt_dbscan_review_opinions_register_2026-07-07.md
```

## Context

Goal5107 diagnosed the 1K UCI 3DRoad same-source mismatch as an AuthorOfficial
directional border-assignment contract:

```text
conventional_mismatch_count=12
author_directional_mismatch_count=0
```

Goal5108 added an app-owned `author_directional_cpu_reference` backend that
matches the clean 1K AuthorOfficial payload, but the RTDL OptiX+Numba route was
blocked on the POD by PTX 8.7 vs 8.4 toolchain mismatch.

Goal5109 tries a different GPU partner route: existing generic RTDL
OptiX+CuPy grouped-stream component labels.

## Claimed Outcome

```text
optix_cupy_runs_1k_but_matches_conventional_not_author_directional_contract
```

The report claims:

- The POD can run `--backend optix_cupy_component_signature`.
- That backend uses existing generic RTDL OptiX+CuPy grouped-stream APIs.
- It does not add an RT-DBSCAN-specific core primitive.
- It fails the AuthorOfficial comparator:

```text
matched=false
signature_matched=false
component_partition_matched=false
core_flags_matched=true
```

- RTDL OptiX+CuPy produces:

```text
{core_count=329, component_sizes=[102,168,181], noise_count=549}
```

- AuthorOfficial produces:

```text
{core_count=329, component_sizes=[90,168,181], noise_count=561}
```

- Therefore the remaining 3DRoad gap is a semantic-contract mismatch, not only
  a Numba/PTX environment issue.
- Owner decision: do not open a new author-directional SoS / border-assignment
  route. RTDL SoS and degeneracy protocols were settled through the RayJoin line
  and are not reopened for RT-DBSCAN.

## Review Questions

1. Does the evidence show that the RTDL OptiX+CuPy route actually ran on the
   1K UCI 3DRoad same-source candidate?
2. Does the summary show a true comparator failure (`matched=false`,
   `signature_matched=false`, `component_partition_matched=false`) while core
   flags still match?
3. Is the report correct that this moves the diagnosis from "only environment
   blocker" to "semantic-contract gap also exists"?
4. Does the RTDL signature match the conventional CPU signature from Goals5107
   and 5108 rather than the AuthorOfficial directional signature?
5. Is the OptiX+CuPy backend generic/app-neutral enough, or does it smuggle
   DBSCAN/AuthorOfficial/RayJoin identity into RTDL core?
6. Does the report correctly refuse to call this an RTDL 3DRoad correctness
   pass?
7. Does the report correctly avoid performance claims?
8. Is it correct to keep the author `xID > primID` rule app-owned rather than
   promoting it as default RTDL DBSCAN semantics?
9. Are the new tests sufficient to keep this negative result from being
   relabeled as success later?
10. Is the recommended next decision fair: keep the generic RTDL route under the
    fixed RTDL protocol, stop targeting the pinned author's directional border
    behavior as a new semantic fork, and avoid relabeling the conventional RTDL
    result as AuthorOfficial reproduction?

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
approve_goal5109_optix_cupy_runs_but_author_contract_gap_remains
```
