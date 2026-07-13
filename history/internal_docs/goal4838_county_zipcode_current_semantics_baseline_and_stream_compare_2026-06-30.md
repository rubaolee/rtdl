# Goal4838 — County x Zipcode Current-Semantics Baseline and Streaming Compare

Date: 2026-06-30

## Purpose

Fix the evidence-chain error exposed during the County x Zipcode same-source line:
RTDL and the author baseline must be compared under the same deterministic SoS
semantics.

The previous comparison was not acceptable because current RTDL used the
author-clarified intended SoS behavior, while the older County x Zipcode author
baseline was generated under an earlier comparator interpretation.

## Dataset

Input provenance:

- `same_source_regenerated_cdb`
- not exact preprocessed Section 5.7 paper input

Inputs:

- map0: `/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb`
- map1: `/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb`

## Current Semantics

Both sides are now intended to use:

- author clarification intended behavior;
- map0 prefers larger slope;
- map1 prefers smaller slope;
- slope-dependent `t_reported` so OptiX strict traversal pruning cannot choose an arbitrary equal-height candidate.

RTDL source check:

- local `src/native/optix/rtdl_optix_core.cpp`: `query_map_id == 0u ? current_slope > best_slope : current_slope < best_slope`
- POD current RTDL worktree: `/workspace/rtdl_goal4817_user_smoke_20260630_102224`

Author source check:

- POD author worktree: `/workspace/RayJoin_goal4834_patched_author`
- `src/algo/rt_pip_custom.cu` contains intended comparator:
  `if ((!query_map_id && !flag) || (query_map_id && flag)) continue;`
- `rayjoin_pip_sos_report_t(...)` is used in `optixReportIntersection(t_reported, 0)`.

## Regenerated Author Baseline

Artifact:

- `history/internal_docs/goal4838_author_intended_county_zipcode_baseline_summary.json`

Output on POD:

- `/workspace/goal4838_current_intended_author_baseline/author_intended_county_zipcode_overlay.txt`

Summary:

- bytes: `2390763754`
- sha256: `02fcae3f53a8486134412564c438a19d7d999d1948742e7f115a5d13f94836ef`
- elapsed wall: `1221.6335825920105` sec
- author reported chains: `29253961`
- author reported faces: `115515`

Important timing note:

- author program spent `284597 ms` reading map0 and `772405 ms` reading map1.
- This was input parsing / CDB load cost, not RTDL execution.

## Current RTDL Streaming Compare

Artifact:

- `history/internal_docs/goal4838_current_rtdl_vs_intended_author_streaming_compare_summary.json`

Command shape:

```bash
cd /workspace/rtdl_goal4817_user_smoke_20260630_102224
RTDL_OPTIX_LIB=/workspace/rtdl_goal4817_user_smoke_20260630_102224/build/librtdl_optix.so \
PYTHONPATH=src \
python3 /workspace/goal4838_streaming_full_compare_current_code.py \
  --left /workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb \
  --right /workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb \
  --author-output /workspace/goal4838_current_intended_author_baseline/author_intended_county_zipcode_overlay.txt \
  --output-dir /workspace/goal4838_streaming_compare_current_code_intended_baseline
```

Result:

```json
{
  "elapsed_sec": 471.8164064884186,
  "stream_match": false,
  "first_diff": {
    "line": 156531,
    "author": "52183 1 53009 53009 582 586",
    "rtdl": "52183 1 53009 53009 578 587"
  }
}
```

## Interpretation

The evidence-chain error was fixed:

- The old line-25 mismatch disappeared after regenerating the author baseline
  under the same intended SoS semantics as current RTDL.

But County x Zipcode same-source correctness is still not complete:

- the new first mismatch is line `156531`, chain `52183`;
- it is again a face-id-only mismatch:
  - chain id matches;
  - point ids match;
  - point count matches;
  - face pair differs.

This means performance remains blocked.

## What This Proves

- The previous line-25 mismatch was a baseline-semantics mismatch, not a valid RTDL correctness conclusion.
- Current RTDL and current intended-author baseline agree past the earlier line-25 failure.
- A real remaining correctness gap still exists at chain `52183` under the current semantics.

## What This Does Not Prove

- It does not prove full County x Zipcode correctness.
- It does not prove exact Section 5.7 reproduction.
- It does not authorize performance testing.
- It does not authorize broad RayJoin or RTDL claims.

## Mistake Record

I initially tried to compare current RTDL against the old Goal4828 author output.
That was wrong because the baseline semantics were not guaranteed to match the
current RTDL comparator. This created an invalid line-25 mismatch.

The correction was to regenerate the author baseline from
`/workspace/RayJoin_goal4834_patched_author`, whose source currently implements
the intended author clarification.

## Next Goal

Goal4839 should diagnose chain `52183` under current semantics.

Required:

1. Extract author lines around chain `52183`.
2. Generate RTDL prefix/context around chain `52183` using the current RTDL worktree.
3. Compare pre-finalize face ids, point ids, intersection events, midpoint owners, and direct point-location result at the relevant coordinate.
4. Decide whether the gap is:
   - midpoint/overlay ownership semantics;
   - directed point-location SoS still incomplete;
   - face-id creation/order mismatch;
   - input/topology provenance gap;
   - or another product bug.

Forbidden:

- no performance run;
- no full Section 5.7 claim;
- no comparison against the old baseline as truth;
- no RayJoin-only hidden kernel.

## Goal-Level Decision Audit

1. **Was I being foolish?**
   Yes. I briefly compared current RTDL against a stale author baseline and treated the mismatch as meaningful.

2. **What made that foolish?**
   The author baseline and RTDL code had diverged in comparator semantics. Same-source data is not enough; the deterministic contract must also match.

3. **Was there another path?**
   Yes: regenerate the author baseline from the current intended-behavior patched author binary first.

4. **Can I now solve the real problem?**
   Yes. The evidence is now same-semantics. The real remaining first diff is chain `52183`, not the stale line-25 mismatch.

## Exit Label

`completed_current_semantics_baseline_regenerated__line25_artifact_removed__new_first_diff_chain52183`
