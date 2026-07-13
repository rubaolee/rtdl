# Call For Review: Goal4827 County x Zipcode Same-Source Status

Requested verdict labels:

- `approve_goal4827_status_and_authorize_deterministic_author_baseline_goal`
- `request_amendments_goal4827_status`
- `fail_redo_goal4827_status`

Please review:

- `history/internal_docs/goal4827_county_zipcode_same_source_status_2026-06-30.md`
- code changes in:
  - `src/native/optix/rtdl_optix_core.cpp`
  - `src/rtdsl/rayjoin_overlay.py`
  - `tests/goal4373_rayjoin_cdb_point_location_route_test.py`
  - `tests/goal4374_rayjoin_exact_paper_suite_test.py`

Questions:

1. Are the three RTDL changes valid general directed point-location /
   directed-overlay repairs rather than RayJoin-only hidden kernels?
2. Does the author determinism note justify the SoS direction used here:
   `query_map_id == 0` prefers larger slope and `query_map_id == 1` prefers
   smaller slope, encoded into `t_reported`?
3. Does preserving rational scaled intersection coordinates for midpoint PIP
   queries correctly follow the author `ExactPoint` midpoint construction?
4. Is the public County x Soil byte-equality rerun sufficient to show the SoS
   correction did not break the official public sample?
5. Does the County x Zipcode prefix evidence justify treating the old
   same-source author-output file as a debug clue rather than deterministic
   byte-equality truth?
6. Should performance remain blocked until a deterministic author-reference
   baseline is generated with the author-reply `t_reported` patch?
7. Is the recommended next goal correct: generate a deterministic author
   baseline from the author source plus the author-reply patch, then compare RTDL
   against that baseline on the same-source County x Zipcode pair?

Boundaries:

- No Embree evidence is requested.
- No performance claim is requested.
- No exact Section 5.7 paper-input claim is requested.
- Do not authorize tuning RTDL to match one old nondeterministic author-output
  file.
