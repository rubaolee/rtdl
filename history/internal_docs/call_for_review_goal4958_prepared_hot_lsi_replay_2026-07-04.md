# Call For Review: Goal4958 Cached LSI Replay Erratum And Exact Device Output Audit

Please review:

`history/internal_docs/goal4958_prepared_hot_lsi_replay_and_exact_device_output_audit_2026-07-04.md`

## Requested Verdict

One of:

- `approve_goal4958_cached_replay_erratum_and_fresh_route_boundary`
- `approve_with_required_amendments`
- `block_goal4958_claims_until_remeasured`

## Review Questions

1. Does the report correctly separate fresh LSI computation cost from cached
   LSI replay cost?
2. Is `--prepared-lsi-replay` honestly bounded as a cached/replay diagnostic,
   not a cold-start, fresh-overlay, or paper text-output timing?
3. Does the report correctly retract the `2.0412770221607137x` arithmetic
   field as a same-denominator performance headline against the patched author
   overlay compute baseline of `0.0421s`?
4. Does the report correctly classify the fair fresh-route comparison as
   roughly `0.90s / 0.0421s`, or about `21x` slower than AuthorPatch?
5. Does the validation artifact prove CUDA sort order still matches the CPU
   longdouble reference?
6. Is the semantic fingerprint stable enough for this numeric/binary route
   claim (`lsi_row_count=20860`, `pair_count=28815`, `total_groups=64459`,
   `total_point_rows=673371`)?
7. Does the exact-device audit correctly reject `candidate_device_columns` as a
   substitute for exact planar-map LSI pair-id rows?
8. Does the exact-device audit correctly reject `left_id_count_device_columns`
   as insufficient for RayJoin reprojection/sort because it lacks right ids?
9. Did the implementation avoid RTDL core/native edits and keep RayJoin as an
   app over generic public primitives?
10. Are the non-authorized claims complete enough to prevent overclaiming?
11. What should be the next goal: larger-input fresh/cached confirmation,
    generic exact LSI device pair columns, or stop this line at the current
    bounded result?
