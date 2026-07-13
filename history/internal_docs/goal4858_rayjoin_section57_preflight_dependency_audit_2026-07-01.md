# Goal4858 - RayJoin Section 5.7 Preflight Dependency Audit

Date: 2026-07-01

Exit label: `completed_section57_preflight__go_directly_to_57`

## Purpose

Goal4858 decides whether RayJoin Sections 5.4, 5.5, and 5.6 must be fully
reproduced before attempting Section 5.7 polygon overlay.

Decision:

**Do not fully reproduce 5.4, 5.5, or 5.6 before 5.7.**  Read them, extract the
dependencies that Section 5.7 needs, lock those dependencies into the Section
5.7 execution plan, and proceed directly to Section 5.7.

This goal did not run POD benchmarks, did not patch author source, and did not
modify RTDL runtime/native code.

## Evidence Read

Paper text:

- `C:\Users\Lestat\Downloads\ics24 (1).pdf`
- Local text extracts:
  - `history/internal_docs/ics24_pdf_text_extract.tmp.txt`
  - `history/internal_docs/_tmp_ics24_text_for_rayjoin_check.txt`

Author source contract already extracted in:

- `history/internal_docs/goal4816_A_rayjoin_section57_paper_source_contract_extraction_2026-06-30.md`

Current RTDL capability state:

- `history/internal_docs/goal4853_section52_lsi_final_reproduction_closure_2026-07-01.md`
- `history/internal_docs/goal4856_section53_pip_result_consistency_2026-07-01.md`
- `history/internal_docs/goal4857_planar_map_point_location_public_front_door_cleanup_2026-07-01.md`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/datasets.py`
- `src/rtdsl/rayjoin_overlay.py`
- `src/rtdsl/rayjoin_paper_suite.py`
- `scripts/rayjoin_section57_overlay_matrix.py`
- `scripts/rayjoin_paper_reproduction_suite.py`

Author-provided determinism note:

- `C:\Users\Lestat\Downloads\rayjoin_pip_determinism_summary.md`

## Paper-Section Dependency Table

| Paper section | What the paper says | Dependency for Section 5.7 | Goal4858 decision |
|---|---|---|---|
| 3.2 High arithmetic precision | RT Cores/OptiX use FP32; RayJoin preserves exact GIS answers by conservative AABBs, integer scaling, exact refinement, rational intersections, and SoS. | **Hard correctness dependency.** 5.7 cannot be evaluated if LSI/PIP point-location does not preserve this contract. | Apply to 5.7. Do not run a separate 3.2 reproduction. |
| 5.4 Precision evaluation | Default FP32 lost 745 LSI intersections and 524 PIP responses on LKNA x PKNA; conservative representation made LSI/PIP match FP64 and all datasets were verified. | **Correctness gate**, not a separate application workload. It tells us 5.7 must use the conservative/SoS path, not default FP32. | `dependency_only`. No full 5.4 reproduction before 5.7. |
| 5.5 Adaptive grouping / parameter tuning | Varying merge threshold `s` trades BVH build/memory against query time; `s=3.5` is the paper's practical point in the shown experiment. | **Parameter dependency.** 5.7 commands must lock the paper parameters and report whether adaptive grouping is enabled. | `dependency_only`. Extract parameters; no full sweep before 5.7. |
| 5.6 Scalability | Synthetic uniform/Gaussian datasets with 5M base polygons and 1M-5M query polygons; BVH build excluded; adaptive grouping disabled; reports LSI/PIP query scalability. | **Not a prerequisite** for 5.7 correctness. Useful later after 5.7 works to evaluate scale behavior of LSI/PIP primitives. | `defer_until_after_5_7`. |
| 5.7 Polygon overlay | Full overlay combines LSI, bidirectional vertex PIP, midpoint PIP, and output-chain construction; Table 4 reports overlay times over eight pairs. | **Target workload.** This is the integration test after 5.2/5.3 primitives. | Do next as Goal4859. |

## Locked Section 5.7 Parameters And Contracts

These must be carried into the next goal:

- author executable: `polyover_exec`;
- mode: `rt`;
- serialized topology prefix: usually `/dev/shm`;
- `grid_size=15000`;
- `-fau`;
- `xsect_factor=0.1`;
- `enlarge=3.5`;
- data shape: CDB point files under the paper paths in `src/rtdsl/rayjoin_paper_suite.py`;
- correctness target: author-format output, preferably byte-equal to author output or answer file;
- no performance comparison before correctness passes.

Precision/SoS contracts to preserve:

- conservative AABBs / conservative representation;
- exact LSI predicate after RT candidate generation;
- integer-scaled coordinates and rational intersection/midpoint handling where
  the overlay chain requires them;
- author-clarified PIP equal-height tie behavior, including the `t_reported`
  perturbation principle from `rayjoin_pip_determinism_summary.md`.

## Author-Source Dependency Map

The authoritative source extraction is Goal4816-A.  Goal4858 carries the map
forward as the preflight basis.

| Section 5.7 stage | Author source contract | Author file/function area | Notes |
|---|---|---|---|
| Top-level overlay command | Load two CDB maps, create overlay app, transfer to device, initialize, build index, run intersections, locate vertices, compute output polygons, optional check/write. | `src/run_overlay.cu`; script wrapper in `expr/run_overlay.sh` | This is the Section 5.7 application driver, not an isolated LSI/PIP microbench. |
| LSI | Cast query map segments over `[tmin,tmax]=[0,1]`; exact segment predicate inside OptiX after AABB candidate hit; emit intersection pairs for overlay. | `src/algo/rt_lsi_custom.cu` | Section 5.2 front door covers count; 5.7 needs rows/coordinates. |
| Vertex PIP / point-location | Cast vertical ray from each vertex; choose closest valid opposite-map boundary edge; convert edge side to face/polygon id. | `src/algo/rt_pip_custom.cu`; `src/app/map_overlay_rt.h` | Section 5.3 hash evidence covers serious cases for closest-edge outputs. |
| Midpoint point-location | Sort intersections per edge; compute midpoints between adjacent intersections; locate midpoint in the opposite map. | `src/app/map_overlay_rt.h` | This is where full overlay becomes more than scalar LSI/PIP. |
| Output-chain construction | Split chains at intersection/midpoint boundaries, assign face ids, deduplicate consecutive points, write author-format chain output. | `src/app/output_chain.h`; `src/app/map_overlay_rt.h` | This is app-layer paper logic. It should not be hidden as an RTDL primitive. |
| Precision / SoS | Scaled integer coordinates, conservative AABBs, rational intersections/midpoints, SoS tie handling. | `src/config.h`; `src/rt/primitive.h`; `src/algo/rt_pip_custom.cu`; author determinism note | Required before a correctness claim. |

## Current RTDL Capability Map For Section 5.7

This table updates older Goal4816-B/C maps with the later Goal4851/4857 public
front-door work.

| Section 5.7 stage | Current RTDL public/generic route | Classification | 5.7 status |
|---|---|---|---|
| CDB loading | `load_cdb`, `chains_to_planar_map_segments`, `chains_to_planar_map_points` | public generic RTDL data helpers | Available. |
| LSI count | `prepare_planar_map_lsi_2d_optix(base).count(query)` | public generic RTDL primitive | Available; Goal4853 matched available counts without bundled helper. |
| LSI rows / intersection coordinates | `prepare_segment_pair_intersection_optix` has pair-column and exact-intersection machinery; bundled overlay path still uses `_run_lsi_rows` to dump/materialize RayJoin overlay rows. | partial public primitive plus bundled-helper/app-layer gap | Must be checked in Goal4859. Full overlay needs row ids and coordinates, not only count. |
| Vertex PIP / point-location | `prepare_planar_map_point_location_2d_optix(base, query_map_id=...)` | public generic-named RTDL primitive over historical native route | Available; Goal4856 proved per-point closest-edge equality on two serious cases. |
| Midpoint projection | Python/Numba can compute midpoints once LSI rows/coordinates are available. | app-layer / Numba continuation | Feasible in principle; depends on LSI row/coordinate availability. |
| Midpoint PIP | Reuse `prepare_planar_map_point_location_2d_optix` on generated midpoint points. | public primitive plus app-layer generated points | Feasible if midpoint generation is correct and efficient. |
| Output-chain assembly | Existing `rayjoin_overlay._assemble_output_chains` and `write_output_chains` implement this, but they are bundled helper/paper app logic. | app-layer paper logic; bundled helper if reused directly | Goal4859 must decide: use existing app helper as bounded reproduction, or reimplement user-layer app logic without claiming it is a primitive. |
| Numba continuation | Existing Numba compact-mask/topology helpers can support post-RT continuation, filtering, and row transforms. | Numba partner continuation | Useful, but not a replacement for LSI/PIP traversal or output-chain correctness. |

## Explicit 5.4 / 5.5 / 5.6 Decisions

| Section | Decision | Reason | Risk carried into 5.7 |
|---|---|---|---|
| 5.4 | `dependency_only` | It validates why conservative representation is mandatory. It does not need to be reproduced before the overlay integration test. | If 5.7 mismatches, first check CR/SoS/precision before blaming overlay assembly. |
| 5.5 | `dependency_only` | It defines the adaptive-grouping/parameter tradeoff and the practical paper parameters. A full sweep is performance-tuning work, not a correctness prerequisite. | 5.7 must record `s`/AG, `enlarge=3.5`, `xsect_factor=0.1`, and `grid_size=15000`; performance claims must not compare different parameters silently. |
| 5.6 | `defer_until_after_5_7` | It is a synthetic LSI/PIP scalability experiment. It does not validate output-chain polygon overlay correctness. | After 5.7 works, run a scalability goal if we want paper completeness or primitive scaling evidence. |

No section receives `must_reproduce_before_5_7`.

## Resulting Goal4859 Direction

Proceed to Section 5.7.

The next goal should not be a performance run first. It should be a correctness
and route-clarity goal:

1. choose one available exact or recovered dataset pair first, preferably
   County x Zipcode because it is the smallest serious U.S. row and has the
   most prior evidence;
2. run or plan the AuthorPatch `polyover_exec` baseline under locked paper
   parameters;
3. run the RTDL route under a clearly labeled route:
   - `generic_public_primitives_plus_app_layer`, if it avoids private bundled
     helpers and uses public LSI/PIP front doors plus app-layer Python/Numba; or
   - `bounded_bundled_helper_reproduction`, if it uses `rayjoin_overlay`;
4. require byte-equal output or a named topology-hash diagnostic before any
   performance timing;
5. only after correctness passes, compare timing on the same machine and same
   input.

The concrete Goal4859 proposal is written separately:

`history/internal_docs/goal4859_rayjoin_section57_overlay_correctness_execution_plan_2026-07-01.md`

## What Goal4858 Did Not Do

- Did not run a full Section 5.4 precision reproduction.
- Did not run a full Section 5.5 adaptive-grouping sweep.
- Did not run a full Section 5.6 scalability experiment.
- Did not run POD performance commands.
- Did not modify `src/rtdsl/**` or `src/native/**`.
- Did not claim Section 5.7 reproduction.

## Worktree Note

The current worktree already contains modified RTDL product/runtime files from
previous RayJoin recovery goals.  Goal4858 does not claim the tree is clean.
The only Goal4858-introduced files are internal documentation/planning files
under `history/internal_docs/`.

## Completion Checklist

| Requirement from Goal4858 | Evidence | Status |
|---|---|---|
| paper-section dependency table for 3.2/5.4/5.5/5.6/5.7 | This report, "Paper-Section Dependency Table" | complete |
| author-source dependency map with file/function names | This report, "Author-Source Dependency Map"; Goal4816-A source extraction | complete |
| Section 5.7 RTDL capability map | This report, "Current RTDL Capability Map" | complete |
| explicit do/defer decisions for 5.4/5.5/5.6 | This report, "Explicit 5.4 / 5.5 / 5.6 Decisions" | complete |
| concrete Goal4859 Section 5.7 plan | `goal4859_rayjoin_section57_overlay_correctness_execution_plan_2026-07-01.md` | complete |
| no runtime/native edits by this goal | Goal4858 only wrote internal docs; current runtime diffs pre-existed | complete with caveat |
| no POD spend | No remote/POD execution was performed for Goal4858 | complete |

## Goal-Level Decision Audit

1. **Am I being foolish?**
   No.  The audit reads 5.4-5.6 for dependencies instead of turning them into
   side quests.  That keeps the work aimed at the real target: Section 5.7.

2. **What would make this foolish?**
   It would be foolish if I skipped a concrete 5.7 dependency.  The audit
   therefore carries forward 3.2/5.4 precision, 5.5 parameters, and author SoS
   behavior into Goal4859.

3. **Is there a better path than sequentially reproducing 5.4, then 5.5, then 5.6?**
   Yes.  The better path is dependency extraction followed by the decisive
   integration test: 5.7 overlay.

4. **Can I now solve the real problem?**
   Yes.  Goal4859 should begin with one correctness-focused 5.7 overlay pair
   and route-label discipline, not another microbenchmark.
