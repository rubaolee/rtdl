# Goal4816-A RayJoin Section 5.7 Paper/Source Contract Extraction

Date: 2026-06-30

Status: `goal4816_A_contract_extraction_complete_pending_review`

This is a read-only contract extraction record for Goal4816. It does not start
implementation, does not authorize POD performance runs, and does not authorize
any changes to `src/rtdsl/**`, `src/native/**`, or the v2.14 release surface.

## Scope

Goal4816 is the v2.14 RayJoin Section 5.7 Polygon Overlay reproduction line:

- released system: RTDL v2.14;
- partner: Numba, only as explicit user/application continuation;
- baseline: RayJoin authors' C++/CUDA/OptiX program;
- workload: Section 5.7 polygon overlay, not scalar-only LSI/PIP.

The goal is to reproduce the paper workload as exactly as available inputs and
released RTDL allow, then compare honestly. If released v2.14 lacks a necessary
generic capability, the result is a capability/input/semantics gap, not a
runtime patch.

## Inputs Read

### Paper

Local file:

`C:\Users\Lestat\Downloads\ics24 (1).pdf`

Read target sections:

- Section 3.1/3.2: LSI/PIP formulation, high-precision contract, conservative
  representation, degeneracy handling.
- Section 4.1 implementation notes: planar graph/CDB-like input, integer
  scaling, rational intersections, combined callback/intersection-shader style.
- Section 5.7: polygon overlay workload, dataset pairs, parameters, and Table 4
  reference timings.

PDF extraction check:

- pages: 13;
- relevant hits found around pages 2, 5-12 for Section 3.2, Polygon Overlay,
  Conservative Representation, Simulation of Simplicity, and Table 4.

### Author Source

Author source was read directly from the POD using clean committed content, not
the dirty working tree:

- POD: `root@157.157.221.29 -p 23132`;
- key that worked: `id_ed25519_rtdl_codex_current_pod`;
- author root: `/workspace/RayJoin_fresh`;
- commit: `02bf6220d6d20b04af77ee20364eced75cc029c9`;
- working tree status: dirty with Goal4806 debug edits in several files;
- authoritative read method: `git show HEAD:<file>`.

Files read from `HEAD`:

- `expr/run_overlay.sh`;
- `src/run_overlay.cu`;
- `src/app/map_overlay_rt.h`;
- `src/algo/rt_lsi_custom.cu`;
- `src/algo/rt_pip_custom.cu`;
- `src/app/output_chain.h`;
- `src/rt/primitive.h`;
- `src/config.h`.

### User-Provided Author-Reply Summary

Local file:

`C:\Users\Lestat\Downloads\rayjoin_pip_determinism_summary.md`

This file is treated as a first-class determinism/clarification input. It
explains the equal-height PIP nondeterminism and the required way to encode the
SoS tie-break into the reported OptiX intersection distance.

### Existing RTDL Evidence

Read or rechecked:

- `history/internal_docs/docs_reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay/section57_overlay_summary.md`;
- `history/release_reports/v2_14_internal_closeout_2026-06-30/rayjoin_author_vs_rtdl_caveat.md`;
- `history/release_reports/v2_14_internal_closeout_2026-06-30/public_rt_vs_embree_comparison.md`;
- archived Goal4806 RayJoin status and language-swap reports under
  `exp-project-1/untracked-current/tools___archive__goal4806_released_rtdl_rayjoin_attempt_2026-06-30/docs_reports/`.

## Paper Contract

### Workload

Section 5.7 Polygon Overlay combines:

1. line segment intersection (LSI);
2. point-in-polygon / point-location (PIP);
3. midpoint point-location for output-chain pieces;
4. output polygon chain construction and author-format output.

Therefore scalar LSI, scalar PIP, or a post-traversal continuation alone is not
full Section 5.7 reproduction.

### LSI Formulation

The paper and source formulate LSI as RT traversal over base-map line-segment
AABBs:

- query segment is cast as a ray from one endpoint toward the other;
- ray range is `[tmin, tmax] = [0, 1]`;
- candidate base edges found by RT traversal are validated by an exact segment
  intersection predicate;
- intersection pairs feed later overlay construction.

Author source confirmation:

- `src/algo/rt_lsi_custom.cu` raygen uses `tmin = 0` and `tmax = 1`;
- the intersection program iterates the grouped edge range and calls the exact
  LSI predicate before appending an intersection pair.

### PIP / Point-Location Formulation

PIP casts a vertical ray upward from each query point and selects the closest
valid boundary edge in the opposite map. The selected boundary edge is then
mapped to the containing face/polygon using left/right face metadata.

Author source confirmation:

- `src/algo/rt_pip_custom.cu` uses ray direction `(0, 1, 0)`;
- it computes `xsect_y` against candidate base edges;
- it rejects points outside edge x-bounds using the query-map-dependent SoS
  endpoint rule;
- it stores the closest edge id in the OptiX payload;
- `src/app/map_overlay_rt.h` transforms closest edge id to polygon id with the
  base map face-id rule.

### Precision Contract

Section 3.2 is not optional. A fair reproduction must preserve:

- scaled integer coordinates;
- high-precision line coefficients;
- exact intersection tests after RT candidate generation;
- rational intersection coordinates before final materialization;
- conservative AABBs for FP32 RT traversal;
- Simulation of Simplicity for degenerate boundary cases.

Author source confirmation:

- `src/config.h` uses `coord_t = double` and `coefficient_t = __int128`;
- `src/rt/primitive.h` expands AABB bounds with `next_float_from_double(...,
  ROUNDING_ITER)`, and `ROUNDING_ITER` is 2;
- `src/app/map_overlay_rt.h` represents midpoint/intersection calculations with
  rational `__int128` values before point-location;
- `src/app/output_chain.h` writes final coordinates with six-decimal formatting.

### Adaptive Grouping / Build Parameters

The author overlay script uses the Section 5.7 flags:

- `grid_size=15000`;
- `mode=rt`;
- `-fau`;
- `xsect_factor=0.1`;
- `enlarge=3.5`;
- serialized topology prefix;
- `check=true` for RT mode in the script, unless manually overridden.

Author source confirmation:

- `expr/run_overlay.sh` constructs the eight overlay pairs and passes those
  options to `polyover_exec`;
- `src/run_overlay.cu` maps `mode=rt` to `MapOverlayRT` and `QueryConfigRT`;
- `src/app/map_overlay_rt.h` builds grouped OptiX AABBs when adaptive grouping
  is enabled.

## Section 5.7 Dataset/Timing Contract

The paper's Section 5.7 overlay matrix has eight pairs:

| Pair | Paper processing sec | Paper preprocessing sec |
| --- | ---: | ---: |
| County x Zipcode | 0.12 | 0.07 |
| Block x Water | 0.23 | 0.12 |
| LKAF x PKAF | 0.01 | 0.01 |
| LKAS x PKAS | 0.04 | 0.05 |
| LKAU x PKAU | 0.01 | 0.01 |
| LKEU x PKEU | 0.20 | 0.20 |
| LKNA x PKNA | 0.25 | 0.21 |
| LKSA x PKSA | 0.02 | 0.01 |

These paper numbers are context, not direct local denominators. Any performance
claim must compare author code and RTDL on the same machine, same CDB inputs,
same semantics, and compatible timing boundary.

The author script expects CDB paths under:

- `point_cdb/<map>/<map>_Point.cdb`;
- `point_cdb/lakes/<continent>/lakes_<continent>_Point.cdb`;
- `point_cdb/parks/<continent>/parks_<continent>_Point.cdb`.

## Author-Reply Determinism Contract

The user-provided author-reply summary explains a critical PIP determinism rule.

Observed issue:

- LSI and map1 PIP counts were stable across repeated RT runs;
- map0 PIP positives varied;
- differences were exterior/non-exterior flips;
- when both runs classified a point as non-exterior, face ids agreed;
- differing candidates often shared the same vertical intersection height.

Root cause:

- equal-height boundary candidates can report the same primary `t`;
- OptiX accepts the first such candidate and tightens `tmax`;
- later equal-`t` candidates are rejected by strict pruning before the shader's
  internal slope comparison can see them;
- result can depend on BVH traversal order.

Required deterministic rule from the summary:

- compute normalized slope:
  `norm_slope = (atan(slope) + pi/2) / pi`;
- for query map 0, larger slope is preferred:
  `tie_breaker = norm_slope`;
- for query map 1, smaller slope is preferred:
  `tie_breaker = 1.0 - norm_slope`;
- report a perturbed distance:
  `t_reported = t_edge + max(t_edge, 1.0) * (1.0 - tie_breaker) * 1e-14`.

Implication:

- The SoS tie-break preference must be encoded in the reported OptiX `t`, not
  only in an internal comparison over `xsect_y`.
- Goal4816 must not silently invent a different RTDL policy.
- If released v2.14 cannot expose/preserve this contract in the app-only route,
  the correct result is a PIP tie-break/capability gap.

Important source/clarification tension:

- Author `HEAD:src/algo/rt_pip_custom.cu` contains the slope comparison inside
  the intersection program.
- That same `HEAD` source still reports the unperturbed `t` to OptiX.
- The author-reply summary explains why this is not enough for deterministic
  equal-height cases.
- Therefore future work must explicitly state whether it is reproducing the
  committed author `HEAD` behavior or the clarified deterministic behavior.

## Author Execution Path

`src/run_overlay.cu` confirms this phase order:

1. read map 0;
2. read map 1;
3. create overlay app;
4. load data to device;
5. initialize;
6. build index;
7. intersection edges;
8. locate vertices of both maps in the other map;
9. compute output polygons;
10. optionally check;
11. optionally write output.

`src/app/map_overlay_rt.h` confirms the RT overlay app uses:

- `LSIRT` for intersection edges;
- `PIPRT` for vertex point-location;
- sorted LSI rows by per-map edge id;
- midpoint projection between adjacent intersections on the same edge;
- midpoint point-location via PIP;
- output-chain writing through `WriteOutputChain`.

`src/app/output_chain.h` confirms the output contract includes:

- grouping intersections by edge;
- splitting original chains at intersection points;
- removing only consecutive duplicate points;
- assigning output face ids from paired polygon ids;
- assigning point ids;
- writing author-format chain rows and coordinates.

## Existing v2.14 Evidence To Carry Forward

Goal4380 already established real but bounded evidence:

| Pair | Paper RayJoin Processing (Preprocess) | Local Author RT Process | RTDL OptiX Total | RTDL Embree Total | RTDL LSI Count Match | Complete |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| County x Zipcode | 0.12 (0.07) | 5.521469 | 5.782340 | 15.121065 | True | True |
| Block x Water | 0.23 (0.12) | 27.943863 | 28.649871 | 53.792848 | True | True |

Boundaries:

- This is 2/8 available exact CDB subset evidence, not all-eight Section 5.7.
- It is near local author process wall on those two rows, not author hot-compute
  parity.
- It separates RTDL OptiX-vs-Embree from RTDL-vs-author-code.
- It does not prove full byte-equal overlay output for all pairs.

Goal4816 starts from this evidence; it must not rediscover it as if from zero.

## Classification Boundary For Goal4816-B

Every required Section 5.7 stage must be classified using this taxonomy:

- `existing_v2_14_primitive`;
- `bundled_rayjoin_helper`;
- `numba_partner_continuation`;
- `paper_app_logic`;
- `author_baseline_only`;
- `missing_input`;
- `missing_v2_14_capability`;
- `unresolved_pip_tie_break_contract`.

Known classification warnings:

- `src/rtdsl/rayjoin_overlay.py::_run_lsi_rows` is a bundled RayJoin helper, not
  proof that generic RTDL users can build Section 5.7 from public primitives.
- `src/rtdsl/rayjoin_overlay.py::_run_point_location_faces` and
  `_PreparedPointLocationRunner` are bundled RayJoin helpers, not generic PIP
  primitives unless the public v2.14 surface proves otherwise.
- Numba compact-mask/segmented/topology continuations can support app logic, but
  they do not replace the LSI/PIP/CR/SoS/output-chain contracts.

## Decisions For Next Goals

Goal4816-A supports the following next step, subject to review:

1. Goal4816-B should inventory exact v2.14 assets and classify every Section
   5.7 stage with the taxonomy above.
2. Goal4816-B must keep `bundled_rayjoin_helper` separate from
   `existing_v2_14_primitive`.
3. No implementation or POD performance run should start until Goal4816-B
   answers whether a generic-primitive + Numba route exists, whether only a
   bundled-helper route exists, or whether the goal is blocked by released v2.14
   capability/input/semantics gaps.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   No, because this step is read-only and turns the author reply into a concrete
   contract instead of racing into another implementation path.

2. **What would make this foolish?**
   It would be foolish to treat `rayjoin_overlay` helper code as a generic RTDL
   primitive, to ignore the PIP `t_reported` determinism issue, or to compare
   scalar/candidate rows as if they were full overlay reproduction.

3. **Is there another path that avoids being trapped in one bad idea?**
   Yes. If Goal4816-B shows released v2.14 only has bundled-helper coverage, we
   can close as bounded helper reproduction or capability gap instead of forcing
   a false generic-language claim.

4. **Can I start a different path that actually solves the problem?**
   Yes. The correct path is now: contract extraction -> capability map ->
   app-only design -> correctness -> POD performance, with no runtime edits.

## Exit Label

`goal4816_A_contract_extraction_complete_pending_review`
