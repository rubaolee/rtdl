# Call For Review: Goal4997 v2.14.3 Final Closeout After Goal4996

Please review:

`history/internal_docs/goal4997_v2_14_3_final_closeout_after_goal4996_2026-07-04.md`

Also inspect the public-facing updates:

- `Paper-reproduction-apps/rayjoin-paper/README.md`
- `docs/release_reports/v2_14/rayjoin_reproduction_packet.md`

## Review Questions

1. Does the closeout correctly preserve the distinction between fresh/cold
   one-shot evidence (`~4.220s`) and prepared/query-many binary-operator
   evidence (`~0.33-0.35s` stable rows, median `~0.4369s`)?
2. Does it avoid using the prepared/query-many number as a fresh overlay timing
   or an author-performance ratio?
3. Does it correctly classify Goal4995 as a no-go for CPU lexsort and
   single-pass run-bounds, with app code restored afterward?
4. Does Goal4996 correctly remove an app-layer face-column widening copy while
   avoiding RTDL core/native modifications and avoiding RayJoin-specific core
   semantics?
5. Does the report identify the remaining stable floor honestly: generic device
   ordering and compiled carrier construction, not text writer and not fresh
   LSI setup?
6. Do the public-facing docs stay clean of internal goal/reviewer/process
   leakage while still giving users a correct performance boundary?
7. Is stopping v2.14.3 here defensible after the owner selected not to pursue a
   new generic GPU ordering primitive in this release?
8. Should this line close with
   `completed_v2_14_3_prepared_query_many_closeout_after_goal4996`?

## Requested Verdict Label

`approve_goal4997_v2_14_3_final_closeout_after_goal4996`
