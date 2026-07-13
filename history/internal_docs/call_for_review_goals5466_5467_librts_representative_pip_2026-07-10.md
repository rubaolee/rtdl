# Call For Review: Goals5466-5467 LibRTS Representative PIP

Please strictly review the representative LibRTS PIP milestone, especially the
boundary between generic RTDL candidate production and app-owned author
compatibility.

## Files

```text
history/internal_docs/goal5466_5467_librts_representative_same_input_pip_result_2026-07-10.md
Paper-reproduction-apps/librts-paper/data/representative/goal5466_blockgroups_simple64_100k/manifest.json
Paper-reproduction-apps/librts-paper/data/representative/goal5466_blockgroups_simple64_100k/blockgroups_simple64_arcgis.wkt
Paper-reproduction-apps/librts-paper/data/representative/goal5466_blockgroups_simple64_100k/blockgroups_simple64_queries_seed0_100k.wkt
Paper-reproduction-apps/librts-paper/author_patches/goal5466_spatialquerybenchmark_gen_only_CMakeLists.txt
Paper-reproduction-apps/librts-paper/author_patches/goal5467_export_author_pip_rows.patch
Paper-reproduction-apps/librts-paper/librts_author_pip_compat.py
Paper-reproduction-apps/librts-paper/run_same_input_representative_pip_gate.py
Paper-reproduction-apps/librts-paper/diagnose_representative_pip_semantics.py
Paper-reproduction-apps/librts-paper/results/librts_goal5467_representative_same_input_pip.json
Paper-reproduction-apps/librts-paper/results/librts_goal5467_representative_pip_semantics_diagnostic.json
tests/goal5466_librts_representative_pip_dataset_test.py
tests/goal5467_librts_representative_same_input_pip_gate_test.py
```

## Critical Facts

```text
unmodified author count = 71,626
standard RTDL count     = 71,624
app-compatible RTDL     = 71,626
instrumented author     = 71,626
full pair-row equality  = true
canonical SHA-256       = 7d30e35b...26c7b
```

The standard mismatch is intentionally preserved. Exact artifact agreement is
provided by an app-owned Numba adapter, not a core semantic change.

## Questions

1. Is the dataset correctly classified as a Level-B public-source
   representative subset rather than exact/full paper data?
2. Is selecting 64 simple, no-hole source-order polygons a defensible way to
   avoid unreviewed MultiPolygon/hole model differences?
3. Does the pinned author generator with seed 0 and 100K queries provide a
   reproducible query contract, including matching SHA-256 on regeneration?
4. Is preserving the initial `71,626` versus `71,624` standard-route mismatch
   the correct evidence discipline?
5. Does the actual author row dump prove that the count difference corresponds
   to six relation differences rather than a timing or capacity artifact?
6. Is the row-dump patch comparator-only, and does running both unmodified and
   instrumented binaries adequately guard against instrumentation drift?
7. Is `expanded_aabb_point_membership_rows_2d` genuinely app-neutral generic
   RTDL work in this route?
8. Is the float32/sentinel/fast-math PNPOLY Numba helper correctly kept
   app-owned rather than promoted into RTDL core?
9. Does complete pair-row equality plus canonical hash equality support the
   bounded representative relation claim?
10. Are the `1e-5` candidate expansion and Numba fast-math settings adequately
    disclosed as author-compatibility policy rather than generic semantics?
11. Are timing fields correctly restricted to diagnostics with no ratio,
    Figure 12, or Ray-Multicast claim?
12. Does the work preserve the full-campaign Embree exclusion?
13. Is any claim stronger than its committed evidence?
14. May Goals5466-5467 close at Level-B representative same-input PIP relation
    agreement while exact paper data, figures, scheduling, and performance stay
    open?

## Expected Answer

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-14:
Requested verdict label:
```

Requested label if approved:

```text
approve_goals5466_5467_librts_representative_same_input_pip_relation
```
