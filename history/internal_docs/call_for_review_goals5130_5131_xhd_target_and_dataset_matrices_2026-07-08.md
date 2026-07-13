# Call For Review - Goals5130-5131 X-HD Target And Dataset Matrices

Please strictly review the X-HD full-paper-reproduction planning step covering
Goal5130 and Goal5131.

## Files To Review

```text
history/internal_docs/goal5130_xhd_paper_target_matrix_2026-07-08.md
history/internal_docs/goal5131_xhd_dataset_provenance_acquisition_matrix_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_dataset_provenance_matrix_2026-07-08.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Context

The X-HD app has completed only bounded same-input reproduction. Goal5129
approved entering the full-paper feasibility phase, with the required amendment
that Level C exact paper dataset reproduction must require file/hash/provenance
evidence. Summary statistics alone are not enough.

Goal5130 maps the paper targets. Goal5131 maps dataset provenance and acquisition
state. Neither goal implements a new RTDL route or claims new performance.

## Review Questions

1. Does Goal5130 correctly separate Table 1, Figure 5, Figure 6, Figure 7,
   Figure 8, Figure 9, Figure 10, and Figure 11 targets instead of collapsing
   them into a vague "full reproduction" claim?
2. Does Goal5130 correctly keep author `Running.AvgTime`, process wall, RTDL
   route time, setup/preprocess/load, and comparator/output as separate
   measurement boundaries?
3. Does Goal5130 avoid claiming any Figure 5-11 reproduction or author parity?
4. Does Goal5131 correctly implement the Goal5129 amendment: exact paper dataset
   reproduction requires files/hashes/provenance, and count/Gini/statistical
   matching is not sufficient?
5. Is the dataset classification honest: exact inputs unavailable, same-source
   candidates identified, and representative gates still not yet run?
6. Is Dragon-HappyBuddha a reasonable first Level B same-source representative
   gate, given public graphics-mesh availability, size, and lower license
   friction?
7. Does the matrix avoid reclassifying historical `hausdorff_xhd` benchmark
   evidence as X-HD paper reproduction?
8. Are the claim boundaries clean: no exact paper dataset claim, no figure claim,
   no performance ratio, no X-HD algorithmic-route claim?
9. Should Goal5132 be authorized only as a Level B same-source representative
   gate unless exact author input files or hashes are found?
10. Are there any missing paper targets or dataset provenance blockers that must
    be added before proceeding?

## Expected Answer Shape

```text
Verdict: approve | approve_with_required_amendments | block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to 10 review questions:
1. ...
...
10. ...
```

## Requested Verdict Label

If acceptable:

```text
approve_goals5130_5131_xhd_target_and_dataset_matrices__level_b_next_exact_blocked
```
