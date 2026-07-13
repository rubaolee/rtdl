# Goal4835 RayJoin Overlay Wide-Change Audit and v2.14 Regression Gate

Date: 2026-06-30

## Exit Label

`completed_rayjoin_focused_gate_passed__wide_change_audit_done__v214_wide_regression_not_green`

## Purpose

Goal4835 exists because Claude's Goal4833 method-reset review approved the
contract-first RayJoin repair line only with a hard warning: core/runtime edits
must not be grandfathered merely because a RayJoin sample passes.

The specific concern was that the current `src/rtdsl/rayjoin_overlay.py` diff is
much wider than the Goal4834 directed point-location SoS repair. This goal
audits those wider changes and runs a v2.14-wide regression gate before any
broader release-facing claim is made.

## Standing Boundary

- This is still the v2.14 public product line.
- V3/V4 work is irrelevant to this goal.
- Embree is not used for the RayJoin evidence in this goal; Embree only appears
  in legacy v2.14-wide regression tests that still exist in the test matrix.
- No broad RayJoin Section 5.7 claim is authorized by this goal.
- No performance win claim is authorized by this goal.

## Current Tracked Code/Test Diff

`git status --short` shows four tracked files changed:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/rtdsl/rayjoin_overlay.py`
- `tests/goal4373_rayjoin_cdb_point_location_route_test.py`
- `tests/goal4374_rayjoin_exact_paper_suite_test.py`

Plus one new focused test file:

- `tests/goal4834_rayjoin_sos_synthetic_contract_test.py`

## Wide-Change Audit

| Change area | Files/symbols | Current evidence | Classification | Decision |
| --- | --- | --- | --- | --- |
| Directed segment point-location SoS comparator | `src/native/optix/rtdl_optix_core.cpp`: `directed_segment_sos_*`, reported `t` perturbation, map-directed slope preference | Goal4834 synthetic tests; public County x Soil byte-equality; Antigravity review `approve_goal4834_correctness_repair_no_performance_win_claim` | `contract_supported_core_fix` | Retain for the current RayJoin repair line. It is justified by author/paper contract and synthetic gate, not by "RayJoin happened to pass." |
| Per-map midpoint face storage | `RayjoinOverlayIntersection.mid_point_polygon_id_map0/map1`, `_assign_midpoint_faces(... map_index)`, `_midpoint_face_for_map`, `_assemble_output_chains` | Goal4820 review approved it as a product/data-model repair; public sample byte-equality depends on not overwriting map0 face assignments with map1 assignments | `externally_reviewed_product_data_model_fix` | Retain. This is not a hidden RayJoin shortcut; one intersection object is reused in two directed map contexts and must store both faces. |
| Non-finite midpoint filtering | `_midpoint_points_from_lsi_rows_numpy(... stats)`, `_midpoints_for_sorted_xsects(... stats)`, `midpoint_pip` telemetry | Goal4826 review: nonfinite LSI rows/midpoints existed in same-source County x Zipcode; passing NaN/Inf to native point-location crashed; tests for dropping nonfinite midpoint points passed | `externally_reviewed_product_input_invariant_fix` | Retain for now. It enforces the general invariant that native point-location kernels receive finite query points. It does not prove exact Section 5.7 reproduction. |
| Author scaled coordinate materialization | `_rayjoin_author_scale_array`, `_rayjoin_scaling_constants`, `_rayjoin_scaled_intersection_points_for_pairs`, scaled/rational row fields | Goal4827 review approved the direction as following author `ExactPoint`/internal-coordinate behavior; tests cover scaled coordinate materialization | `externally_reviewed_contract_alignment_candidate` | Retain as a contract-alignment candidate. It is useful, but still not enough to claim full County x Zipcode or eight-pair Section 5.7 success. |
| Rational midpoint projection before truncation | `_midpoints_for_sorted_xsects(... scale_bounds)` with `Fraction` fields | `test_output_chain_midpoint_uses_rational_intersection_before_truncation`; Goal4827 review says this follows author `ExactPoint` midpoint construction | `contract_tested_candidate` | Retain. This directly addresses rational-vs-float midpoint drift. It still needs larger deterministic author-baseline validation before broad claims. |
| Intersection sorting tie behavior | `_sort_xsects_for_map(... scale_bounds)` now sorts by scaled distance from edge start and opposite edge id, not the older `(eid0,eid1)` pair | Goal4827 review says the old artificial `(eid0,eid1)` tie-break did not match author logic; Claude Goal4833 warned not to keep an unproven reactive sort-tie merely because it was tried | `partially_reviewed_but_not_release_complete` | Retain only as a hypothesis under audit. It is not enough by itself to prove County x Zipcode. A chain-30138 minimal reproducer remains the best next proof. |
| Device-face/no-count route | point-location `face_ids_device_points` mode and no-positive-count behavior | Existing Goal4374 tests assert no output path avoids positive count atomics and uses face IDs | `preexisting_or_earlier_route_evidence` | Keep. Not newly authorized by Goal4835; included here to avoid confusing it with the newer overlay correctness fixes. |

## Tests Run

### RayJoin-Focused Gate

Command:

```powershell
py -3 -m unittest tests.goal4834_rayjoin_sos_synthetic_contract_test tests.goal4373_rayjoin_cdb_point_location_route_test tests.goal4374_rayjoin_exact_paper_suite_test
```

Result:

```text
Ran 38 tests in 3.189s
OK
```

Interpretation:

- The focused RayJoin/SoS/overlay tests pass locally.
- This supports the correctness-repair line.
- It does **not** by itself prove v2.14-wide release safety.

### v2.14-Wide Local Regression Gate

Command:

```powershell
py -3 scripts/run_test_matrix.py --group full
```

Result:

```text
group: full
module_count: 41
Ran 264 tests in 291.292s
FAILED (errors=13, skipped=16)
```

Observed failure classes:

1. Legacy public-surface cleanup fallout:
   - `tests.baseline_integration_test`
   - `tests.rtdsl_language_test`
   - `tests.rtdsl_ray_query_test`
   - These still import `examples.internal.*`, but the v2.14 public-surface
     cleanup moved or removed that old internal example path.

2. Windows Embree compile/link failures in legacy v2.14 matrix tests:
   - `tests.goal32_lsi_sort_sweep_test`
   - `tests.report_smoke_test`
   - `tests.section_5_6_scalability_test`
   - These fail through Windows Embree native-library construction paths. This
     goal does not use Embree for RayJoin, but Claude AM3 asked for a v2.14-wide
     regression gate, so the failures must be recorded rather than ignored.

Interpretation:

- The v2.14-wide gate is **not green**.
- The failures appear unrelated to the RayJoin OptiX SoS comparator itself, but
  they still block any statement that "the full v2.14 matrix is clean after the
  core repair."
- A separate regression-harness cleanup goal is needed before a release-facing
  claim can say the product line is globally clean.

## What This Goal Proves

1. The Goal4834 correctness repair is not merely one passing sample:
   it is covered by a focused synthetic/direct RayJoin test gate.

2. The major `rayjoin_overlay.py` changes can be separated into:
   - externally reviewed product fixes;
   - contract-alignment candidates with tests;
   - still-open hypotheses that must not be promoted.

3. The project now has a clear stop sign:
   RayJoin focused tests are green, but v2.14-wide regression is not.

## What This Goal Does Not Prove

- It does not prove full Section 5.7 eight-pair reproduction.
- It does not prove County x Zipcode byte equality against a deterministic,
  patched-author baseline.
- It does not prove a performance win over the patched author binary.
- It does not prove the full v2.14 test matrix is clean.
- It does not authorize public-facing performance wording.

## Required Next Work

1. **Goal4836: v2.14 regression-harness cleanup.**
   Fix or explicitly retire stale tests that still import `examples.internal.*`
   after the public-surface cleanup. This is a test-harness/product-hygiene
   issue, not a RayJoin algorithm result.

2. **Goal4837: Linux/OptiX-only RayJoin regression confirmation.**
   Run the focused RayJoin gate on Linux/POD with rebuilt OptiX after the current
   code state is synchronized.

3. **Goal4838: chain-30138 minimal reproducer.**
   Build the minimal synthetic/contract regression around the known County x
   Zipcode first-diff region. This is the main open proof point for the
   scaled/rational/sort/midpoint branch.

4. **Goal4839: deterministic patched-author County x Zipcode comparison.**
   Only after Goal4838, compare current RTDL to a patched-author deterministic
   baseline on County x Zipcode. If it still fails, stop performance work and
   diagnose the next structural mismatch.

## Goal-Level Decision Audit

1. **Was this decision stupid?**
   No. Running the focused gate and the full matrix exposed the real boundary:
   RayJoin is locally repaired, but the broader v2.14 regression surface is not
   clean.

2. **What would have made it stupid?**
   Claiming that the focused 38-test pass equals a full product gate, or hiding
   the 13-error full matrix result.

3. **Was there another path that avoided overfocusing on one idea?**
   Yes: split the evidence into focused RayJoin correctness and v2.14-wide
   regression. That is exactly what this goal did.

4. **Can we now take a better path?**
   Yes. The next path is controlled: clean the stale regression harness, confirm
   RayJoin on Linux/OptiX, then build the chain-30138 minimal reproducer before
   any larger performance run.
