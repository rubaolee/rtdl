# RTDBSCAN Component-Signature Route Split

Status: V3 rebuild tutorial, one row-scoped M7 claim.

This lesson exists to prevent a common mistake: RTDBSCAN has several useful V3
routes, but they cannot be merged into one speedup claim.

## Four Rows, Four Meanings

| Evidence | What it proves | What it does not prove |
| --- | --- | --- |
| Old all-app ratio row | A route-health warning: route choices can produce huge ratios. | It does not prove RTDBSCAN is 1483x faster because `matches_reference` was null and routes were mixed. |
| First same-contract rerun | Embree and OptiX can produce the same component-size signature under the same Numba continuation contract. | It did not prove M7 performance: serious overall wins were only 1.150x, 1.079x, and 1.071x. |
| M23 grouped-stream component signature | A device-side component-signature route can avoid Python row materialization and match oracle/signature checks. | It has no same-scale Embree baseline for that grouped-stream contract. |
| Optimized repeat5 same-contract row | The prepared OptiX threshold path feeding the same Numba component-signature step is 1.102x to 1.236x faster than same-contract Embree on zero-noise synthetic clustered3d rows from 65,536 to 524,288 points. | It is not full DBSCAN, not RTDBSCAN paper reproduction, not broad V3-over-V2 evidence, and not a noisy-dataset or other-hardware claim. |

## Current M7 Row

Exact row:

```text
component_union_clustered3d_65536_524288_repeat5_row_scoped
```

Approved wording:

```text
RTDL V3 includes a generic component-signature continuation route where
prepared OptiX fixed-radius threshold columns feeding the same Numba component
signature are 1.102x to 1.236x faster end-to-end than the same-contract Embree
route on zero-noise four-cluster synthetic clustered3d rows from 65,536 to
524,288 points on an RTX 4000 Ada pod; at 262,144 and 524,288 points, the Numba
continuation still dominates wall time.
```

Current repeat5 table:

| Points | Repeat | Overall OptiX/Embree | RT-threshold phase | Continuation dominates OptiX |
| ---: | ---: | ---: | ---: | --- |
| 65,536 | 5 | 1.236x | 1.254x | false |
| 262,144 | 5 | 1.124x | 1.262x | true |
| 524,288 | 5 | 1.102x | 1.480x | true |

Large-scale correctness is OptiX/Embree intra-run canonical
component-signature agreement, not independent CPU reference validation.

## What To Learn

- Treat `component_signature` as a reviewed signature contract, not full DBSCAN
  labels.
- Keep same-contract comparisons separate from grouped-stream internal rows.
- Do not quote the RT threshold phase as whole RTDBSCAN speedup.
- Keep the zero-noise synthetic dataset, RTX 4000 Ada hardware, and continuation
  bottleneck caveats with the row.

## Source Packets

- `docs/rebuild/v3/phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_repeat5_final_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2ai_consensus_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_rtdbscan_same_contract_pod_evidence_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_rtdbscan_component_union_m7_feasibility_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_rtdbscan_continuation_bottleneck_no_go_2026-06-21.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/m23_dbscan_component_signature_524288.json`

## Claim Boundary

Allowed:

```text
Exactly `component_union_clustered3d_65536_524288_repeat5_row_scoped` is
M7-qualified as a row-scoped component-signature continuation claim.
```

Forbidden:

```text
Do not claim RTDBSCAN V3 is 1483x faster.
Do not claim component_signature is full DBSCAN labels.
Do not claim M23 grouped-stream evidence proves same-contract DBSCAN speedup.
Do not claim full RTDBSCAN or full DBSCAN is M7-qualified.
Do not claim the row generalizes to noisy datasets, irregular clusters, other
hardware, V2 comparison, or full applications.
```
