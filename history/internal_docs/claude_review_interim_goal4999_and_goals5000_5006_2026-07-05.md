# Claude Review — Interim Check (Goal4999 + Goals5000–5006 Plan)

Date: 2026-07-05
Reviewer: Claude (strict)
Under review: `interim_check_goal4999_and_goals5000_5006_device_resident_pipeline_2026-07-04.md`,
`goal4999_device_midpoint_query_points_handoff_result_2026-07-04.md`, and the
`device_query_midpoint_top4_repeat5.json` artifact.

## Verdict

```text
approve_goal4999__revise_goal5000_5006_plan_before_implementation
```

Goal4999 itself is sound and I approve it: it removed a real host boundary (midpoint
points no longer packed through host scaled-point records before native PIP), the new
native API is generically named directed point-location device-query input (not a RayJoin
overlay kernel), the POD evidence is solid, and the performance is honestly called modest
(1.026x) architecture, not a win. The owner's "remove the boundary, don't caveat it"
correction was right and was actually executed.

**But the Goals5000–5006 plan must be revised before implementation, because the entire
campaign optimizes a regime that this project's own Goal4985 labeled "diagnostic only,"
mislabels it "query-many," and drops the one cost that actually dominates the fresh
route.** This is not a rejection of device-residency work — it is a demand that the plan
target the regime the product actually runs in, and not lose the ~2.7 s LSI producer.

## The regime problem (the serious finding)

The `0.3295 s` median that Goal4998/4999 improve, and that Goals5001–5004 will keep
optimizing, is measured with `--prepared-operator-session --warmup-runs 1 --repeat 5`.
The artifact's own **median LSI phase is 0.003 s** — i.e. the ~2.7 s exact LSI producer is
cached out. This is precisely the regime Goal4985 recorded as:

```text
Prepared/cached LSI replay routes | diagnostic only | not a fresh overlay result | cannot be headlined
```

Three consequences the plan does not confront:

1. **"prepared/query-many" overstates the evidence.** The run is `--repeat 5` of the *same*
   top4 pair — replay of identical input, not many *distinct* queries. "query-many" implies
   one prepared base serving N different query batches; nothing here demonstrates distinct
   queries. So the number is still replay-diagnostic (Goal4985's own label), now dressed in
   product-sounding language. Do not let "prepared replay" quietly become "prepared/query-many."

2. **The plan optimizes the cached-out regime and ignores the fresh bottleneck.** Fresh top4
   is still ~4.22 s = ~2.7 s LSI producer + ~1.5 s downstream (Goal4985). Goals5001–5004
   attack sort (~0.16 s), carrier (~0.087 s), consumer (~0.041 s) — all sub-components of the
   0.33 s *prepared* body. Even if all seven goals land, fresh moves from ~4.22 s to maybe
   ~3.9 s, because the 2.7 s LSI is untouched. The owner should decide **explicitly** whether
   seven goals that do not materially move the fresh number are the right use of v2.14.3.

3. **The LSI producer goal — the only real fresh mover — is missing.** Goal4983 and Goal4985
   both named exact LSI producer setup/ensure (~2.7 s) the *primary unresolved cost*. The
   5000–5006 plan drops it entirely. Either sequence an LSI-producer goal in, or state
   plainly that v2.14.3 **accepts** the ~2.7 s LSI fresh floor and that 5000–5006 is
   downstream/architecture polish that will not materially move fresh — so no one is
   surprised when fresh stays ~4 s after seven goals.

## Required plan revisions

- **R1 (regime honesty).** Keep Goal4985's label: the `--prepared-operator-session` number is
  prepared **replay** (diagnostic), not "query-many," until a real query-many workload is
  demonstrated. Rename it accordingly throughout 5000–5006.
- **R2 (justify the regime or measure fresh).** To optimize the prepared downstream floors at
  all, either (a) demonstrate a genuine query-many workload — one prepared base LSI, N
  **distinct** query batches, measured — or (b) measure and report each of Goals5001–5004's
  effect on the **fresh** route, not only the prepared body. Do not defer fresh to Goal5005;
  move fresh measurement forward so every optimization is judged against the product regime.
- **R3 (don't lose the LSI producer).** Add an explicit decision/goal on the ~2.7 s LSI
  producer, or an explicit written acceptance that v2.14.3 ships with that fresh floor and
  that 5000–5006 does not target it. The plan must not silently drop the cost its own prior
  goals called primary.
- **R4 (self-validate device-residency).** Carry over the Goal4988 amendment: the "boundary
  removed / device-resident" claims must be verified from row-buffer / prepared-points
  metadata (`materializes_host_rows_for_bridge == False`), not from self-declared flags. Make
  Goal5000's audit confirm device-residency via metadata and confirm the new prepared-points
  wrapper's owner-lifetime in code, not prose.

## Answers to the review questions

1. Why the owner forced it (Goal4998 still had a midpoint host pack; caveat ≠ work)? **Yes,
   correctly explained, and the fix genuinely removed the boundary.**
2. Goal4999 removed the midpoint host pack in `--device-resident-carrier`? **Yes** — device
   query records now feed native PIP directly (~0.0015–0.0017 s device-query phases).
3. New native/API classified as generic directed point-location device-query input? **Yes on
   naming/semantics** (`RtdlDirectedSegmentDeviceQueryPoint2D`,
   `..._prepare_directed_segment_point_location_device_query_points_2d`). Note: it forwards
   into legacy `PreparedRayjoinCdbPointLocation2D` internals — generic façade over a
   rayjoin-named core type (the standing P1-1 naming debt; verify no rayjoin semantics leak at
   Goal5000).
4. POD evidence supports the narrow claim? **Yes** — OptiX 8.1 rebuild, symbol exported, 9
   tests, top4 complete, `lsi_row_count=428322`, `descriptor_pair_count=15014`, median
   `0.3381→0.3295`.
5. Performance interpreted honestly as modest + architectural, not parity/broad win? **Yes.**
6. Remaining floors correct (sort/carrier/consumer, not midpoint packing)? **Yes for the
   prepared body — but they are floors of the 0.33 s *replay* regime, not of fresh (R2/R3).**
7. Goal5001 (device run-bound generation) the right next target? **Only under R2/R3** —
   it removes a real host boundary (good) but is a sub-0.1 s prepared-regime cost; justify
   against fresh.
8. Goal5002 (ordering decision, no RayJoin sorter) framed right? **Yes** — reuse-generic-or-
   record-as-floor is correct discipline.
9. Goal5003 (generic binary carrier output contract, no text in core)? **Yes** — this is real
   operator value; keep it generic and app-name-free.
10. Goal5004 (real downstream operator proof) necessary? **Yes — and it is the most important
    goal in the set** (it finally tests the binary-operator thesis). But one operator on one
    output is not "query-many"; keep the claim scoped.
11. Goal5005 keeps fresh/warm/prepared/text/binary separated? **Yes** — but it arrives too
    late; per R2 fresh must be measured before/with 5001–5004, not only at 5005.
12. Goal5006 preserves release/public-surface boundaries? **Yes** — leak scan + artifact
    separation are correctly required.
13. Missing goals? **Yes — (a) the LSI producer fresh-cost goal (R3); (b) a genuine
    query-many workload demonstration if the prepared regime is to be optimized (R2); (c)
    metadata-based device-residency verification (R4).**
14. Proceed in the proposed order? **Only after R1–R4.** Goal5000 (external review = this
    review) correctly gates first; insert the regime decision (R2/R3) as a blocking step
    before Goal5001.

## Non-authorization

Authorizes Goal4999's boundary removal only. No author parity, no fresh headline from the
0.33 s prepared/replay number, no "query-many" claim without a distinct-query workload, no
hidden RayJoin core primitive, no claim that host/device boundaries are all solved, and no
v2.14.3 publication before a Goal5005 matrix that shows fresh alongside prepared and a
Goal5006 boundary check. The prepared 0.33 s stays diagnostic until a real query-many use
case is measured; fresh (~4.22 s, LSI-dominated) remains the only honest product number.
