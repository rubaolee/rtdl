# Goal4820 — Core Directed-Segment Point-Location SoS Fix

Date: 2026-06-30

Status: `core_fix_verified_on_author_public_sample`

## Why This Goal Exists

Goal4817-Goal4819 exposed a product defect while attempting to reproduce the
RayJoin Section 5.7 polygon overlay workload as an RTDL user/application author.
The author public sample passes byte-for-byte with the author binary but fails
with released RTDL's bundled helper.

The diagnosed blocker is not a performance issue. It is a correctness issue in
the directed-segment point-location/PIP contract under equal-depth candidates.

## Core Rule

This goal must repair an RTDL core primitive contract, not add a RayJoin-only
shortcut.

The core primitive is:

`directed-segment point-location / PIP over closed polygonal edge sets`

The required semantics are:

- equal-depth candidates must be resolved deterministically;
- Simulation-of-Simplicity slope preference must be part of the primitive's
  contract, not an incidental app postprocess;
- the chosen preference must be encoded in the reported OptiX hit distance so
  OptiX traversal pruning cannot bypass the tie-breaker;
- the fix must remain useful for any app that needs deterministic directed-edge
  point location, not only RayJoin.

RayJoin is the first exposed validation workload, not a special-case engine
identity.

## Exposed Product Problem Register

### P1 — OptiX pruning bypasses equal-depth slope tie-break

Evidence:

- User-provided author determinism note:
  `C:/Users/Lestat/Downloads/rayjoin_pip_determinism_summary.md`
- Goal4818 diagnosis:
  `history/internal_docs/goal4818_rayjoin_public_sample_correctness_gap_diagnosis_2026-06-30.md`
- Goal4819 external closure review:
  `history/internal_docs/antigravity_goal4819_rayjoin_user_mode_reproduction_closure_review_2026-06-30.md`

Current behavior:

- the intersection program can compare slopes inside a visited primitive range;
- but OptiX globally prunes later equal-depth candidates after the first
  reported hit, so the slope tie-break may never run for the candidate that
  should win;
- the existing `RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES=1` path uses `nextafterf`
  and does not encode slope preference.

Required fix:

- make the core directed-segment point-location reported hit distance carry the
  slope preference, so more preferred equal-depth candidates report a smaller
  distance and win independent of traversal order.

Patch status:

- implemented for the OptiX directed-segment point-location kernel;
- source-level test updated;
- POD build succeeded on NVIDIA RTX 4000 Ada using
  `OPTIX_PREFIX=/tmp/optix-sdk-probe`;
- synthetic equal-height probe confirms the core policy is observable:
  `query_map_id=0` chooses the larger normalized slope and `query_map_id=1`
  chooses the smaller normalized slope.

### P2 — Public sample output is unchanged after the core SoS fix

Evidence:

- patched library SHA256 on POD:
  `554b747ddda990c552c78aa7ddc0301ab9673f3975f30e04a1b69946fa6e0b34`
- patched RTDL public-sample output SHA256:
  `296ad11acb39cd6c54ca6d95aab16598a44d56bb14d960a370b629c9ea5289c7`
- author answer SHA256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`
- byte equality remains false.

Interpretation:

The author-reply `t_reported` issue is a real core primitive defect, but it is
not sufficient to repair the current public-sample overlay mismatch. The next
exposed issue is therefore downstream of the fixed equal-depth PIP pruning
case, most likely in face/topology assignment or output-chain assembly.

Required next action:

- do not run performance;
- do not broaden this into an app-specific RayJoin kernel;
- diagnose the first public-sample divergence at the overlay topology/output
  contract level and record whether the missing behavior is a core primitive
  contract, a bundled-helper application bug, or an input/parameter mismatch.

### P3 — Author reply direction and author source comparator must be reconciled

Evidence:

- The user-provided author-reply summary defines a slope-dependent
  `t_reported` rule with:
  - `query_map_id == 0`: larger normalized slope has higher preference;
  - `query_map_id == 1`: smaller normalized slope has higher preference.
- The committed author source in
  `RayJoin_fresh:src/algo/rt_pip_custom.cu` contains this internal
  equal-height comparator:

  ```text
  bool flag = current_e_slope > best_e_slope;
  if ((query_map_id && !flag) || (flag && !query_map_id)) {
    continue;
  }
  ```

  Executed literally, that comparator rejects a larger current slope for
  `query_map_id == 0` and rejects a non-larger current slope for
  `query_map_id == 1`. The adjacent source comment says the opposite:
  `im==0` wants bigger slope and `im==1` wants smaller.

Interpretation:

The previous Goal4818 note overtrusted the source comment. The product fix now
must treat the slope direction as an exposed contract ambiguity, not as a
settled fact. The first patch matched the author-reply `t_reported` direction;
the public sample output remained unchanged. A second diagnostic must test the
literal author-source comparator direction before any final claim that the core
SoS contract has been repaired.

Required next action:

- test both candidate core contracts on the author public sample:
  1. author-reply `t_reported` direction;
  2. committed-source comparator direction;
- record the output hash and byte-equality result for each;
- only after that decide whether the next gap is still PIP/SoS or is
  downstream topology/output-chain assembly.

Follow-up result:

- Both candidate slope-preference directions produced the same RTDL output hash
  on the author public sample:
  `296ad11acb39cd6c54ca6d95aab16598a44d56bb14d960a370b629c9ea5289c7`.
- The author answer hash remained:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`.
- Therefore the author-reply non-determinism fix is relevant core product work,
  but it does not explain the current public-sample byte-equality failure.
- The next active blocker is downstream or adjacent contract mismatch in
  midpoint classification, face assignment, output-chain assembly, or input
  parameterization.

### P4 — Midpoint face assignment used one shared field for two directed maps

Evidence:

- Raw-chain diagnostics localized the first relevant output mismatch to a
  midpoint interval on map 0:
  - owner intersection pair: `left_eid=2203`, `right_eid=85627`;
  - interval endpoints:
    `(-65.31317139696486, -9.896999126713506)` and
    `(-65.29756365310183, -9.879066370763889)`;
  - old overlay assembly read `mid_point_polygon_id=17`;
  - author raw output and author-rule scalar oracle require face `1113`.
- Direct native single-point point-location for that same midpoint returned
  face `1113`.
- Scalar author-rule oracle also returned face `1113` for both candidate
  slope-direction interpretations.

Root cause:

- `RayjoinOverlayIntersection` stored only one `mid_point_polygon_id`.
- The same intersection objects are reused in both map-0-sorted and
  map-1-sorted lists.
- Midpoint PIP assignment for map 1 overwrote map 0's midpoint face on the same
  intersection object.
- Output-chain assembly for map 0 then read the wrong map's face id.

Why this is a product fix, not a RayJoin-only shortcut:

- The defect is a general directed-overlay continuation data-model bug:
  one geometric intersection can participate in interval continuations for
  both input maps, and those two continuations need independent point-location
  results.
- The fix stores midpoint faces per directed map and makes assembly read the
  face for the map currently being emitted.

Patch status:

- `RayjoinOverlayIntersection` now stores:
  - `mid_point_polygon_id_map0`;
  - `mid_point_polygon_id_map1`.
- `_assign_midpoint_faces(..., map_index=...)` writes the correct directed
  slot.
- `_assemble_output_chains` reads `_midpoint_face_for_map(xsect, map_index)`.
- Added regression test:
  `tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_overlay_midpoint_faces_are_stored_per_map`.

### P5 — Author public sample byte equality is repaired after P4

POD environment:

- host: `root@157.157.221.29 -p 23132`
- RTDL checkout:
  `/workspace/rtdl_goal4817_user_smoke_20260630_102224`
- author repo:
  `/workspace/RayJoin_fresh`
- input left:
  `/workspace/RayJoin_fresh/test/dataset/br_county_clean_25_odyssey_final.txt`
- input right:
  `/workspace/RayJoin_fresh/test/dataset/br_soil_ascii_odyssey_final.txt`
- author answer:
  `/workspace/RayJoin_fresh/test/dataset/br_countyXbr_soil_answer.txt`
- OptiX library SHA256 after P4:
  `f668a1780eaaaaa65805bc2d02ca77d68df1be6cbb9756ec6eace46f9dc5cad8`

Focused tests:

- local:
  `py -3 -m unittest tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_overlay_midpoint_faces_are_stored_per_map tests.goal4373_rayjoin_cdb_point_location_route_test.Goal4373RayjoinCdbPointLocationRouteTest`
- POD:
  `python -m unittest tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_overlay_midpoint_faces_are_stored_per_map tests.goal4373_rayjoin_cdb_point_location_route_test.Goal4373RayjoinCdbPointLocationRouteTest`
- both passed.

Author public sample rerun after P4:

```json
{
  "answer_bytes": 16631243,
  "answer_sha256": "464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e",
  "byte_equal": true,
  "elapsed_sec": 6.219067253172398,
  "output_bytes": 16631243,
  "output_sha256": "464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e"
}
```

Local artifact copies:

- `history/internal_docs/goal4820_artifacts_2026-06-30/after_midpoint_fix_summary.json`
- `history/internal_docs/goal4820_artifacts_2026-06-30/author_pip_scalar_oracle_after_fix.json`

Interpretation:

- Correctness gate for the author public sample now passes byte-for-byte.
- Performance remains a separate next goal; this result authorizes moving from
  correctness repair to controlled performance measurement, not broad
  performance claims.

## Verification Gates

1. Code review gate: the implementation must not introduce a new app-identity
   native path such as a RayJoin-only overlay kernel.

2. Focused source gate: tests must assert the native OptiX source now expresses
   the deterministic reported-distance SoS rule and the corrected slope
   preference.

3. Correctness gate: the public RayJoin sample must be rerun against author
   output. This gate passed after P4 for the author public sample.

4. Regression gate: public docs and tutorials are not part of this goal unless
   a user-facing contract change must be documented after correctness passes.

## Decision-Audit Note

The previous blocked conclusion was correct under a strict "released user mode,
no RTDL edits" constraint. The user has now explicitly authorized product
repair. Continuing to merely record the gap would be a repeat of the previous
avoidance failure; modifying arbitrary RayJoin-specific application code would
be the opposite failure. The aligned action is a core primitive fix plus a
clear exposed-problem record.
