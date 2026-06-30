# Goal4806 Follow-Up Goal Sequence: Released RTDL RayJoin Section 5.7

Date: 2026-06-30

## Controlling Rule

All follow-up goals serve the same parent objective:

> Finish Goal4806: reproduce RayJoin paper Section 5.7 Polygon Overlay as an
> installed-user application using released RTDL V4.0.0 + Python + Numba, and
> compare against the author implementation and the existing V2.14 route.

The following files must not be edited for these goals:

- `src/rtdsl/**`
- `src/native/**`
- V4.0.0 release tag contents

If a required capability is missing from released RTDL, record it as a product
gap.  Do not patch RTDL and call the patched result released V4.

## Goal4807 — Released-Only Design And API Map

Purpose:

Determine exactly which released RTDL V4.0.0 APIs and scripts a normal user can
call for RayJoin Section 5.7, and map them to the author workload stages.

Authorization:

- Goal4807 is the only currently authorized follow-up goal.
- It is read-only.
- It must run from a fresh clean `v4.0.0` checkout, not the main development
  worktree.
- It must paste the full clean-check output:
  - `git rev-parse HEAD`
  - `git status --porcelain`
  - any `PYTHONPATH` / import-path proof needed to show it is not importing from
    the dirty tree.

Deliverable files:

- `docs/reports/goal4807_released_rtdl_rayjoin_section57_api_map_2026-06-30.md`
- `docs/reports/goal4807_released_rtdl_rayjoin_section57_api_map_2026-06-30.json`
- `docs/reviews/call_for_review_goal4807_released_rtdl_api_map_2026-06-30.md`

Exit gate:

- The report lists every released callable used by the external app.
- It explicitly marks missing released capabilities, especially Numba
  Section 5.7 device-column or continuation routes.
- It proves no planned step requires modifying RTDL source.
- For every Section 5.7 stage, the report labels the route as exactly one of:
  `generic_rtdl_operator`, `numba_user_continuation`,
  `bundled_rayjoin_helper`, `author_or_v214_baseline`, or
  `missing_released_capability`.
- `blocked_by_released_rtdl_capability_gap` remains an allowed and likely
  outcome.

## Goal4808 — External User App Skeleton

Purpose:

Create the independent user-layer reproduction entrypoint.  This is application
code, not RTDL runtime code.

Deliverable files:

- `examples/paper_reproduction/rayjoin_section57_released_user_app.py`
- `tests/goal4808_rayjoin_section57_released_user_app_contract_test.py`
- `docs/reports/goal4808_released_user_app_skeleton_2026-06-30.md`

Required commands exposed by the app:

- `preflight`
- `manifest`
- `run-author`
- `run-v214`
- `run-v4-released`
- `compare`

Exit gate:

- The app runs under a clean `v4.0.0` checkout with `PYTHONPATH=src`.
- The app does not import untagged Goal4806 helper modules.
- Tests prove it reports missing inputs/capabilities instead of crashing or
  silently changing scope.

## Goal4809 — Clean V4.0.0 Local User Smoke

Purpose:

Run the Goal4808 app as a simulated installed user from a clean `v4.0.0`
worktree.

Deliverable files:

- `docs/reports/goal4809_clean_v4_0_0_user_smoke_2026-06-30.json`
- `docs/reports/goal4809_clean_v4_0_0_user_smoke_2026-06-30.md`
- `docs/reviews/call_for_review_goal4809_clean_user_smoke_2026-06-30.md`

Exit gate:

- The smoke run records the exact `v4.0.0` commit.
- It records whether exact Section 5.7 CDB inputs are present.
- It records whether author binaries are present.
- It records whether released RTDL can execute the V4 route for available
  inputs.
- It contains no evidence from the dirty development worktree.

## Goal4810 — POD Preflight For Author / V2.14 / Released V4

Purpose:

Prepare the NVIDIA POD run without starting long performance work blindly.

Deliverable files:

- `docs/reports/goal4810_pod_section57_preflight_2026-06-30.json`
- `docs/reports/goal4810_pod_section57_preflight_2026-06-30.md`

Exit gate:

- POD path, GPU, driver, author repo commit, V2.14 route, clean V4.0.0 route,
  dataset root, and available Section 5.7 pairs are recorded.
- The report says whether the full 8-pair paper-preprocessed run is possible.
- If not, it identifies the maximum fair slice that can run now.

## Goal4811 — Exact County x Zipcode Three-Way Correctness Slice

Purpose:

Run the smallest exact-paper slice that can prove the workflow end to end:
County x Zipcode, full polygon overlay.

Deliverable files:

- `docs/reports/goal4811_county_zipcode_three_way_correctness_2026-06-30.json`
- `docs/reports/goal4811_county_zipcode_three_way_correctness_2026-06-30.md`
- generated app artifacts under `artifacts/goal4811_county_zipcode_three_way/`

Required comparisons:

- author C++/CUDA/OptiX output;
- V2.14 exact-suite output or equivalent historical route;
- released V4.0.0 user app output.

Exit gate:

- Correctness is byte-equal where possible; otherwise topology/geometry hash
  and output-chain-level mismatch diagnostics are recorded.
- Count-only evidence is not sufficient.

## Goal4812 — Released V4 + Numba User Continuation Assessment

Purpose:

Determine whether Numba can participate in the released-V4 user app without
modifying RTDL.  This goal does not add runtime features.

Deliverable files:

- `examples/paper_reproduction/rayjoin_section57_numba_user_continuation.py`
- `tests/goal4812_rayjoin_section57_numba_user_continuation_test.py`
- `docs/reports/goal4812_released_v4_numba_user_continuation_2026-06-30.md`
- `docs/reports/goal4812_released_v4_numba_user_continuation_2026-06-30.json`

Exit gate:

- If Numba can be used with released RTDL outputs, the app records exactly
  which data crosses the Python/Numba boundary and whether it remains in the
  hot path.
- If released RTDL lacks the needed device-column route, the report records
  that as a product gap.
- No RTDL source is modified.

## Goal4813 — POD Performance Slice

Purpose:

Measure the fair performance slice on the POD after correctness is established.

Deliverable files:

- `docs/reports/goal4813_section57_pod_performance_slice_2026-06-30.json`
- `docs/reports/goal4813_section57_pod_performance_slice_2026-06-30.md`

Required table columns:

- author code seconds;
- V2.14 route seconds;
- released V4.0.0 user app seconds;
- released V4.0.0 + Numba user continuation seconds, if Goal4812 proves it is
  valid;
- correctness status;
- input provenance.

Exit gate:

- Same hardware, same inputs, same timing boundary.
- No toy data.
- No broad claim beyond the measured slice.

## Goal4814 — Available-Pairs Expansion Or Data-Gap Closure

Purpose:

Decide whether Goal4806 can become all-eight-pair Section 5.7 reproduction, or
must close as a bounded available-input slice with explicit data gaps.

Deliverable files:

- `docs/reports/goal4814_section57_available_pairs_or_data_gap_2026-06-30.md`
- `docs/reports/goal4814_section57_available_pairs_or_data_gap_2026-06-30.json`

Exit gate:

- Exact paper-preprocessed CDB availability is listed for all eight pairs.
- Same-source regenerated rows are labeled separately and never counted as
  exact paper reproduction.
- If all eight pairs are unavailable, the report says exactly which missing
  data prevents completion.

## Goal4815 — Final Goal4806 Completion Packet And External Review

Purpose:

Produce the final decision packet for Goal4806.

Deliverable files:

- `docs/reports/goal4815_goal4806_final_completion_packet_2026-06-30.md`
- `docs/reports/goal4815_goal4806_final_completion_packet_2026-06-30.json`
- `docs/reviews/call_for_review_goal4815_goal4806_final_completion_packet_2026-06-30.md`

Allowed verdict labels:

- `complete_exact_section57_reproduction`
- `complete_bounded_available_input_reproduction`
- `blocked_by_missing_paper_inputs`
- `blocked_by_released_rtdl_capability_gap`
- `not_complete_requires_runtime_development`

Exit gate:

- The packet lists author / V2.14 / released V4 evidence.
- It states whether Goal4806 is complete under the original objective.
- It explicitly separates product gaps from reproduction-app bugs.
- External review is requested before any final completion claim.
