# Goal5224 - ModelNet40 Algorithm-Aware Batch40 Gate Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_algorithm_aware_batch40_gate__40_categories_40_of_40_matched
```

Goal5224 expands Goal5223 from 20 selected ModelNet40 paper-log records to one
selected record from each of the 40 ModelNet40 categories. The comparator is
algorithm-aware: it reads the original author paper-log blob, extracts
`Running.Repeats[*].Algorithm`, and selects the author binary/variant
accordingly.

## Evidence Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5224_modelnet40_algorithm_aware_batch40_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5224_modelnet40_algorithm_aware_batch40_artifacts_2026-07-09.tar.gz
```

## Batch Scope

The paper-log index contains:

```text
ModelNet40 normalized records = 2000
unique pairs                  = 400
categories                    = 40
```

Goal5224 selects one unique pair per category using the existing selection
policy:

```text
smallest_unique_pairs_preferring_distinct_categories
```

Selected categories:

```text
airplane, bathtub, bed, bench, bookshelf, bottle, bowl, car, chair, cone,
cup, curtain, desk, door, dresser, flower_pot, glass_box, guitar, keyboard,
lamp, laptop, mantel, monitor, night_stand, person, piano, plant, radio,
range_hood, sink, sofa, stairs, stool, table, tent, toilet, tv_stand, vase,
wardrobe, xbox
```

## Result

```text
schema = rtdl.paper_reproduction.xhd.modelnet40_normalized_batch_gate.v2
selected_count = 40
matched_case_count = 40
all_cases_matched = true
category_count = 40
observed author algorithms = Hybrid for 40 / 40 cases
max author-vs-paper HDResult diff = 0.0
max RTDL-vs-author HDResult diff  = 2.8723411737985316e-07
MBR matched cases                 = 40 / 40
```

This means:

```text
For one selected pair from every ModelNet40 category, official public OFF files
plus author-compatible normalization reproduce the paper-log HDResult under the
paper-branch Hybrid author comparator; RTDL's normalized route matches that
author comparator within 1e-6.
```

The previously problematic `range_hood` category is included in this 40-case
batch and passes under the paper-branch Hybrid comparator.

## What This Proves

- The ModelNet40 public OFF + author normalization reconstruction hypothesis is
  now supported across all 40 categories, one selected pair per category.
- The selected 40 paper-log records all require the paper-branch Hybrid
  comparator, not current main/rt.
- RTDL's app-owned OFF loader + normalization + generic route matches the
  algorithm-aware author comparator for all 40 selected cases.

## What This Does Not Prove

This still does **not** prove:

```text
all 400 unique ModelNet40 pairs
all 2000 ModelNet40 paper-log records
exact paper input byte identity / hashes
author-vs-RTDL performance ratio
ModelNet40 paper performance reproduction
full X-HD paper reproduction
```

It is a strong Level-B ModelNet40 representative batch, not Level-C exact
dataset proof.

## Next Step

The next decision is whether to expand ModelNet40 to all 400 unique pairs or
freeze this 40-category batch as representative evidence and move to another
paper workload family.

Recommended next goal if continuing ModelNet40:

```text
Goal5225: algorithm-aware ModelNet40 all-unique-pair feasibility plan
```

That goal should estimate runtime, storage, and failure handling before running
all 400 pairs. It must keep the same claim boundary: no exact byte-identity
claim and no performance ratio.
