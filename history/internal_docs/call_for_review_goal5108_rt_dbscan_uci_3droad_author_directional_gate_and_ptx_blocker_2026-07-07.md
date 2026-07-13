# Call For Review - Goal5108 RT-DBSCAN UCI 3DRoad Author-Directional Gate And PTX Blocker

Please strictly review Goal5108:

```text
history/internal_docs/goal5108_rt_dbscan_uci_3droad_author_directional_gate_and_ptx_blocker_2026-07-07.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py
tests/goal5108_rt_dbscan_author_directional_gate_test.py
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_author_directional_gate_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_author_goal5107_clean.jsonl
Paper-reproduction-apps/rt-dbscan-paper/data/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
history/internal_docs/rt_dbscan_review_opinions_register_2026-07-07.md
```

## Context

Goal5107 diagnosed the 1K UCI 3DRoad mismatch as a pinned AuthorOfficial
directional border-assignment contract: conventional DBSCAN mismatched 12
points, but an author-directional reference mismatched 0 points.

Goal5108 claims to make that comparator executable in the app runner and to
narrow the remaining RTDL OptiX+Numba blocker.

## Claimed Outcome

```text
author_directional_app_gate_matches_1k_author_payload__rtdl_optix_numba_still_ptx_blocked
```

The report claims:

- `run_authorofficial_component_signature_gate.py` now supports
  `--backend author_directional_cpu_reference`.
- On the 1K UCI 3DRoad same-source candidate, that backend matches the clean
  AuthorOfficial payload exactly:

```text
matched=true
signature_matched=true
component_partition_matched=true
core_flags_matched=true
```

- The conventional CPU reference still mismatches the same payload, so the
  comparator distinction is behaviorally covered.
- The author-directional backend is app-owned and not exported as RTDL core.
- The RTDL OptiX+Numba route still cannot run on the POD because a minimal
  Numba CUDA kernel fails with PTX 8.7 vs PTX 8.4 support mismatch.
- This is not a correctness result for RTDL on 3DRoad.

## Review Questions

1. Does the new `author_directional_cpu_reference` backend correctly encode the
   Goal5107 author call-2 contract without promoting it into RTDL core?
2. Does the new 1K summary show a real AuthorOfficial match
   (`matched/signature/component_partition/core_flags` all true)?
3. Does the test suite correctly keep the conventional CPU reference mismatch
   visible, rather than silently replacing it?
4. Is the author-directional backend properly labeled as app-owned, not
   conventional DBSCAN and not a generic RTDL primitive?
5. Are the manifest/register/README updates consistent with the bounded claim?
6. Is the POD PTX diagnosis credible: Numba emits PTX 8.7 while the active
   driver/linker path accepts PTX 8.4?
7. Did the attempted remediations reasonably narrow the blocker without
   mutating RTDL semantics?
8. Does the report correctly avoid claiming RTDL 3DRoad correctness,
   performance, or exact paper reproduction?
9. Are the tests sufficient for this app-comparator gate?
10. Is the recommended Goal5109 direction correct: fix GPU partner environment
    or choose another validated GPU partner route before claiming RTDL 3DRoad
    correctness?

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
approve_goal5108_author_directional_app_gate__rtdl_ptx_blocker_carried
```
