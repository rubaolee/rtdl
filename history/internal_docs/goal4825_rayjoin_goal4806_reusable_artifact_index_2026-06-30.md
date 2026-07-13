# Goal4825 RayJoin Goal4806 Reusable Artifact Index

Date: 2026-06-30

## Purpose

Goal4825 turns the old Goal4806 work into a provenance-controlled index so the
current RayJoin reproduction line can reuse data and evidence without
continuing abandoned V4 work.

The machine-readable index is:

`history/internal_docs/goal4825_rayjoin_goal4806_reusable_artifact_index_2026-06-30.json`

## Critical Boundary

This is **not** V4 continuation.

Reusable items are only:

- dataset locations;
- generated CDB files;
- author-code paths;
- source/data availability checks;
- debug or bottleneck artifacts.

Forbidden promotions:

- V4 API/planner evidence as current product evidence;
- V4+Numba candidate-stage numbers as full overlay performance;
- same-source regenerated CDBs as exact paper-preprocessed inputs;
- dirty Goal4806 byte-equality reports as current evidence without revalidation.

## POD Recheck

The current POD still has the old Goal4806 data/artifacts:

```text
HOST=e7820d339c40
GPU=NVIDIA RTX 4000 Ada Generation
PRESENT:/workspace/rtdl_goal4806_fast_min
PRESENT:/workspace/rayjoin_section57_same_source_cdb
PRESENT:/workspace/RayJoin_fresh
PRESENT:/workspace/rayjoin_section57_arcgis_stage
PRESENT:/workspace/rtdl_goal4806
PRESENT:/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_matrix_exact_county_20260630
PRESENT:/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630
```

## Indexed Artifact Classes

| Label | Meaning |
|---|---|
| `exact_public_sample_current_line` | Current post-fix evidence from Goal4820/4821. |
| `goal4806_dirty_line_needs_revalidation` | Old Goal4806 evidence that can guide work but cannot be cited until revalidated. |
| `same_source_regenerated_cdb` | Rebuilt from live source data; useful, but not exact paper CDB. |
| `candidate_stage_only` | Numba/continuation candidate evidence, not full overlay performance. |
| `missing_exact_input_or_answer` | Evidence that exact inputs, answers, or pair coverage are missing. |

## Key Findings

1. The public County x Soil sample is current-line evidence after Goal4820/4821.
2. Old Goal4806 County x Zipcode byte-equality is a valuable revalidation
   target, but it is not current evidence yet.
3. Old Goal4806 Block x Water CDBs are usable as `same_source_regenerated_cdb`
   artifacts, not exact paper inputs.
4. Old Goal4806 V4+Numba rows are candidate-stage only.
5. Six Lakes/Parks rows remain blocked by missing source targets/conversion
   and missing exact CDB/answer evidence.

## Next Authorized Work

### Goal4826

Revalidate County x Zipcode under the current repaired product line.

Exit condition: byte-equal current-line output or exact mismatch diagnosis.

### Goal4827

Decide the Block x Water route.

Exit condition: either exact paper data appears, or Block x Water remains
explicitly same-source-only.

### Goal4828

Audit Lakes/Parks source gap.

Exit condition: registered reconstruction path or explicit missing-input
closure for the six rows.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   I would be foolish if I treated old Goal4806 results as current evidence.

2. **What actions would make the decision foolish?**
   Reusing dirty output as product proof; calling same-source data exact paper
   data; calling candidate-stage Numba full overlay performance.

3. **Is there another path that avoids being stuck?**
   Yes. Use the index as a provenance gate, then revalidate only the rows that
   can become current-line evidence.

4. **Can I start a different path that truly solves the problem?**
   Yes. Goal4826 should revalidate County x Zipcode first, because it is the
   strongest old clue and can become useful current evidence if it still passes.
