# Goal4830: County x Zipcode Streaming Full Compare Result

Date: 2026-06-30

## Purpose

Run a full correctness comparison against the deterministic author baseline without writing RTDL's full 2.4GB output file or storing all output chains in memory.

This remains correctness-only. Performance is still blocked.

## Method

Internal diagnostic user app:

`history/internal_docs/goal4830_streaming_full_compare_user_app.py`

The app monkey-patches only the current Python process:

- It streams RTDL-generated output-chain lines in author format.
- It compares each generated line against the deterministic author output.
- It stops at the first mismatch.
- It does not modify RTDL source.
- It does not write a 2.4GB RTDL output file.

POD artifact directory:

`/workspace/rtdl_goal4820_sos_fix/artifacts/goal4830_streaming_full_compare_after_comparator_restore`

## Result

Artifact:

`/workspace/rtdl_goal4820_sos_fix/artifacts/goal4830_streaming_full_compare_after_comparator_restore/summary.json`

Summary:

```json
{
  "elapsed_sec": 479.5086336135864,
  "stream_match": false,
  "first_diff": {
    "line": 90411,
    "author": "30138 1 31059 31059 63 110",
    "rtdl": "30138 1 31059 31059 106 107"
  }
}
```

Interpretation:

- The corrected comparator fixed the earlier first-20-chain regression.
- Full same-source County x Zipcode correctness still fails.
- The first remaining mismatch is chain `30138`, line `90411`.
- The mismatch is face-id-only; chain id and point ids match.
- This is the same locality previously identified in Goal4827 as a difficult midpoint / point-location / face-id assignment region.

## Current Status

Verified:

- Deterministic author baseline exists.
- Public County x Soil still passes byte-equality.
- County x Zipcode first 20 chains match deterministic author baseline after comparator restore.
- Streaming full compare avoids the 2.4GB file-write problem and gives an actionable first diff.

Not yet solved:

- County x Zipcode same-source full correctness.
- Exact paper Section 5.7 reproduction.
- Performance.

Current blocker:

- Need diagnose and repair the chain `30138` face-id mismatch under the deterministic author contract.

## Next Work

Recommended next goal:

1. Re-run or extend the existing chain-prefix probe around chain `30138` under the corrected comparator.
2. Compare the author source's selected midpoint / face assignment for that chain against RTDL's selected segment/face.
3. Determine whether the gap is:
   - point-location SoS still incomplete,
   - midpoint construction mismatch,
   - output-chain face-id assignment mismatch,
   - or another CDB/data-model issue.
4. If it is a general directed point-location or overlay data-model defect, fix RTDL core.
5. If it is only a RayJoin-specific compatibility gap, record it honestly rather than hiding it as a generic language win.

Forbidden:

- No performance run.
- No full Section 5.7 claim.
- No tuning to the old nondeterministic author output.
- No RayJoin-only hidden kernel.
