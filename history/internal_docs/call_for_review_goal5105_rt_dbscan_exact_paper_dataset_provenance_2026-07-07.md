# Call For Review - Goal5105 RT-DBSCAN Exact Paper Dataset Provenance

Please strictly review Goal5105:

```text
history/internal_docs/goal5105_rt_dbscan_exact_paper_dataset_provenance_2026-07-07.md
Paper-reproduction-apps/rt-dbscan-paper/data/paper_dataset_candidates.json
Paper-reproduction-apps/rt-dbscan-paper/data/README.md
Paper-reproduction-apps/rt-dbscan-paper/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
history/internal_docs/rt_dbscan_review_opinions_register_2026-07-07.md
```

## Context

After bounded RT-DBSCAN same-input and representative synthetic gates passed, the
owner selected the next path:

```text
pursue exact RT-DBSCAN paper dataset provenance
```

Goal5105 did not run a new performance benchmark. It audited the paper, the
pinned author artifact, public source candidates, and current RTDL paper app
inputs.

## Claimed Outcome

```text
exact_paper_inputs_not_pinned__candidate_sources_recorded
```

The report claims:

- The paper datasets are `3DRoad`, `NGSIM`, `Porto`, and `3DIono`.
- Candidate public sources are identified for `3DRoad`, `Porto`, and `NGSIM`;
  a TEC-source candidate and author-local filename hint exist for `3DIono`.
- The pinned AuthorOfficial artifact reads an input file from `av[1]` and does
  not package exact paper input files.
- The source comments mention local paths for `3D_iono.txt`, `porto.txt`, and
  `3droad_full.csv`; these are evidence of author-local preprocessed files, not
  packaged data.
- Exact paper dataset reproduction remains open.

## Review Questions

Please answer:

1. Does the report correctly identify the four paper datasets and the relevant
   paper workload policy from the RT-DBSCAN paper?
2. Does the report correctly distinguish public source datasets from exact
   author-preprocessed paper input files?
3. Is the inference about author preprocessed point streams reasonable, given
   that the pinned `hostCode.cpp` hardcodes `dim = 3` while the paper says 2D
   data are represented with z set to 0?
4. Does `paper_dataset_candidates.json` avoid overclaiming exact dataset
   reproduction?
5. Are 3DRoad, Porto, 3DIono, and NGSIM status labels accurate and sufficiently
   conservative?
6. Does the updated README/manifest/register preserve the boundary that the
   existing fixtures are synthetic same-input or representative inputs, not
   exact paper datasets?
7. Is the recommended Goal5106 split correct: exact-first route if the exact
   preprocessed input can be pinned, otherwise same-source public route with a
   non-exact label?
8. Are there any missing public data sources or paper references that should be
   added before closing this provenance audit?
9. Does this packet avoid author-performance parity, paper-performance, and full
   paper reproduction claims?
10. Should Goal5105 close as
   `exact_paper_inputs_not_pinned__candidate_sources_recorded`?

## Expected Answer Shape

Please provide:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to the 10 review questions:
```

Preferred verdict label if approved:

```text
approve_goal5105_exact_paper_dataset_provenance_candidates_recorded
```
