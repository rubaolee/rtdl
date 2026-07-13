# Goal5220 ModelNet40 Normalized Batch Gate Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_normalized_public_off_batch_gate__5_of_5_pairs_matched
```

## Purpose

Goal5219 proved the normalized-public-OFF contract on one ModelNet40 pair:

```text
official public raw OFF + author -normalize=true
```

reproduced the paper-branch author HDResult and logged MBRs for
`glass_box_0115.off -> glass_box_0081.off`, and the RTDL generic route matched
that normalized author run.

Goal5220 tests whether that contract survives a small batch across multiple
ModelNet40 categories.

## Method

Input source:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
```

Public data source:

```text
/tmp/xhd-modelnet40/ModelNet40.zip
```

The ZIP remains POD-local and is not committed.

Selection strategy:

```text
smallest_unique_pairs_preferring_distinct_categories
max_pairs = 5
```

The batch script deduplicates repeated paper-branch records by input path, then
selects the smallest pairs while preferring distinct ModelNet40 categories.

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5220_modelnet40_normalized_batch_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5220_modelnet40_normalized_batch_artifacts_2026-07-09.tar.gz
```

The tarball contains per-case author JSON and RTDL route JSON from the POD run.

## Gate Contract

For each selected pair:

1. Extract official public raw OFF files from `ModelNet40.zip`.
2. Run author `hd_exec` with:

   ```text
   -input_type off
   -variant rt
   -execution gpu
   -normalize=true
   -check=false
   -repeat=1
   ```

3. Compare author normalized `HDResult` against the paper-branch log HDResult.
4. Compare author normalized MBRs against the paper-branch log MBRs.
5. Run the RTDL generic route with:

   ```text
   input_type = off
   normalize_each_input_to_author_unit_box = true
   backend = optix
   direction_mode = directed-a-to-b
   validation_mode = author-only
   tolerance = 1e-6
   ```

6. Require RTDL route output to match the author normalized HDResult.

## Results

Summary:

```text
selected_count = 5
matched_case_count = 5
all_cases_matched = true
```

Per-case outcomes:

| case | category | pair | point counts | paper HDResult | author paper diff | MBR match | RTDL-author diff | matched |
|---:|---|---|---:|---:|---:|---|---:|---|
| 0 | glass_box | `glass_box_0115 -> glass_box_0081` | 1107 + 1200 | 0.22594279050827026 | 0.0 | true | 5.288031956762751e-08 | true |
| 1 | cone | `cone_0080 -> cone_0161` | 1694 + 2726 | 0.5204525589942932 | 0.0 | true | 3.234579470934307e-08 | true |
| 2 | bowl | `bowl_0025 -> bowl_0057` | 3580 + 3026 | 0.4354671835899353 | 0.0 | true | 4.740150061355308e-08 | true |
| 3 | door | `door_0025 -> door_0014` | 5165 + 5040 | 0.40083712339401245 | 0.0 | true | 1.6569232041963033e-08 | true |
| 4 | wardrobe | `wardrobe_0032 -> wardrobe_0061` | 5164 + 7127 | 0.5185111165046692 | 0.0 | true | 2.760373485344303e-08 | true |

Route wall timings are present in the JSON but are not used for any performance
claim. This batch was run as a provenance/correctness gate, not as a stable
performance matrix.

## Interpretation

Goal5220 strengthens Goal5219 materially:

```text
5 distinct ModelNet40 pairs across 5 categories reproduce the paper-branch
author HDResult exactly when using official public raw OFF plus author
-normalize=true, and RTDL matches the same normalized author outputs under the
existing float-author tolerance.
```

This moves ModelNet40 from:

```text
one-pair normalized contract evidence
```

to:

```text
small-batch normalized public OFF reconstruction evidence
```

It still does not prove all 400 unique ModelNet40 pairs or exact paper dataset
identity for every paper workload.

## What This Proves

```text
For five unique ModelNet40 paper-branch pairs across five categories, official
public raw OFF files plus the author NormalizePoints transform reproduce the
paper-branch HDResult and logged MBRs.

For those same five pairs, the RTDL generic route on app-owned normalized OFF
input matches the normalized author HDResult within tolerance.

The X-HD app input bridge can consume OFF data and apply author-compatible
normalization without adding ModelNet40/OFF/X-HD semantics to RTDL core.
```

## What This Does Not Prove

```text
all ModelNet40 pairs reproduced;
all X-HD paper categories reproduced;
exact paper input bytes or hashes recovered;
BraTS/geospatial/Stanford exact paper inputs recovered;
author-vs-RTDL performance ratio;
author performance parity;
full X-HD paper reproduction;
X-HD fused RT-core algorithm equivalence.
```

## Claim Boundary

Allowed:

```text
ModelNet40 public raw OFF plus author -normalize=true is a strong reconstruction
candidate: a five-pair, five-category batch exactly matches paper-branch
HDResults/MBRs on the author binary and matches RTDL route outputs within
float-author tolerance.
```

Not authorized:

```text
ModelNet40 full reproduction complete;
all ModelNet40 pairs match;
public raw OFF is exact paper input without preprocessing;
exact paper dataset identity proved;
author-vs-RTDL speedup or parity;
full X-HD paper reproduction complete.
```

## Next Recommendation

Proceed to a larger ModelNet40 validation batch before promoting the dataset
status beyond "strong reconstruction candidate":

```text
Goal5221: run a broader ModelNet40 normalized batch, e.g. 20-40 unique pairs
across more categories, with the same author normalized and RTDL normalized
route gates.
```

If that broader batch passes, update the dataset provenance matrix to mark
ModelNet40 as:

```text
public_raw_off_plus_author_normalize_contract_reconstructs_observed_paper_branch_logs
```

not as:

```text
exact byte-identical paper inputs recovered
```
