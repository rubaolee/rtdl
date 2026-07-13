# Call For Review - Goal5106 RT-DBSCAN UCI 3DRoad Same-Source Candidate

Please strictly review Goal5106:

```text
history/internal_docs/goal5106_rt_dbscan_uci_3droad_same_source_candidate_2026-07-07.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/prepare_uci_3droad_author_input.py
Paper-reproduction-apps/rt-dbscan-paper/data/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
Paper-reproduction-apps/rt-dbscan-paper/data/paper_dataset_candidates.json
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_author_2d_zero_z_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_16k_author_2d_zero_z_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_full_author_2d_zero_z_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_cpu_author_payload_compare_summary.json
```

## Context

Goal5105 identified 3DRoad as the safest first exact-paper provenance target,
but warned that the public UCI source is not automatically the author's exact
preprocessed paper input. Goal5106 downloaded/pinned UCI 3DRoad, transformed it
into an author-readable three-column candidate, and attempted a POD smoke.

## Claimed Outcome

```text
uci_3droad_same_source_candidate_created__not_clean_exact_gate
```

The report claims:

- UCI 3DRoad source is downloaded, extracted, and SHA256-pinned.
- Deterministic author-format candidates were generated for 1K, 16K, and full
  434,874 rows using `(longitude, latitude, 0.0)`.
- This is a same-source candidate only, not author `3droad_full.csv`.
- Patched AuthorOfficial produces a 1K payload/timing but exits with `SIGSEGV`
  during teardown.
- 1K author payload and CPU reference agree on core flags/core count, but not on
  component partition/signature.
- 16K author reaches timing output but also exits with `SIGSEGV`.
- RTDL OptiX+Numba could not run on the POD because of a PTX version mismatch.

## Review Questions

1. Is the UCI source pinning and hash evidence sufficient for a same-source
   public 3DRoad candidate?
2. Is the `(longitude, latitude, 0.0)` transform an acceptable candidate route
   given the paper's "2D latitude/longitude" statement and author three-float
   input contract?
3. Does the report correctly avoid claiming this is the author's exact
   `3droad_full.csv` or exact paper input?
4. Does the 1K result correctly distinguish core predicate agreement from
   component-partition mismatch?
5. Is the teardown `SIGSEGV` handled honestly as blocking a clean AuthorOfficial
   gate, even though JSON/timing are produced?
6. Is the 16K result correctly treated as diagnostic only because the author
   process exits with `SIGSEGV`?
7. Is the RTDL OptiX+Numba failure correctly classified as an environment/PTX
   blocker rather than a correctness result?
8. Are the recommended next routes correct: reduce the component mismatch,
   stabilize AuthorOfficial teardown, and then fix the POD Numba/PTX mismatch?
9. Does this packet avoid paper-performance, author-parity, and exact-paper
   reproduction claims?
10. Should Goal5106 close as
    `uci_3droad_same_source_candidate_created__not_clean_exact_gate`?

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
approve_goal5106_uci_3droad_same_source_candidate_not_clean_gate
```
