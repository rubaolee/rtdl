# Call for Review: Goal5473 LibRTS Exact Dataset Acquisition Decision

Please review:

```text
history/internal_docs/goal5473_librts_exact_dataset_acquisition_decision_2026-07-11.md
Paper-reproduction-apps/librts-paper/results/librts_goal5473_dataset_acquisition_decision.json
Paper-reproduction-apps/librts-paper/build_dataset_acquisition_decision.py
tests/goal5471_5472_librts_full_target_and_author_log_matrix_test.py
```

Questions:

1. Is Zenodo v2 size/MD5 provenance pinned correctly?
2. Is the 12.10-hour estimate correctly derived from the measured transfer rate?
3. Does the report avoid treating direct SharePoint 401 as permanent loss?
4. Is deferring the 23.1 GB download on the 8 GB VRAM / 16 GB RAM host correct?
5. Is the proposed 24 GB VRAM / 64 GB RAM / 70 GB disk POD floor justified by
   the official paper guidance and archive size?
6. Is POD correctly unnecessary for more metadata work but required for exact
   dataset execution?
7. Are all exact-data, figure, ratio, and Embree claims still fail-closed?

Requested verdict:

```text
approve_goal5473_librts_exact_dataset_acquisition_deferred_to_suitable_host
```
