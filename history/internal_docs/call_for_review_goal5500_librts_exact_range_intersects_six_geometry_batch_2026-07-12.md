# Call For Review: Goal5500 LibRTS Exact Range-Intersects Six-Geometry Batch

Please strictly review Goal5500 against the actual code, result JSON, archive
provenance, and the claim boundary. This is a batch-attempt milestone, not a
success headline. Do not infer a semantic bug from a count mismatch without
relation-level or independent-reference evidence.

## Files To Review

```text
history/internal_docs/goal5500_librts_exact_range_intersects_six_geometry_batch_result_2026-07-12.md
Paper-reproduction-apps/librts-paper/data/goal5500_range_intersects_representative_cases.json
Paper-reproduction-apps/librts-paper/extract_verified_operation_batch.py
Paper-reproduction-apps/librts-paper/run_exact_range_intersects_batch.py
Paper-reproduction-apps/librts-paper/results/librts_goal5500_range_intersects_batch_extraction.json
Paper-reproduction-apps/librts-paper/results/librts_goal5500_range_intersects_batch_gate.json
tests/goal5500_librts_exact_range_intersects_batch_tools_test.py
tests/goal5500_librts_exact_range_intersects_batch_result_test.py
```

## Review Questions

1. Does the extraction JSON prove that all six geometry/query pairs came from
   the verified official archive, with 12 selected members and per-member
   size/SHA-256 evidence?
2. Does the batch runner pass the exact same extracted files to author and RTDL
   and record each case fail-closed?
3. Are the three matches, two count mismatches, and one author CUDA OOM
   accurately reported without silently dropping or relabeling cases?
4. Does the evidence distinguish a count disagreement from a relation-level
   disagreement, given that the author binary does not expose pair rows?
5. Is the `parks.bz2` failure correctly classified as author-side CUDA
   allocation failure rather than semantic mismatch or RTDL failure?
6. Are RTDL WKT/load, preparation, prepared-query, and primitive phases kept
   separate from the author's internal query metric, with no ratio claim?
7. Does the generic `Aabb2DColumns` / `prepare_aabb_index_2d_columns` route
   remain app-neutral, with no LibRTS-specific core API or Embree work?
8. Does the report correctly refuse a six-case matrix claim, complete
   range-intersects claim, Figure 6 claim, pointwise relation claim, full-paper
   claim, performance parity, zero-copy, and Embree evidence?
9. Is the proposed next step—diagnose the two count disagreements using a
   generic/reference or relation-level probe—better justified than more route
   tuning?
10. Are the local regression tests meaningful and tied to the actual evidence,
    rather than source-string-only assertions or a self-approved status?

## Required Verdict Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-10:
Claim boundary decision:
Requested verdict label:
```

## Explicitly Unauthorized Summaries

```text
"six exact range-intersects cases matched"
"full range-intersects matrix complete"
"RTDL and author relation rows are equal"
"RTDL is faster than the author"
"author performance parity"
"Figure 6 reproduced"
"full LibRTS paper reproduction"
"parks.bz2 semantic mismatch"
"Embree comparison"
```

The correct bounded summary, if evidence survives review, is:

```text
Six exact official range-intersects pairs were attempted on the same extracted
files: three count matches, two count disagreements requiring diagnosis, and
one author CUDA allocation failure. No complete matrix, relation equality,
performance ratio, figure reproduction, or Embree claim is authorized.
```
