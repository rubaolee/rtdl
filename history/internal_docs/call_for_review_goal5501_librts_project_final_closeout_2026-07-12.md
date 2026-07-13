# Final Call For Review: Goal5501 LibRTS Project Closeout

This is the only planned external review after the Goal5500 consolidated
review. Please review the complete LibRTS workstream at its final bounded
closeout boundary. No intermediate review is requested or required.

## Scope

Review Goals5482-5501 as one final packet. Goals5482-5491 were previously
approved and are included as baseline evidence. Goals5492-5500 were approved
as bounded evidence by the consolidated review. Goal5501 adds the required
mismatch diagnostic and final project boundary.

## Files To Review

```text
history/internal_docs/goal5501_librts_project_closeout_mismatch_diagnosis_result_2026-07-12.md
history/internal_docs/review_librts_goals5492_5500_consolidated_2026-07-12.md
history/internal_docs/call_for_review_librts_goals5482_5500_consolidated_2026-07-12.md
Paper-reproduction-apps/librts-paper/data/manifest.json
Paper-reproduction-apps/librts-paper/run_goal5501_range_intersects_mismatch_diagnostic.py
Paper-reproduction-apps/librts-paper/results/librts_goal5500_range_intersects_batch_gate.json
Paper-reproduction-apps/librts-paper/results/goal5501/mismatch_diagnostic.json
Paper-reproduction-apps/librts-paper/results/goal5501/parks_bz2_capacity.json
tests/goal5501_librts_range_intersects_mismatch_diagnostic_test.py
tests/goal5501_librts_mismatch_diagnostic_result_test.py
```

## Final Evidence Questions

1. Does the Goal5501 diagnostic use same-source prefixes for author, RTDL,
   and independent CPU float64/float32 overlap oracles?
2. Are the three diagnostic results accurately represented: RTDL equals CPU32
   on all three feasible prefixes, author differs on the two parks prefixes,
   and author/RTDL agree on the lakes prefix?
3. Does the evidence avoid claiming that this prefix result proves the root
   cause of the full-input parks/lakes disagreements?
4. Is the `parks.bz2` full-input CUDA OOM correctly closed as a capacity
   boundary, while the 100k prefix is correctly treated only as a probe?
5. Does the final report preserve the distinction between exact input identity,
   count equality, relation equality, and performance equality?
6. Does the final project boundary accurately close the current engineering
   scope without claiming all 42 exact range-intersects pairs or Figure 6?
7. Does the RTDL implementation remain generic AABB/columnar functionality,
   with WKT parsing, provenance, author handling, and cache policy app-owned?
8. Does the final packet preserve the no-ratio rule and keep author internal
   query time separate from RTDL load/prepare/query phases?
9. Are the final tests evidence-based and do they fail closed if counts or
   claim flags change?
10. Is any further full-input mismatch/author-pair-row/capacity campaign
    correctly classified as a new scope rather than an untracked continuation?

## Final Claim Boundary

Approve only the following bounded statement:

```text
LibRTS has a generic columnar AABB route with verified official archive
provenance. The current paper-app campaign records exact count matches for
point-contains, range-contains, and three range-intersects cases. A six-case
range-intersects attempt found two full-input count disagreements and one
author CUDA allocation failure. Independent prefix diagnostics show RTDL
matching a generic CPU float32 AABB oracle on all feasible probes, but do not
fully adjudicate the author/RTDL full-input contract. The project is closed at
this bounded evidence boundary; full paper, complete matrix, relation parity,
performance parity, zero-copy, and Embree claims remain unmade.
```

## Forbidden Final Summaries

```text
full LibRTS paper reproduction
complete range-intersects matrix
all six exact range-intersects cases matched
RTDL matches the author on every input
RTDL is faster than the author
author performance parity
pointwise relation equality for Goal5500
parks.bz2 OOM resolved
Embree comparison
```

## Requested Verdict Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to final evidence questions 1-10:
Goal5501 status decision:
Final project-boundary decision:
Next-scope decision:
Requested verdict label:
```
