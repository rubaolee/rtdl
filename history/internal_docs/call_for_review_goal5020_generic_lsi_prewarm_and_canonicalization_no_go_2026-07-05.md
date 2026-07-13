# Call For Review: Goal5020 Generic LSI Prewarm And Canonicalization No-Go

Please review:

```text
history/internal_docs/goal5020_generic_lsi_prewarm_productized_and_canonicalization_no_go_2026-07-05.md
history/internal_docs/rtdl_goal5020_sort_baseline_top4.json
history/internal_docs/rtdl_goal5020_hash_canonical_top4.json
history/internal_docs/rtdl_goal5020_flat_hash_canonical_top4.json
history/internal_docs/rtdl_goal5020_generic_lsi_prewarm_top4.json
history/internal_docs/rtdl_goal5020_generic_lsi_prewarm_repeat_top4.json
tests/goal5020_generic_lsi_prewarm_cli_test.py
```

## Requested Verdict Label

```text
approve_goal5020_generic_lsi_prewarm_productized__cpu_hash_no_go
```

## Review Questions

1. Does the duplicate-structure audit justify rejecting a linear adjacent-run
   canonicalization path?
2. Do the `hash` and `flat_hash` POD probes correctly show that CPU hash
   duplicate canonicalization is slower than the current sort path, while
   preserving structural anchors?
3. Is it correct that the failed CPU hash probes were not kept in source, and
   only their artifacts/report remain?
4. Does the new `--generic-lsi-prewarm` CLI use the public generic LSI front
   door rather than a RayJoin-specific core shortcut?
5. Does the summary correctly keep prewarm time separate from
   `writer_free_hot_sec` and block cold CLI one-shot / 10x / query-many claims?
6. Does the POD repeat protocol support saying the warm-process fresh route
   moves to about `2.386s` median under `--generic-lsi-prewarm`, with stable
   structural anchors?
7. Is it correct to classify this as a useful warm-process fresh improvement,
   not author parity and not a cold CLI one-shot improvement?
8. Should the next serious target be prepared workspace reuse or GPU-side
   duplicate/range construction, rather than more CPU hash/sort micro-work?
9. Should Goal5020 close with:

```text
completed_generic_lsi_prewarm_productized__cpu_duplicate_hash_no_go__warm_process_fresh_route_moves
```
