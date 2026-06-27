# Goal1273 v1.2 Validated Pod Findings And Next Steps

Date: 2026-05-05

Status: internal v1.2 evidence interpretation. This report does not authorize
public RTX speedup wording, public release claims, release gates, tags, or new
backend scope.

## Source Evidence

- Intake: `docs/reports/goal1272_v1_2_targeted_pod_intake_2026-05-05.md`
- Pod copy-back: `docs/reports/goal1267_live_pod_2026-05-05`
- Result archive SHA256:
  `2e4946068a1d305d884faac5e787b97168042897b6724fcf35e634d69efdb5e1`
- Pod environment: Ubuntu, NVIDIA RTX A5000, driver `550.127.08`, CUDA toolkit
  `13.0`, OptiX headers from `/root/vendor/optix-dev`
- Artifact status: `failed_count=0`, `missing_artifacts=0`

## Summary

The second Goal1267 pod run completed the missing environment probe, graph
prepared-repeat artifacts, and Embree DB baselines. Goal1272 now validates the
artifact set and classifies the current internal v1.2 result as:

| App row | Internal outcome | Key evidence |
| --- | --- | --- |
| `graph_analytics` | `optix_improved` | OptiX total beats Embree at 30k and 60k copies; prepared-repeat query mean is tens of microseconds. |
| `database_analytics` | `optix_improved` | Sales-risk warm-query median beats Embree at 100k and 300k copies under compact-summary contract. |
| `polygon_pair_overlap_area_rows` | `optix_improved` | OptiX candidate discovery beats Embree at 40k, 80k, and 160k copies; positive-pair parity is true. |
| `polygon_set_jaccard` | `optix_still_slower_with_reason` | Chunk `1024` remains correctness-safe and parity-clean, but OptiX candidate discovery is still slower than Embree. |

This is a meaningful internal v1.2 improvement over the earlier partial
copy-back, but it is still not public wording. Public claims need an exact
sub-path wording packet plus required external review.

## Detailed Findings

### Graph Analytics

| Copies | Embree query sec | OptiX total sec | Total ratio | Prepared repeat mean sec | Repeat ratio |
| ---: | ---: | ---: | ---: | ---: | ---: |
| `30000` | `8.79577` | `1.27866` | `6.87889` | `0.0000722098` | `121809` |
| `60000` | `2.79877` | `0.993101` | `2.81821` | `0.000100736` | `27783.2` |

Interpretation:

- The graph path is now internally positive under the measured summary
  visibility contract.
- The repeated any-hit query itself is extremely fast; the remaining wall time
  is dominated by `scene_prepare_sec`, `blocker_pack_sec`, `ray_pack_sec`, and
  input construction.
- This supports v1.3/v1.5 work on prepared scene reuse and generic
  `ANY_HIT`/`COUNT_HITS` primitive boundaries rather than kernel
  micro-optimization.
- This does not cover BFS, triangle counting, graph-database analytics, or
  graph reductions.

### Database Analytics

| Copies | Embree warm median sec | OptiX warm median sec | Ratio | Native counter status |
| ---: | ---: | ---: | ---: | --- |
| `100000` | `0.636918` | `0.421495` | `1.51109` | `exported` |
| `300000` | `1.75629` | `1.26793` | `1.38517` | `exported` |

Interpretation:

- Sales-risk compact-summary warm-query timing is now internally positive at
  both retained scales.
- The evidence is limited to the compact summary contract with
  `row_materializing_operation_count=0`; it is not a DBMS, SQL, broad database,
  or row-materializing claim.
- v1.3 should capture this as a primitive/ABI requirement for summary-style
  count or predicate reduction paths, not as a general database engine claim.

### Polygon Pair Overlap Area Rows

| Copies | Embree candidate sec | OptiX candidate sec | Ratio | Positive-pair parity | Candidate diagnostic |
| ---: | ---: | ---: | ---: | --- | --- |
| `40000` | `10.1272` | `4.58619` | `2.20819` | `true` | conservative upper-bound delta `-40000` |
| `80000` | `21.3146` | `10.7915` | `1.97513` | `true` | conservative upper-bound delta `-80000` |
| `160000` | `41.8981` | `19.7338` | `2.12326` | `true` | conservative upper-bound delta `-160000` |

Interpretation:

- Candidate discovery is internally positive at all retained scales.
- Goal1270’s diagnostic split remains important: conservative candidate
  upper-bound equality is false, while final positive-pair parity is true.
- The exact-area continuation is still a native continuation, not yet a generic
  v1.5 primitive. v1.3 must document whether this lowers to
  `ANY_HIT`/`COUNT_HITS` plus a reduction or remains app-specific until v1.4.

### Polygon Set Jaccard

| Copies | Chunk | Embree candidate sec | OptiX candidate sec | Ratio | Positive-pair parity |
| ---: | ---: | ---: | ---: | ---: | --- |
| `4096` | `1024` | `1.07280` | `1.44806` | `0.740851` | `true` |
| `8192` | `1024` | `1.73172` | `2.11099` | `0.820336` | `true` |

Interpretation:

- Jaccard remains slower than Embree under the reviewed safe chunk policy.
- This is still useful: correctness, chunk policy, and positive-pair parity are
  clean, so the row can close as `optix_still_slower_with_reason`.
- The likely next problem is not basic RT-core availability; it is chunking,
  pair collection, and exact/native continuation overhead. This is v1.3/v1.5
  design input for bounded collection and reduction primitives.

## Architecture Consequences

The v1.2 result supports the roadmap direction:

- v1.2 can close the immediate NVIDIA evidence gap for the four targeted rows.
- v1.3 should formalize primitive boundaries and migration gates before more
  native refactor work.
- v1.4 should begin replacing app-name-specific continuation code with wrapper
  slices only after v1.3 defines parity, dtype, tolerance, and result-shape
  contracts.
- v1.5 should expose a reviewed generic traversal-plus-reduction backend
  surface, not a universal compute engine.

The immediate primitive pressure from this evidence is:

| Primitive pressure | Evidence source | Why it matters |
| --- | --- | --- |
| `ANY_HIT` | graph visibility, polygon pair, Jaccard | Traversal predicate is the common core. |
| `COUNT_HITS` | graph summary, DB summary-like paths | Summary outputs need counts without Python row materialization. |
| `REDUCE_INT(COUNT|SUM)` | DB compact summary, graph summary | Avoid row-materializing Python continuations for common analytics. |
| `REDUCE_FLOAT(SUM)` | polygon areas and future Jaccard scoring | Needed to retire app-specific exact/native continuation boundaries. |
| `COLLECT_K_BOUNDED` | Jaccard and candidate-pair workflows | Useful but should remain experimental until scalar reductions are stable. |

## Next Steps

1. Write the v1.3 primitive ABI and per-app lowering matrix from this evidence.
2. Keep Jaccard as the primary still-slower diagnostic row; do not broaden its
   claim until chunk/collection overhead is solved.
3. Prepare a separate public-wording candidate packet only if the user wants to
   promote bounded graph, DB sales-risk, or polygon-pair wording. Treat that as
   a key goal requiring 3-AI consensus.
4. Do not spend new implementation effort on Vulkan, HIPRT, or Apple RT before
   v2.1.

## Boundary

This report is internal engineering interpretation. It may guide v1.3/v1.4/v1.5
planning, but it is not a public performance page and does not authorize public
RTX speedup wording.
