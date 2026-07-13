# Call For Review: Goal5220 ModelNet40 Normalized Batch Gate

Date: 2026-07-09

Please strictly review Goal5220.

Primary report:

```text
history/internal_docs/goal5220_modelnet40_normalized_batch_gate_result_2026-07-09.md
```

Evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5220_modelnet40_normalized_batch_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5220_modelnet40_normalized_batch_artifacts_2026-07-09.tar.gz
```

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
```

## Context

Goal5218 showed that public raw ModelNet40 OFF files are count-compatible with
one paper-branch pair but do not match paper HDResult without preprocessing.

Goal5219 found the missing contract for that one pair:

```text
official public raw OFF + author -normalize=true
```

exactly reproduces the author paper-branch HDResult and logged MBRs, and RTDL
matches the normalized author output within float-author tolerance.

Goal5220 extends that from one pair to a small batch.

## Key Evidence

Selection:

```text
strategy = smallest_unique_pairs_preferring_distinct_categories
selected_count = 5
categories = glass_box, cone, bowl, door, wardrobe
```

All selected cases passed:

```text
matched_case_count = 5
all_cases_matched = true
```

Per-case summary:

```text
glass_box: author paper diff 0.0, MBR match true, RTDL-author diff 5.288e-08
cone:      author paper diff 0.0, MBR match true, RTDL-author diff 3.235e-08
bowl:      author paper diff 0.0, MBR match true, RTDL-author diff 4.740e-08
door:      author paper diff 0.0, MBR match true, RTDL-author diff 1.657e-08
wardrobe:  author paper diff 0.0, MBR match true, RTDL-author diff 2.760e-08
```

Claim boundary in JSON:

```text
modelnet40_batch_normalized_contract_claimed = true
modelnet40_all_pairs_reproduced = false
exact_paper_dataset_identity_proved = false
author_vs_rtdl_ratio_claimed = false
full_xhd_paper_reproduction_claimed = false
```

## Requested Verdict Labels

Choose one:

```text
approve_goal5220_modelnet40_normalized_batch_gate
approve_with_required_amendments
revise_goal5220_before_promoting_modelnet40_status
block_due_to_invalid_batch_or_overclaim
```

## Review Questions

1. Does the batch selection genuinely use unique paper-branch ModelNet40 pairs,
   not duplicate log entries for the same pair?

2. Is selecting five pairs across five categories sufficient to support the
   narrow claim "strong reconstruction candidate", while still insufficient for
   "all ModelNet40 reproduced"?

3. Does the evidence show that author `hd_exec -normalize=true` exactly matches
   the paper-branch HDResult and MBRs for all five selected cases?

4. Does the RTDL route comparison remain appropriately bounded to normalized
   same-input correctness under `1e-6` float-author tolerance?

5. Does the report avoid author-vs-RTDL performance ratios and avoid using the
   batch run timings as a performance matrix?

6. Does the app-owned OFF + normalize support preserve the principle that RTDL
   core remains generic and X-HD/ModelNet40 input semantics stay in the paper
   app?

7. Is the recommended next step correct: broaden the ModelNet40 batch before
   promoting the dataset provenance matrix beyond "strong reconstruction
   candidate"?

8. Are any additional facts required before this batch can be used as
   provenance evidence?

## Expected Answer Shape

```text
Verdict:
<one requested verdict label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers:
1. ...
...
8. ...
```

## Non-Authorization Boundary

This review must not authorize:

```text
ModelNet40 full reproduction complete;
all ModelNet40 pairs match;
public raw OFF is exact paper input without preprocessing;
exact paper dataset identity proved;
author-vs-RTDL speedup or parity;
full X-HD paper reproduction complete.
```
