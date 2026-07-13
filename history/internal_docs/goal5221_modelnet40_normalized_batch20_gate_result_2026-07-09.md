# Goal5221 ModelNet40 Normalized Batch20 Gate Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_normalized_batch20_gate__19_of_20_matched_one_author_rerun_mismatch
```

## Purpose

Goal5220 showed that five unique ModelNet40 pairs across five categories match
the paper-branch log when using:

```text
official public raw OFF + author -normalize=true
```

and that RTDL's generic route matches the normalized author output for those
same inputs.

Goal5221 broadens this to 20 unique pairs, preferring distinct ModelNet40
categories, to test whether the normalized-public-OFF reconstruction contract is
stable enough to promote beyond small-batch evidence.

## Method

Input log index:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
```

Public data:

```text
/tmp/xhd-modelnet40/ModelNet40.zip
```

Selection:

```text
strategy = smallest_unique_pairs_preferring_distinct_categories
requested_max_pairs = 20
selected_count = 20
```

Important correction versus the first exploratory batch attempt:

```text
author hd_exec reruns now pass paper-log NumPointsPerCell via -n_points_cell.
```

This matters because the paper-branch log records `NumPointsPerCell=8` for the
selected ModelNet40 records, while the author binary default is 15.

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5221_modelnet40_normalized_batch20_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5221_modelnet40_normalized_batch20_artifacts_2026-07-09.tar.gz
```

## Result Summary

```text
selected_count = 20
matched_case_count = 19
all_cases_matched = false
```

The pass/fail rule is strict:

```text
case_matched =
  author normalized HDResult matches paper log
  AND author normalized MBRs match paper log
  AND RTDL normalized route matches author normalized HDResult
```

## Passing Cases

Nineteen cases passed all three checks:

| case | category | point counts | paper HDResult | author-paper diff | MBR match | RTDL-author diff |
|---:|---|---:|---:|---:|---|---:|
| 0 | glass_box | 1107 + 1200 | 0.22594279050827026 | 0.0 | true | 5.288031956762751e-08 |
| 1 | cone | 1694 + 2726 | 0.5204525589942932 | 0.0 | true | 3.234579470934307e-08 |
| 2 | bowl | 3580 + 3026 | 0.4354671835899353 | 0.0 | true | 4.740150061355308e-08 |
| 3 | door | 5165 + 5040 | 0.40083712339401245 | 0.0 | true | 1.6569232041963033e-08 |
| 4 | wardrobe | 5164 + 7127 | 0.5185111165046692 | 0.0 | true | 2.760373485344303e-08 |
| 5 | cup | 6515 + 7377 | 0.4409995675086975 | 0.0 | true | 1.1439352742836917e-08 |
| 7 | stool | 7490 + 15723 | 0.3204610347747803 | 0.0 | true | 2.480902305812549e-08 |
| 8 | bottle | 13248 + 17294 | 0.16716471314430237 | 0.0 | true | 1.7815695252387798e-08 |
| 9 | lamp | 15639 + 16854 | 0.5426021218299866 | 0.0 | true | 1.1170203562116399e-07 |
| 10 | bathtub | 15788 + 18108 | 0.25528034567832947 | 0.0 | true | 1.1452990056337597e-08 |
| 11 | night_stand | 15144 + 19260 | 0.48401525616645813 | 0.0 | true | 7.622047326627523e-09 |
| 12 | sink | 19345 + 18492 | 0.8123759031295776 | 0.0 | true | 6.249583295314665e-09 |
| 13 | bench | 17637 + 20832 | 0.7183098196983337 | 0.0 | true | 3.1896707497480747e-13 |
| 14 | tv_stand | 23510 + 18988 | 0.5844879746437073 | 0.0 | true | 4.265781916590328e-08 |
| 15 | tent | 28629 + 13874 | 0.5462191700935364 | 0.0 | true | 3.282378813196374e-08 |
| 16 | monitor | 20237 + 24220 | 0.28980961441993713 | 0.0 | true | 1.552928347026139e-08 |
| 17 | toilet | 24680 + 23166 | 0.24103166162967682 | 0.0 | true | 1.7364701621058742e-09 |
| 18 | person | 28671 + 24580 | 0.5544348359107971 | 0.0 | true | 5.1045972115915106e-08 |
| 19 | table | 33176 + 23912 | 0.328748494386673 | 0.0 | true | 1.2485555755947786e-08 |

These cases support:

```text
public raw OFF + author NormalizePoints + paper-log NumPointsPerCell
```

as a strong reconstruction contract for many ModelNet40 paper-branch records.

## Failing Case

One selected case did not satisfy the strict author-rerun gate:

```text
case = range_hood_0124.off -> range_hood_0004.off
point counts = 11578 + 9530
paper log HDResult = 0.46497631072998047
author current rerun HDResult = 0.466653436422348
author-paper diff = 0.0016771256923675537
MBR match = true
```

The RTDL route result for the same normalized public input was:

```text
RTDL route directed_a_to_b = 0.46497629417671404
RTDL vs paper-log diff ~= 1.6553e-08
RTDL vs current-author-rerun diff ~= 0.001677142245633978
```

This is important:

```text
RTDL matches the paper-log scalar for the failing case, while the current
author `-variant rt` rerun does not.
```

The original paper-branch log for this case reports `Algorithm = Hybrid` in
the repeat payload, while the current author rerun reports `Algorithm = XHD`.
The current binary exposes `-variant clover`, but a direct `clover` probe on
this case aborted with a CUDA illegal memory access in the current build, so it
is not usable evidence.

Therefore the failing case is not currently evidence that public normalized OFF
is wrong. It is evidence that the author-rerun comparator still has an
algorithm/regime mismatch for at least one paper-branch ModelNet40 record.

## Interpretation

Goal5221 materially strengthens ModelNet40 provenance:

```text
19 / 20 unique pairs across 20 categories pass author normalized paper-log
matching and RTDL normalized route matching.
```

But it also prevents overclaim:

```text
1 / 20 exposes a paper-branch Algorithm=Hybrid vs current-rerun Algorithm=XHD
boundary.
```

The correct status is:

```text
ModelNet40 normalized public OFF is a strong but not complete reconstruction
candidate. It is not yet an all-pair reproduction.
```

## What This Proves

```text
The normalized-public-OFF contract is robust across at least 19 unique
ModelNet40 paper-branch pairs from 19 categories.

For those passing cases, public raw OFF + author NormalizePoints +
paper-log NumPointsPerCell exactly reproduces paper-branch author HDResult and
MBRs, and RTDL matches the same normalized author output within tolerance.

The X-HD app's OFF/normalize support remains app-owned; RTDL core still
consumes generic coordinate columns and nearest/frontier/reduction APIs.
```

## What This Does Not Prove

```text
all 400 unique ModelNet40 pairs reproduced;
the range_hood failing author-rerun case resolved;
exact paper input byte identity or hashes;
BraTS/geospatial/Stanford exact paper inputs;
author-vs-RTDL performance ratio;
author algorithm parity;
full X-HD paper reproduction.
```

## Claim Boundary

Allowed:

```text
A 20-pair ModelNet40 normalized-public-OFF batch passed 19 cases and exposed
one author-rerun algorithm/regime mismatch. The normalized-public-OFF contract
is now strong ModelNet40 provenance evidence, but not a complete all-pair
proof.
```

Not authorized:

```text
ModelNet40 fully reproduced;
all ModelNet40 pairs match;
range_hood failure resolved;
exact paper dataset identity proved;
author-vs-RTDL ratio;
full X-HD paper reproduction complete.
```

## Next Recommendation

Do not broaden the batch again until the single failing case is understood.
The next goal should target the comparator/regime mismatch:

```text
Goal5222: investigate the range_hood paper-branch Algorithm=Hybrid vs current
author XHD rerun mismatch. Determine whether the original paper-branch hybrid
variant is buildable/runnable, whether another public flag combination
reproduces the paper log, or whether the paper log value should be treated as
exact/reference while current author rerun cannot reproduce that one record.
```

Only after resolving or explicitly classifying that mismatch should the project
promote ModelNet40 beyond "strong reconstruction candidate with one known
rerun mismatch."
