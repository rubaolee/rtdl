# X-HD Review Opinions Register

Date: 2026-07-07

This register tracks review status for the X-HD paper-app line. It does not
convert existing Hausdorff/X-HD-style benchmark evidence into X-HD paper
reproduction.

## Status Table

| Goal | Subject | Status | Notes |
| --- | --- | --- | --- |
| Goal5451 | X-HD same-input directed-HDResult scoped closeout | externally reviewed and approved | `review_goal5451_xhd_same_input_hdresult_closeout_verified_2026-07-10.md`; verdict `approve_goal5451_xhd_same_input_directed_hdresult_closeout`; 7/7 primary exact-witness cases plus 3/3 scalar-only routes match; current X-HD line closed at owner-approved scope |
| Goal5110 | X-HD requirements/provenance scaffold | externally reviewed and approved | `review_goal5110_xhd_scaffold_2026-07-07.md`; no reproduction claim; next target is `bounded_same_input_author_json_gate` |
| Goal5111 | Tiny same-input author JSON gate packet | externally reviewed and approved | Local exact reference and comparator runner ready; runner now fails closed when author subprocess fails |
| Goal5112 | Author `hd_exec` build/run on POD | externally reviewed and approved | POD `Author+BuildPatch` route built `hd_exec` and matched tiny WKT fixture: author `HDResult=1.0`, RTDL exact `1.0`, `abs_diff=0.0`, `matched=true`; no paper/performance claim |
| Goal5113 | Larger bounded same-input WKT gate | externally reviewed and approved | POD `Author+BuildPatch` route matched 10x9 bounded2d fixture: author `HDResult=2.0`, RTDL exact `2.0`, `abs_diff=0.0`, `matched=true`; no paper/performance claim |
| Goal5114 | Bounded 3D same-input WKT gate | externally reviewed and approved | POD `Author+BuildPatch` route matched 9x8 bounded3d fixture: author `HDResult=2.0`, RTDL exact `2.0`, `abs_diff=0.0`, `matched=true`; no paper/performance claim |
| Goal5115 | Bounded 2D RTDL public column route gate | externally reviewed and approved | Paper app now runs bounded2d through RTDL public 2D columnar Hausdorff APIs: author `HDResult=2.0`, RTDL route `2.0`, exact reference `2.0`, `matched=true`; no 3D route or performance claim |
| Goal5116 | X-HD completion boundary and phase model | externally reviewed and approved | Freezes evidence levels, final statuses, regime labels, and the rule that 5111-5115 are implementation evidence until external review |
| Goal5117 | Generic 3D Hausdorff column route contract | externally reviewed and approved | Adds app-neutral RTDL public 3D NumPy column route and non-X-HD tests; no X-HD/core identity |
| Goal5118 | Bounded 3D RTDL public column route gate | externally reviewed and approved | Paper app now runs bounded3d through RTDL public 3D columnar Hausdorff APIs: author `HDResult=2.0`, RTDL route `2.0`, exact reference `2.0`, `matched=true`; no performance claim |
| Goal5119 | X-HD author phase semantics and directed HD contract | externally reviewed and approved | Author `HDResult` is treated as directed input1-to-input2; `Running.AvgTime` is internal repeat `ReportedTime`, not process wall |
| Goal5120 | X-HD-style decision route feasibility | externally reviewed and approved | Existing 2D fixed-radius generic primitive can express a decision predicate; full X-HD iterative route needs new generic API; no X-HD primitive added |
| Goal5121 | Representative / exact dataset decision | externally reviewed and approved | Author logs reference external datasets, but exact paper inputs and `/local/storage/shared/HDDatasets` are unavailable in current evidence |
| Goal5122 | Representative correctness gate | externally reviewed and approved as skipped | Skipped because Goal5121 exited `paper_inputs_unavailable_bounded_fixtures_only` |
| Goal5123 | Bounded fair performance matrix | externally reviewed and approved | Publishes phase disclosure only; no author-vs-RTDL ratio because hardware and denominators do not align |
| Goal5124 | X-HD system API extraction | externally reviewed and approved | New generic `point_rows_to_numpy_columns_3d` and `directed_hausdorff_3d_numpy_columns`; app-owned wrapper/comparator remains outside core |
| Goal5125 | X-HD bounded same-input closeout packet | externally reviewed and approved | Final status `xhd_bounded_same_input_reproduction_complete`; exact paper and representative claims remain open |
| Goal5126 | Directed semantics discriminating gate amendment | externally reviewed and approved | Adds directed-asymmetric fixture with author `HDResult=0.5`, `directed_b_to_a=9.0`, symmetric diagnostic `9.0`; closes the reviewer RA-1; verified by `review_goals5111_5126_xhd_bounded_completion_verified_2026-07-08.md` |
| Goal5127 | Generic nearest pipeline extraction | externally reviewed and approved | Extracts app-neutral `pairwise_l2_distance_candidate_rows_numpy_columns -> nearest_witness_numpy_columns -> max_nearest_distance_witness_numpy_columns`; `directed_hausdorff_*_numpy_columns` remain compatibility wrappers; no performance or paper claim; verified by `review_goals5127_5128_xhd_system_extraction_verified_2026-07-08.md` |
| Goal5128 | Non-Hausdorff max-nearest consumer | externally reviewed and approved | Adds facility-service-radius / worst-served-demand test consuming the generic max-nearest pipeline without directed-Hausdorff wrappers; addresses Goal5127 non-blocking genericity note; verified by `review_goals5127_5128_xhd_system_extraction_verified_2026-07-08.md` |
| Goal5129 | Full paper reproduction plan | externally reviewed and approved with amendment incorporated | Defines full-reproduction levels, identifies dataset provenance as the next blocker, and proposes Goals5130-5136; Level C exact-dataset definition now requires file/hash/provenance evidence; no new reproduction or performance claim |
| Goal5130 | X-HD paper target matrix | implemented; review pending | Extracts dataset/table/figure targets into `xhd_paper_target_matrix_2026-07-08.json`; no figure reproduction or performance claim |
| Goal5131 | X-HD dataset provenance and acquisition matrix | implemented; review pending | Classifies exact paper inputs as unavailable in current evidence, identifies same-source candidates, and recommends a Level B Dragon-HappyBuddha first gate; no exact dataset claim |
| Goal5132 | Stanford graphics same-source acquisition | implemented; review pending | Acquires public Dragon/HappyBuddha Stanford archives, records hashes and PLY counts, and identifies PLY input bridge/scalability gaps; no author/RTDL gate yet |
| Goal5133 | X-HD PLY input bridge | implemented; review pending | Adds app-owned ASCII PLY vertex loader and parameterized `--input-type wkt|ply` gates; tiny PLY RTDL route matches exact reference; no author POD run yet |
| Goal5134 | Stanford graphics sample PLY gate packet | implemented; review pending | Creates deterministic Dragon/HappyBuddha res4 sample256 PLY fixtures and runs RTDL route vs exact reference; author POD gate pending |
| Goal5135 | Stanford graphics sample PLY author gate | implemented; review pending | Runs author hd_exec on POD for sample256 PLY and matches RTDL directed reference after explicit min-bound translation preprocessing; Level B bounded sample only |
| Goal5136 | Stanford graphics sample scaling | implemented; review pending | Extends Level B PLY correctness to sample1024 and sample2048, both matched; exposes exact-reference route scaling floor and recommends algorithmic gap analysis next |
| Goal5137 | X-HD algorithmic route gap analysis | implemented; review pending | Maps author RT source phases to generic RTDL API gaps; recommends generic grid-cell candidate API next; no code copy or performance claim |
| Goal5138 | Generic grid-cell candidate API reference | implemented; review pending | Adds app-neutral NumPy reference APIs for point-grid tight cell-MBR descriptors and radius cell-MBR candidate rows; no native/OptiX backend or X-HD performance claim |
| Goal5139 | Generic nearest-state frontier API reference | implemented; review pending | Adds app-neutral NumPy reference API for splitting cell candidates by current nearest state into inline, offload, and pruned frontiers; no native/OptiX backend or X-HD performance claim |
| Goal5140 | Generic cell-MBR traversal native ABI | implemented; review pending | Specifies app-neutral native/RT ABI row schema for cell-MBR nearest frontiers and adds a row-table adapter; no backend implementation or X-HD performance claim |
| Goal5141 | Generic cell-MBR backend feasibility | implemented; review pending | Audits existing generic AABB/OptiX/fixed-radius/nearest-witness native assets and concludes an OptiX backend spike is feasible but requires a new app-neutral native symbol; no backend or performance claim |
| Goal5142 | Backend-assisted 2-D cell-MBR front door | implemented; review pending | Adds executable generic 2-D route from AABB membership backend rows to Goal5140 frontier row tables; local CPU backend tests pass; OptiX POD validation and true native symbol remain future work; no X-HD performance claim |
| Goal5143 | OptiX backend local availability probe | implemented; review pending | Attempted Goal5142 route with backend=\"optix\" locally; blocked by missing CUDA driver library (`libcuda.so.1`); POD validation required; no correctness/performance claim |
| Goal5144 | POD OptiX backend-assisted gate | implemented; review pending | Adds reusable CPU/OptiX backend-assisted gate runner; CPU summary matched; after correcting the POD SSH key, current `librtdl_optix.so` was built on POD and the OptiX gate matched with `broadphase_native_symbol=rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows`; no native Goal5140 backend or X-HD performance claim |
| Goal5145 | Dimension-generic cell-MBR front door | implemented; review pending | Adds public `cell_mbr_nearest_frontier_numpy_columns`, a 2-D/3-D NumPy reference front door that composes generic cell-MBR candidates, nearest-state frontier splitting, and Goal5140 row-table output; 3-D synthetic fixture matched manual composition; no native backend or X-HD performance claim |
| Goal5146 | Native 3-D AABB point-membership row producer | implemented; review pending | Adds app-neutral native OptiX 3-D AABB index prepare/collect/destroy symbols and Python wrappers; POD gate matched a synthetic overlapping-box fixture using `rtdl_optix_collect_prepared_aabb_index_3d_point_contains_rows`; this is a generic 3-D broadphase brick, not a complete Goal5140 cell-MBR nearest-frontier backend or X-HD performance route |
| Goal5147 | Backend-assisted 3-D cell-MBR front door | implemented; review pending | Adds public `cell_mbr_nearest_frontier_aabb_membership_3d_numpy_columns`, which uses CPU or native OptiX 3-D AABB membership rows as broadphase input, then generic NumPy exact filtering and nearest-state/frontier lowering; local CPU and POD OptiX gates matched the Goal5145 oracle; still not a complete native Goal5140 backend or X-HD performance route |
| Goal5148 | Native 3-D cell-MBR frontier row producer | implemented; review pending | Adds bounded app-neutral native OptiX 3-D cell-MBR nearest-frontier row producer `rtdl_optix_collect_cell_mbr_nearest_frontier_3d`; POD gate matched the Goal5145 oracle; not full 2-D/3-D Goal5140 backend or X-HD performance route |
| Goal5149 | Cell-MBR frontier nearest continuation | implemented; review pending | Adds generic `nearest_witness_from_cell_mbr_frontier_numpy_columns` with a non-Hausdorff facility/service-radius consumer; still a partner/reference continuation, not native fused RT-core |
| Goal5150 | X-HD bounded3D cell-MBR frontier route gate | implemented; review pending | Connects generic grid-cell MBRs, native/NumPy frontier rows, Goal5149 continuation, and max-nearest reduction; local NumPy and POD OptiX matched author HDResult and exact reference; no performance claim |
| Goal5151 | X-HD sample256 cell-MBR frontier route gate | implemented; review pending | Extends the route to Stanford graphics sample256 Level B fixture under min-bound translation; local NumPy and POD OptiX matched author/exact but still all-pairs continuation work |
| Goal5152 | Nearest-cell-MBR seeded pruning | implemented; review pending | Adds generic nearest-cell-MBR initial-state seed; sample256 POD OptiX remains matched and reduces candidate point-distance evaluations to about 1,200 per direction; work-reduction evidence only |
| Goal5153 | Vectorized nearest-cell-MBR seed | implemented; review pending | Vectorizes seed MBR selection; sample256 POD OptiX remains matched and records `numpy_vectorized_min_distance_then_cell_id`; not a fair performance matrix |
| Goal5154 | Seeded sample256/sample1024 performance matrix | implemented; review pending | Same-POD matrix separates author `Running.AvgTime`, author process wall, RTDL route, RTDL total, load, and exact-reference validation; both cases matched; no ratio authorized |
| Goal5155 | Production-mode author-only matrix and route profile | implemented; review pending | Adds `validation_mode=author-only` to skip exact-reference validation in production-style timing and records seed/frontier/continuation/reduce subphase timings; sample256/sample1024 POD matrix matched author HDResult; no speedup/parity ratio authorized |
| Goal5156 | Route phase median profile | implemented; review pending | Extends the production matrix with per-repeat subphase runs and medians for both directed routes; sample1024 median profile shows nearest continuation and seed dominate native frontier; no speedup/parity ratio authorized |
| Goal5157 | Vectorized frontier nearest continuation | implemented; review pending | Replaces row-by-row Python scanning in the generic frontier nearest continuation with vectorized expand + lexsort reduction; sample1024 production route median improves from ~0.289s to ~0.170s vs Goal5156; no author parity/speedup ratio authorized |
| Goal5158 | Vectorized nearest-cell-MBR seed | implemented; review pending | Replaces per-query nearest-cell-MBR seed selection and selected-cell point scanning with vectorized ordered argmin plus expand + lexsort reduction; sample1024 production route median improves from ~0.170s to ~0.114s vs Goal5157; no author parity/speedup ratio authorized |
| Goal5159 | Row-table-only native frontier route | implemented; review pending | Adds compatibility-preserving `return_split_frontiers=False` for generic native 3-D cell-MBR frontier rows and uses it in the X-HD route; sample1024 production route median improves modestly from ~0.114s to ~0.108s vs Goal5158; remaining frontier cost is row volume/production, not split materialization |
| Goal5160 | Active-row-only native frontier emission | implemented; review pending | Adds compatibility-preserving `emit_pruned_rows=False` for generic native 3-D cell-MBR frontier rows and uses it in the streaming X-HD route together with `return_split_frontiers=False`; sample1024 production route median improves from ~0.108s to ~0.079s vs Goal5159; frontier rows collapse from 189472/82544 to 2272/2185; no author parity/speedup ratio authorized |
| Goal5161 | Numba nearest-cell-MBR seed executor | implemented; review pending | Adds generic `executor=auto|numpy|numba` to the nearest-cell-MBR seed helper; Numba preserves the same tie-break semantics while avoiding the large NumPy matrix and expand/lexsort intermediates; sample1024 production route median improves from ~0.079s to ~0.022s vs Goal5160; no author parity/speedup ratio authorized |
| Goal5162 | Post-Numba-seed sample2048 profile | implemented; review pending | Extends the seeded performance matrix to sample2048 and runs the current OptiX route on POD; author HDResult matched, RTDL route median is ~0.059s, and nearest continuation is the dominant measured phase; no author parity/speedup ratio authorized |
| Goal5163 | Numba frontier nearest continuation executor | implemented; review pending | Adds generic `executor=auto|numpy|numba` to the cell-MBR frontier nearest continuation helper; sample2048 author HDResult matched and route median improves from ~0.059s to ~0.025s vs Goal5162; no author parity/speedup ratio authorized |
| Goal5164 | Post-Goal5163 three-sample matrix | implemented; review pending | Runs the current post-Goal5163 route on sample256/sample1024/sample2048 in one same-POD matrix; all cases matched author HDResult with route medians ~0.009s/~0.025s/~0.025s; no author parity/speedup ratio authorized |
| Goal5165 | Sample4096 Level B scaling matrix | implemented; review pending | Prepares deterministic 4096-point Stanford Dragon/HappyBuddha res4 samples and runs the current post-Goal5163 OptiX route on POD; author HDResult matched, route median is ~0.041s and total median ~0.067s; no author parity/speedup ratio authorized |
| Goal5166 | Full public res4 Level B scaling matrix | implemented; review pending | Prepares normalized full public Stanford Dragon/HappyBuddha res4 fixtures (5205 vs 7108 points) and runs the current post-Goal5163 OptiX route on POD; author HDResult matched, route median is ~0.059s and total median ~0.100s; no author parity/speedup ratio authorized |
| Goal5167 | Generic grid cell-MBR reduceat construction | implemented; review pending | Replaces per-cell Python min/max loops in the app-neutral `point_grid_cell_mbrs_numpy_columns` helper with NumPy `reduceat`; full public res4 POD route remains matched and route median improves from ~0.059s to ~0.052s vs Goal5166, with combined grid-MBR construction falling from ~11.5ms to ~3.7ms; no author parity/speedup ratio authorized |
| Goal5168 | Generic parallel nearest-cell-MBR seed executor | implemented; review pending | Adds a Numba `prange` executor path for the app-neutral nearest-cell-MBR seed helper while preserving NumPy and serial Numba paths; full public res4 POD route remains matched and route median improves from ~0.052s to ~0.039s vs Goal5167, with combined seed time falling from ~20.0ms to ~6.4ms; no author parity/speedup ratio authorized |
| Goal5169 | Streaming native frontier inferred-capacity retry | implemented; review pending | Adds a fail-closed inferred row-capacity retry policy for app-neutral native 3-D cell-MBR frontier rows when streaming consumers suppress pruned rows; explicit row_capacity still fails without retry. Full public res4 POD route remains matched and route median improves from ~0.039s to ~0.036s vs Goal5168; no author parity/speedup ratio authorized |

## Carry-Forward Boundaries

- Full X-HD paper reproduction: not closed.
- Exact paper dataset reproduction: not closed.
- Author `hd_exec` build/run gate: bounded tiny, bounded2d, and bounded3d same-input gates matched on POD using documented build-compatibility patch.
- Performance or speedup: not claimed.
- Author `Running.AvgTime` and process wall are tracked as separate metrics.
- Author `HDResult` comparator is directed input1-to-input2.
- Exact paper datasets and representative same-source datasets: not available in current evidence.
- Existing `hausdorff_xhd` benchmark evidence: historical RTDL asset evidence,
  not paper reproduction.
- Goal5127 and Goal5128 are externally reviewed and approved. They close the
  system-extraction line by keeping Hausdorff as an app-level wrapper over
  generic nearest/witness/reduction helpers and by adding an independent
  non-Hausdorff consumer. They do not alter the bounded same-input reproduction
  status or authorize performance claims.
- Goal5129 is a plan-only step for possible full paper reproduction and has been
  externally reviewed with amendment incorporated. It is not evidence that exact
  paper datasets, figure reproduction, or performance parity are available.
- Goal5130 and Goal5131 are implemented but not yet externally reviewed. They
  are planning/provenance evidence only: exact paper datasets remain unavailable
  in current evidence, and the next actionable step is at most a Level B
  same-source representative gate unless files/hashes/provenance are found.
- Goal5132 is implemented but not yet externally reviewed. It acquired Stanford
  Dragon/HappyBuddha source archives for a Level B graphics path, but no
  correctness or performance gate has run on those PLY files.
- Goal5133 is implemented but not yet externally reviewed. It adds app-owned PLY
  input support and tiny PLY smoke evidence only. It does not claim author
  success, representative correctness, or performance on Stanford inputs.
- Goal5134 is implemented but not yet externally reviewed. It prepares a
  bounded Stanford graphics PLY gate packet and validates the RTDL half against
  exact reference; author POD execution remains pending.
- Goal5135 is implemented but not yet externally reviewed. It closes the
  sample256 PLY author gate under an explicit author-style min-bound translation
  preprocessing contract. This is Level B bounded correctness only, not exact
  paper dataset or performance reproduction.
- Goal5136 is implemented but not yet externally reviewed. It closes larger
  Level B sample1024/sample2048 correctness gates and shows the current exact
  reference route is not a full-resolution performance route.
- Goal5137 is implemented but not yet externally reviewed. It uses author source
  as behavioral evidence and identifies the next generic system API track:
  grid-cell descriptors, radius-expanded traversal, nearest-state reducers,
  offload queues, and radius controllers.
- Goal5138 is implemented but not yet externally reviewed. It extracts the first
  generic system contract from that track: point columns to tight grid-cell MBR
  descriptors, then radius cell-MBR candidate rows. It is a NumPy reference
  front door only, with no native/OptiX backend and no X-HD performance claim.
- Goal5139 is implemented but not yet externally reviewed. It extracts the next
  generic system contract from that track: current nearest-state pruning and
  inline/offload/pruned frontier splitting over generic cell candidates. It is a
  NumPy reference front door only, with no native/OptiX backend and no X-HD
  performance claim.
- Goal5140 is implemented but not yet externally reviewed. It specifies the
  native/RT ABI row schema for that frontier and an adapter that flattens
  reference frontiers into ABI-shaped row columns. It does not implement a
  backend and does not authorize any performance claim.
- Goal5141 is implemented but not yet externally reviewed. It is a feasibility
  audit only: existing generic native assets are reusable patterns, but no
  Goal5140 backend exists yet. The next implementation step, if approved, is a
  bounded OptiX correctness spike with an app-neutral native symbol.
- Goal5142 is implemented but not yet externally reviewed. It adds an executable
  2-D backend-assisted front door over generic AABB membership rows and
  Goal5140 row-table output. Local CPU backend tests pass. The dedicated native
  OptiX symbol, 3-D route, and X-HD performance route remain unimplemented.
- Goal5143 is implemented but not yet externally reviewed. It is a local
  environment probe only: backend=\"optix\" could not run because the CUDA driver
  library was unavailable. OptiX correctness remains pending a POD gate.
- Goal5144 is implemented but not yet externally reviewed. It adds the reusable
  POD gate runner and records matched CPU and POD OptiX summaries for the
  backend-assisted 2-D front door. The earlier auth-blocked attempt is
  superseded by an authenticated POD run using the current POD key. The verified
  native symbol is the generic AABB broadphase
  `rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows`; this is not a
  complete native Goal5140 backend and does not authorize any X-HD performance
  claim.
- Goal5145 is implemented but not yet externally reviewed. It adds a public
  dimension-generic NumPy reference front door for Goal5140 row tables. This is
  the 3-D oracle needed before any native 3-D cell-MBR backend; it is not itself
  a native backend, OptiX 3-D support, or X-HD performance route.
- Goal5146 is implemented but not yet externally reviewed. It adds the first
  app-neutral native OptiX 3-D AABB broadphase brick for this track:
  `rtdl_optix_prepare_aabb_index_3d`,
  `rtdl_optix_collect_prepared_aabb_index_3d_point_contains_rows`, and
  `rtdl_optix_destroy_prepared_aabb_index_3d`. The POD gate matched a synthetic
  overlapping-box point-membership fixture. This still does not implement the
  full Goal5140 native cell-MBR nearest-frontier backend, nearest-state payload
  pruning, offload queues, X-HD RT-core algorithm, or any X-HD performance
  claim.
- Goal5147 is implemented but not yet externally reviewed. It connects Goal5146
  broadphase rows to the existing generic NumPy exact distance filter,
  nearest-state frontier split, and Goal5140 row-table adapter. Local CPU and
  POD OptiX gates matched the Goal5145 dimension-generic oracle. This is a
  backend-assisted front door, not a fully fused native cell-MBR traversal
  backend: frontier classification still runs outside native traversal, and no
  X-HD performance claim is authorized.
- Goal5148 is implemented but not yet externally reviewed. It adds a bounded
  app-neutral native OptiX 3-D cell-MBR nearest-frontier row producer,
  `rtdl_optix_collect_cell_mbr_nearest_frontier_3d`, plus the public
  `cell_mbr_nearest_frontier_native_3d_optix_columns` wrapper. Local source/API
  tests pass and the POD OptiX gate matched the Goal5145 dimension-generic
  oracle. This moves exact point-to-cell-MBR filtering and nearest-state
  frontier kind classification into native traversal for 3-D, but it is still
  not the full 2-D/3-D Goal5140 native ABI backend and does not authorize X-HD
  performance or full paper reproduction claims.
- Goal5149 is implemented but not yet externally reviewed. It adds the generic
  `nearest_witness_from_cell_mbr_frontier_numpy_columns` continuation, which
  consumes generic cell-MBR frontier row tables and target cell point spans to
  produce nearest-witness columns. Local tests include a non-Hausdorff
  facility/service-radius consumer, keeping the helper on the system side
  rather than as an X-HD-specific operation. This is still a partner/reference
  continuation, not a native fused RT-core continuation and not a performance
  claim.
- Goal5150 is implemented but not yet externally reviewed. It connects the
  generic grid-cell MBRs, native/NumPy cell-MBR frontier rows, Goal5149 nearest
  continuation, and generic max-nearest reduction into a bounded3D X-HD route
  gate. Local NumPy and POD OptiX runs both matched the directed input1-to-input2
  author HDResult and exact reference on the bounded3D fixture. The POD OptiX
  route uses `rtdl_optix_collect_cell_mbr_nearest_frontier_3d`. This is not full
  paper reproduction, not author fused RT-core equivalence, and not a
  performance claim; the nearest-witness continuation remains outside native
  traversal.
- Goal5151 is implemented but not yet externally reviewed. It runs the same
  cell-MBR frontier route on the Stanford graphics sample256 same-source PLY
  fixture under the established min-bound translation contract. Local NumPy and
  POD OptiX runs both matched the directed input1-to-input2 author HDResult and
  exact reference. The POD OptiX route uses
  `rtdl_optix_collect_cell_mbr_nearest_frontier_3d`. This is representative
  Level B correctness evidence only: it still evaluates all 65,536 point pairs
  in each directed pass and does not authorize any performance, author fused
  RT-core, exact paper dataset, or full paper reproduction claim.
- Goal5152 is implemented but not yet externally reviewed. It adds the generic
  `seed_nearest_witness_from_nearest_cell_mbr_numpy_columns` nearest-state
  initializer and wires it into the X-HD cell-MBR route behind
  `--initial-state nearest-cell-mbr`. On the Stanford sample256 fixture, local
  NumPy and POD OptiX seeded routes still matched author HDResult and exact
  reference while reducing candidate point-distance evaluations from 65,536 per
  direction to roughly 1,200 total seed+continuation evaluations per direction.
  This is algorithmic work-reduction evidence, not a performance claim: the
  seed still performs tens of thousands of Python cell-MBR tests.
- Goal5153 is implemented but not yet externally reviewed. It preserves the
  generic nearest-cell-MBR seed API but vectorizes the internal query-by-cell
  MBR lower-bound selection. Local and POD tests pass, and the Stanford sample256
  POD OptiX route remains matched while reporting
  `initial_cell_mbr_selection=numpy_vectorized_min_distance_then_cell_id`.
  The single POD route run reports about 0.37s route / 0.48s total, but this is
  not a fair author-vs-RTDL performance matrix or parity claim.
- Goal5154 is implemented but not yet externally reviewed. It adds a same-POD
  seeded performance matrix for sample256 and sample1024. It reruns author
  `hd_exec` and the RTDL seeded OptiX route, separates author `Running.AvgTime`,
  author process wall, RTDL route time, RTDL total time, input load time, and
  exact-reference validation time, and deliberately reports no speedup/parity
  ratio. Both cases matched author HDResult and exact reference. The matrix
  shows the current route is still far from author `Running.AvgTime`, especially
  on sample1024.
- Goal5155 is implemented but not yet externally reviewed. It adds an explicit
  production-style `author-only` validation mode, where exact-reference
  validation is skipped and recorded as `null` rather than as a failure. The
  sample256/sample1024 POD production matrix matched author HDResult, records no
  speedup/parity ratio, and exposes route subphase timings. This does not weaken
  the exact-validation gates from Goal5154; it separates production timing from
  validation timing and shows the next performance targets are seed,
  nearest-continuation, and native frontier phases.
- Goal5156 is implemented but not yet externally reviewed. It upgrades the
  Goal5155 profile from last-run-only to per-repeat phase runs plus median
  subphase timings. The sample1024 median profile shows nearest continuation
  (~0.135s combined) and nearest-cell-MBR seed (~0.092s combined) exceed native
  frontier rows (~0.050s combined), so the next optimization target should be
  selected from median evidence rather than last-run noise.
- Goal5157 is implemented but not yet externally reviewed. It vectorizes the
  generic `nearest_witness_from_cell_mbr_frontier_numpy_columns` continuation
  with expand + lexsort reduction while preserving seed and tie-break semantics.
  On the same POD production matrix, sample1024 route median improves from
  ~0.289s to ~0.170s compared with Goal5156, and the continuation phase drops
  from ~0.135s combined to ~0.010s combined. This is an RTDL route improvement,
  not author parity or full paper reproduction.
- Goal5158 is implemented but not yet externally reviewed. It vectorizes the
  generic `seed_nearest_witness_from_nearest_cell_mbr_numpy_columns` helper,
  replacing per-query nearest-cell selection and selected-cell point scanning
  with ordered vectorized argmin plus expand + lexsort reduction. On the same
  POD production matrix, sample1024 route median improves from ~0.170s to
  ~0.114s compared with Goal5157, and the combined seed phase drops from
  ~0.096s to ~0.041s. This remains an RTDL route improvement only; it is not
  author parity, a denominator-aligned speedup ratio, or full paper
  reproduction.
- Goal5159 is implemented but not yet externally reviewed. It adds a
  compatibility-preserving `return_split_frontiers=False` mode to the generic
  native 3-D cell-MBR frontier helper and uses it in the X-HD route, which only
  consumes the ABI row table. On the same POD production matrix, sample1024
  route median improves modestly from ~0.114s to ~0.108s compared with Goal5158.
  The diagnostic result is that split-frontier materialization was only a small
  part of the remaining frontier cost; native row volume/production remains the
  next hard target.
- Goal5160 is implemented but not yet externally reviewed. It adds a
  compatibility-preserving `emit_pruned_rows=False` native ABI option to the
  generic 3-D cell-MBR frontier producer and uses it in the X-HD streaming route.
  The route still gets the same author HDResult, while sample1024 frontier rows
  drop from 189472/82544 to 2272/2185 and the production route median improves
  from ~0.108s to ~0.079s compared with Goal5159. This is an RTDL route
  improvement only; it is not author parity, a denominator-aligned speedup
  ratio, or full paper reproduction.
- Goal5161 is implemented but not yet externally reviewed. It adds a generic
  `executor=auto|numpy|numba` option to
  `seed_nearest_witness_from_nearest_cell_mbr_numpy_columns`. The Numba executor
  preserves the existing nearest-cell and nearest-point tie-break semantics
  while avoiding the large NumPy query-by-cell matrix and expand/lexsort
  intermediates. On the same POD production matrix, sample1024 route median
  improves from ~0.079s to ~0.022s compared with Goal5160. This is an RTDL
  route improvement only; it is not author parity, a denominator-aligned speedup
  ratio, or full paper reproduction.
- Goal5162 is implemented but not yet externally reviewed. It extends the same
  performance/profile matrix to the existing Stanford sample2048 fixture. The
  POD run matched author HDResult with `validation_mode=author-only`, reports
  sample2048 route median ~0.059s, and shows nearest continuation is now the
  dominant measured phase. This is profile evidence only; it is not author
  parity, a denominator-aligned speedup ratio, or full paper reproduction.
- Goal5163 is implemented but not yet externally reviewed. It adds a generic
  `executor=auto|numpy|numba` option to
  `nearest_witness_from_cell_mbr_frontier_numpy_columns`, preserving the NumPy
  fallback and active-row/seeded-state semantics while avoiding the
  expand/lexsort candidate arrays. On the same sample2048 POD matrix, route
  median improves from ~0.059s to ~0.025s compared with Goal5162. This is an
  RTDL route improvement only; it is not author parity, a denominator-aligned
  speedup ratio, or full paper reproduction.
- Goal5164 is implemented but not yet externally reviewed. It records the
  current post-Goal5163 route on sample256/sample1024/sample2048 in one same-POD
  matrix. All cases matched author HDResult, route medians are
  ~0.009s/~0.025s/~0.025s, and no author-vs-RTDL speedup/parity ratio is
  authorized. This is the current route lock point, not full paper reproduction.
- Goal5165 is implemented but not yet externally reviewed. It extends the same
  post-Goal5163 production route to deterministic sample4096 Stanford graphics
  fixtures prepared from public Dragon/HappyBuddha res4 PLYs. The POD run
  matched author HDResult with `validation_mode=author-only`; RTDL route median
  is ~0.041s and total median is ~0.067s. This is Level B scaling evidence only,
  not exact paper dataset reproduction, denominator-aligned author performance,
  or full paper reproduction.
- Goal5166 is implemented but not yet externally reviewed. It extends the same
  post-Goal5163 production route to full public Stanford res4 fixtures:
  Dragon 5205 points vs HappyBuddha 7108 points. The POD run matched author
  HDResult with `validation_mode=author-only`; RTDL route median is ~0.059s and
  total median is ~0.100s. This is the strongest current Level B Stanford
  graphics scale point, but still not exact paper dataset reproduction,
  denominator-aligned author performance, or full paper reproduction.
- Goal5167 is implemented but not yet externally reviewed. It replaces per-cell
  Python min/max loops in the generic `point_grid_cell_mbrs_numpy_columns`
  helper with NumPy `reduceat` segmented reductions. The full public res4 POD
  route still matched author HDResult with `validation_mode=author-only`; route
  median improves to ~0.052s and total median to ~0.092s. This is a generic
  RTDL route improvement only.
- Goal5168 is implemented but not yet externally reviewed. It adds a generic
  Numba parallel executor for nearest-cell-MBR seeding while preserving the
  NumPy and serial Numba modes. The full public res4 POD route still matched
  author HDResult; route median improves to ~0.039s and total median to
  ~0.079s. This is not exact paper reproduction or an author-performance ratio.
- Goal5169 is implemented but not yet externally reviewed. It adds fail-closed
  inferred-capacity retry for streaming native 3-D cell-MBR frontier rows when
  `row_capacity is None` and `emit_pruned_rows=False`. The full public res4 POD
  route still matched author HDResult; route median improves to ~0.036s and
  total median to ~0.075s. This remains a no-ratio Level B route result.
- Goal5170 is implemented but not yet externally reviewed. It adds a race-free
  grouped Numba parallel executor for
  `nearest_witness_from_cell_mbr_frontier_numpy_columns` and records a same-POD
  serial-vs-parallel control. The full public res4 POD route still matched
  author HDResult; the parallel route median is ~0.034s and total median is
  ~0.075s. The continuation subphase improves modestly; no paper-performance
  or author-parity ratio is authorized.
- Goal5171 is implemented but not yet externally reviewed. It adds an
  app-neutral `sort_rows` / row-order policy to the native 3-D cell-MBR
  frontier collector while preserving the legacy sorted+unique default. The X-HD
  streaming route can explicitly request `frontier_row_order=native`, which
  uses the new `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2` symbol and
  leaves rows in backend emission order. The full public res4 same-POD route
  still matched author HDResult; the sorted-control route median is ~0.03376s
  and the native-unsorted route median is ~0.03309s. The win is small because
  some frontier sorting savings move into continuation grouping cost. No
  paper-performance or author-parity ratio is authorized.
- Goal5172 is implemented but not yet externally reviewed. It adds an
  app-neutral `inline_nearest` mode to the native 3-D cell-MBR frontier
  collector, exposed as
  `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3`, so inline cell rows can
  compute nearest-witness payload state inside native traversal and emit only
  offload rows to the downstream continuation. The full public res4 same-POD
  route still matched author HDResult; the same-rebuild no-inline control route
  median is ~0.03279s and the inline-nearest route median is ~0.02916s. The
  continuation candidate distance evaluations collapse from about 1.15M to
  7354, while route-time improvement remains modest because native frontier work
  increases. No paper-performance or author-parity ratio is authorized.
- Goal5173 is implemented but not yet externally reviewed. It adds an explicit
  `direction_mode` policy to the X-HD seeded route and matrix: the compatibility
  default `symmetric-diagnostic` still runs both A->B and B->A, while
  `directed-a-to-b` matches the author `HDResult` contract established by
  Goal5126 and avoids the extra diagnostic B->A direction. The full public res4
  POD route with Goal5172 inline-nearest still matched author HDResult; route
  median is ~0.01536s and total median is ~0.05673s. A sample256
  exact-and-author smoke also matched exact directed reference. No
  paper-performance or author-parity ratio is authorized.
- Goal5174 is implemented but not yet externally reviewed. It records a
  same-POD multiscale matrix for the current author-directed, native
  inline-nearest route across sample256, sample1024, sample2048, sample4096, and
  full public res4. All cases matched author HDResult, with route medians of
  ~0.00307s, ~0.00582s, ~0.00635s, ~0.01063s, and ~0.01492s respectively.
  `directed_b_to_a` is null in every case by design. This is Level B
  same-source representative profile evidence only; it is not exact paper
  dataset reproduction, a denominator-aligned author ratio, or full paper
  reproduction.
- Goal5175 is implemented but not yet externally reviewed. It extracts a
  structured author-log workload manifest from the pinned author repository.
  The artifact parses 281 current main-branch `expr/logs` JSON records, records
  335 unique author input paths, confirms zero input files are available in the
  author repo/current machine, and inventories 41755
  `origin/paper:expr/for_the_paper` JSON blobs as inventory-only. This deepens
  dataset provenance, but it does not supply input bytes/hashes and does not
  upgrade Level B representative evidence to exact paper dataset reproduction.
- Goal5176 is implemented but not yet externally reviewed. It parses the
  author `paper` branch `expr/for_the_paper/logs` tree through git object
  access, avoiding ordinary Windows checkout of long paths. The artifact parses
  41755 JSON blobs with zero parse errors, retains all 4535 `run_all` records,
  samples non-`run_all` training logs, and records 1946 unique author input
  paths. This turns the paper-branch log inventory into structured workload
  provenance, but still does not provide input bytes/hashes, exact paper
  dataset reproduction, figure reproduction, or a performance ratio.
- Goal5177 is implemented but not yet externally reviewed. It maps the Goal5130
  paper figure targets to the Goal5176 paper-branch `run_all` log index. The
  artifact identifies Figure 5 as having the strongest workload-family log
  coverage, Figures 6/7/9/10 as partially covered but blocked by missing phase
  counters, script semantics, or scale/overlap labels, and Figures 8/11 as not
  covered by `run_all` timing logs. It also defines priority input subsets such
  as Dragon-HappyBuddha, Dragon-AsianDragon, County-Zipcode, Lakes-Parks, and
  the first logged BraTS pair. This is figure-target provenance only; it does
  not provide input bytes/hashes, exact paper dataset reproduction, figure
  reproduction, or a performance ratio.
- Goal5178 is implemented but not yet externally reviewed. It bridges the
  `graphics_dragon_happy_buddha` priority subset from Goal5177 to locally
  acquired public Stanford full-resolution Dragon/HappyBuddha PLY candidates.
  The public candidate files exist and their vertex counts match the author
  paper-branch logs (`437645` and `543652`), with SHA256 hashes recorded for
  source archives and extracted PLY files. This is a strong Level B same-source
  candidate only; exact paper dataset identity is not proved because author
  input bytes/hashes or deterministic conversion provenance are absent.
- Goal5179 is implemented but not yet externally reviewed. It profiles the
  full public Stanford Dragon/HappyBuddha Level B candidate without running a
  route. The artifact records MBRs, grid occupancy for `8^3`, `16^3`, and
  `32^3` grids, and a naive pairwise estimate of `237926579540` point pairs.
  Even a minimal 16-byte candidate row would be about 3.8 TB, so the artifact
  explicitly disallows naive pairwise exact materialization and requires a
  scalable seeded/frontier/inline-nearest route before any full-candidate gate.
  This is planning/scale evidence only; no route run, figure reproduction,
  performance ratio, or exact paper dataset claim is made.
- Goal5180 is implemented but not yet externally reviewed. It loads the full
  public Stanford Dragon/HappyBuddha Level B candidate, selects 16 deterministic
  evenly-spaced Dragon source rows, runs the scalable RTDL route against the
  full 543652-point HappyBuddha target, and compares that result to a
  vectorized exact subset oracle. The artifact reports `matched=true` and
  `route_abs_diff=0.0`, with `58518` frontier rows and `12741` total candidate
  distance evaluations for the bounded subset. This is a bounded source-subset
  feasibility gate only: it is not an all-source route run, not native/POD
  fail-closed capacity validation, not figure reproduction, not exact paper
  dataset reproduction, and not a performance ratio.
- Goal5181 is implemented but not yet externally reviewed. It extends Goal5180
  into a bounded source-subset scaling matrix over the full public
  Dragon/HappyBuddha Level B candidate. Source limits `16`, `64`, and `128`
  all match exact subset oracles with `route_abs_diff=0.0`. The largest
  observed frontier row count is `526006`, and the artifact suggests `789009`
  as the next explicit row capacity for a future bounded POD/OptiX gate. This
  is still not an all-source route run, native/POD fail-closed capacity
  validation, figure reproduction, exact paper dataset reproduction, full
  paper reproduction, or a performance ratio.
- Goal5182 is implemented but not yet externally reviewed. It threads explicit
  fail-closed frontier row capacity through the X-HD full-public route runners
  and records a local NumPy readiness artifact using the Goal5181 capacity
  value `789009`. Source limits `16`, `64`, and `128` still match exact subset
  oracles with `route_abs_diff=0.0`; each case records
  `frontier_row_capacity_requested=789009`, `frontier_row_capacity=789009`,
  `frontier_row_capacity_policy=explicit`, and
  `frontier_row_capacity_attempts=[789009]`. Tests prove too-small explicit
  capacity fails closed with `fail_closed_overflow`. This is local capacity
  plumbing/readiness evidence only; it is not native/POD capacity validation,
  an all-source route run, exact paper dataset reproduction, full paper
  reproduction, or a performance ratio.
- Goal5183 is implemented but not yet externally reviewed. It runs the
  Goal5182 explicit-capacity gate on a CUDA/OptiX POD using backend `optix`,
  full public HappyBuddha target points, and Dragon source limits `16`, `64`,
  and `128`. All three cases match exact subset oracles with
  `route_abs_diff=0.0`; each case records capacity `789009`,
  `row_capacity_policy=explicit`, native symbol
  `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3`,
  `frontier_row_order=native_unsorted`, and `frontier_inline_nearest=true`.
  Max observed native frontier rows are `528` because inline-nearest consumes
  inline cell rows in native traversal. This is bounded POD/OptiX capacity
  validation only; it is not an all-source route run, exact paper dataset
  reproduction, full paper reproduction, or a performance ratio.
- Goal5184 is implemented but not yet externally reviewed. It extends the
  Goal5183 POD/OptiX bounded gate to source limits `256`, `512`, `1024`,
  `2048`, and `4096` against the full public HappyBuddha target. Every case
  matches the exact subset oracle with `route_abs_diff=0.0`, uses backend
  `optix`, native symbol `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3`,
  explicit capacity `789009`, `row_capacity_policy=explicit`,
  `frontier_row_order=native_unsorted`, and `frontier_inline_nearest=true`.
  Max observed native frontier rows are `19229` and total candidate distance
  evaluations at source_limit `4096` are `3203273`. This is larger bounded
  subset evidence only; it is not an all-source route run, exact paper dataset
  reproduction, full paper reproduction, or a performance ratio.
- Goal5185 is implemented but not yet externally reviewed. It extends the
  exact-oracle POD/OptiX bounded gate to source_limit `8192` against the full
  public HappyBuddha target. The case matches the exact subset oracle with
  `route_abs_diff=0.0`, uses backend `optix`, native symbol
  `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3`, explicit capacity
  `789009`, and observes `38249` native frontier rows. The exact subset oracle
  evaluates `4453597184` source-target pairs and takes about `62.34s`, while
  the RTDL route wall is about `1.43s`. This is the largest current
  exact-oracle-validated subset for the full public Level-B candidate, but it
  is still not an all-source route run, exact paper dataset reproduction, full
  paper reproduction, or a performance ratio.
- Goal5186 is implemented but not yet externally reviewed. It runs the author
  `hd_exec` binary on the full public Stanford Dragon/HappyBuddha Level-B
  candidate (`437645` x `543652` points) and compares the produced author
  `HDResult` with the paper-branch author-log value for
  `graphics_dragon_happy_buddha`. The raw author JSON reports
  `HDResult=0.12572988867759705`, `Running.AvgTime=7.823ms`, and point counts
  `[437645, 543652]`; the paper-log value is `0.12572969496250153`, giving
  `paper_log_min_abs_diff=1.9371509552001953e-07` at tolerance `1e-6`.
  This is strong Level-B same-source author evidence, but it is not RTDL
  all-source route completion, not exact paper dataset identity, not full paper
  reproduction, and not a performance ratio.
- Goal5187 is implemented but not yet externally reviewed. It runs the scalable
  RTDL route over all `437645` Dragon source points and all `543652`
  HappyBuddha target points for the same full public Level-B candidate, skips
  exact-oracle validation, and compares the route distance to Goal5186 author
  `HDResult`. The artifact reports `matched=true`, RTDL route distance
  `0.12572988629271128`, author distance `0.12572988867759705`, and
  `author_abs_diff=2.3848857610975216e-09` at tolerance `1e-6`. The route uses
  backend `optix`, native symbol
  `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3`, explicit frontier row
  capacity `4000000`, and observes `2052249` native frontier rows. This is the
  strongest current Level-B route evidence, but it is route-only author
  comparison: not exact-oracle validation, not exact paper dataset identity,
  not full paper reproduction, and not a performance ratio.
- Goal5188 is implemented but not yet externally reviewed. It builds the
  full-public Level-B phase-boundary matrix from the Goal5188 timed author run
  and Goal5187 RTDL all-source route. The matrix records author
  `Running.AvgTime=7.603ms`, author process wall `1.973201423883438s`, RTDL
  load `2.5199945867061615s`, RTDL route wall `7.303133897483349s`, and RTDL
  total `10.011082544922829s`. It explicitly reports no author-vs-RTDL ratio
  because author internal timing, author process wall, and RTDL route/total
  have different phase boundaries. It identifies the dominant RTDL route phases
  as `initial_state_seed ~= 4.04s` and `frontier_rows ~= 1.94s`.
- Goal5189 is implemented but not yet externally reviewed. It adds an
  app-neutral `seed_nearest_witness_from_local_grid_cell_numpy_columns` helper
  that produces a valid upper-bound seed from a nearby occupied grid cell
  instead of scanning every tight cell MBR. On the full public
  Dragon/HappyBuddha Level-B route, the same-POD nearest-MBR control matches
  author HDResult with route wall about `8.31s`, seed about `5.15s`, and
  `2052249` frontier rows. The local-grid seed route also matches author
  HDResult with abs diff about `2.38e-9`, lowers route wall to about `5.98s`,
  and reduces seed time to about `0.90s`, but increases frontier rows to
  `7590188` and continuation time to about `2.03s`. This is route-local system
  evidence only: no author performance ratio, no exact paper dataset identity,
  and no full paper reproduction claim.
- Goal5190 is implemented but not yet externally reviewed. It adds an
  app-neutral `seed_nearest_witness_from_grid_branch_bound_numpy_columns`
  helper that searches grid shells until lower bounds can no longer improve the
  current point witness. On the same full public Level-B route it matches the
  author HDResult, lowers frontier rows to `1811625`, and has route wall about
  `7.71s`. This is faster than the same-POD nearest-MBR control (`~8.31s`) but
  slower than Goal5189 local-grid seed (`~5.98s`) because seed search costs
  about `4.60s`. It is an optional measured strategy, not the current best route
  and not a performance-ratio claim.
- Goal5191 is implemented but not yet externally reviewed. It measures larger
  generic native inline-nearest thresholds on top of the Goal5189 local-grid
  seed and adds a fail-closed route-runner fast path for the case where the
  native inline nearest state is complete and `frontier_row_count=0`. On the
  same full public Level-B route, `max_inline_points=512` plus the
  empty-frontier passthrough matches author HDResult with abs diff about
  `2.38e-9`, reports route wall about `3.65s`, records `frontier_rows=0`, and
  reduces nearest-continuation overhead to about `0.016s`. This is route-local
  Level-B system evidence only: no author performance ratio, no exact paper
  dataset identity, and no full paper reproduction claim.
- Goal5192 is implemented but not yet externally reviewed. It adds optional
  telemetry counters to the generic native 3-D cell-MBR inline-nearest
  collector via `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v4`, while
  preserving prior v1/v2/v3 call behavior. On the same full public
  Dragon/HappyBuddha Level-B route, the no-telemetry control matches author
  HDResult with route wall about `3.70s`; the telemetry run also matches and
  reports `inline_cell_hit_count=12003138` and
  `inline_point_evaluation_count=1242677739`. This is diagnostic accounting
  evidence only; telemetry timing is not the best route time, and it is not an
  author performance ratio, exact paper dataset identity, or full paper
  reproduction claim.
- Goal5193 is implemented but not yet externally reviewed. It adds a generic
  bounded grid-cell seed helper,
  `seed_nearest_witness_from_grid_cell_budget_numpy_columns`, and tests it on
  the full public Dragon/HappyBuddha Level-B route along with intermediate
  inline thresholds. All measured variants match the Goal5186 author HDResult,
  but none improves the current best local-grid + inline512 route. The helper is
  generic route evidence and should be reviewed as either an acceptable public
  RTDL seed strategy or demoted if reviewers consider the no-go result
  insufficient for public-surface promotion. This is not an author performance
  ratio, exact paper dataset identity, or full paper reproduction claim.
- Goal5194 is implemented but not yet externally reviewed. It changes the
  generic native 3-D cell-MBR inline-nearest any-hit path so later cell
  classification uses the updated payload current best distance instead of only
  the initial query seed distance. The change preserves app-neutral naming,
  keeps equal-distance cells evaluable for lower-id tie-breaks, and exposes
  `inline_nearest_pruning=payload_current_best_min_cell_distance_gt_best` in
  metadata. On the full public Dragon/HappyBuddha Level-B route, two warmed
  no-telemetry reruns match the Goal5186 author HDResult and report route walls
  about `3.46s` and `3.45s`; telemetry reports inline cell hits reduced from
  about `12.00M` to `3.64M` and inline point evaluations from about `1.24B` to
  `0.40B`. This is route-local generic system evidence only: no author
  performance ratio, no exact paper dataset identity, and no full paper
  reproduction claim.
- Goal5195 is implemented but not yet externally reviewed. It moves the same
  payload-current-best prune earlier into the generic native 3-D cell-MBR
  intersection program for inline-nearest / no-pruned-row mode, so cells already
  excluded by the current nearest-state can return before
  `optixReportIntersection`. Equal-distance cells remain evaluable for
  lower-id tie-breaks, and metadata now carries
  `intersection_pruning=payload_current_best_before_report_intersection`.
  Full-public Dragon/HappyBuddha Level-B runs still match the Goal5186 author
  HDResult; warmed route-local evidence reports route wall about `2.6s` and
  native frontier / inline time about `0.93-0.94s`. This is generic route-local
  system evidence only: no author performance ratio, no exact paper dataset
  identity, and no full paper reproduction claim.
- Goal5196 is implemented but not yet externally reviewed. It changes the
  generic grid-cell seed lookup from repeated binary search over
  `original_cell_ids` to a dense encoded-cell position table when the grid
  volume is under a configurable cap, with binary-search fallback for oversized
  grids. The dense lookup now covers local-grid, grid-cell-budget, and
  grid-branch-bound seed helpers. Full-public Dragon/HappyBuddha Level-B runs
  still match the Goal5186 author HDResult; observed route-local evidence
  reports the dense local-grid route wall about `2.26s` and seed time about
  `0.55s`. Dense budget and branch-bound controls also match, but do not beat
  dense local-grid, so the default route remains dense local-grid. This is
  generic route-local system evidence only: no author performance ratio, no
  exact paper dataset identity, and no full paper reproduction claim.
- Goal5197 is implemented but not yet externally reviewed. It carries the
  cell-MBR `min_sq` computed in the native OptiX intersection program to
  any-hit via OptiX attributes, and computes row-only min/max distances lazily
  only when a row is emitted. Full-public Dragon/HappyBuddha Level-B runs still
  match the Goal5186 author HDResult; warm route evidence remains about
  `2.25-2.28s`, so this should be reviewed as a generic native cleanup /
  neutral optimization rather than a decisive speedup over Goal5196. This is
  generic route-local system evidence only: no author performance ratio, no
  exact paper dataset identity, and no full paper reproduction claim.
- Goal5198 is implemented but not yet externally reviewed. It is a grid-shape
  telemetry / no-go gate for the same generic full-public Level-B route. The
  current 32^3 route still matches the Goal5186 author HDResult and records
  route wall about `2.24s`, inline_cell_hit_count about `3.64M`, and
  inline_point_evaluation_count about `400.6M`. 24^3 fails the empty-frontier
  capacity-0 route with `155511` attempted frontier rows. 48^3, 64^3, and 128^3
  all match author HDResult and reduce point-evaluation counts, but route wall
  worsens to about `3.16s`, `6.76s`, and `10.72s` because seed probes and inline
  cell hits grow. This is route-local no-go/control evidence only: no author
  performance ratio, no exact paper dataset identity, and no full paper
  reproduction claim.
- Goal5199 is implemented but not yet externally reviewed. It is a
  trace-tmax-bound no-go gate for the same generic native OptiX cell-MBR route.
  The temporary implementation bounded ray `tmax` by radius or initial
  current-best distance plus epsilon. The full-public Level-B run still matched
  Goal5186 author HDResult, but inline_cell_hit_count and
  inline_point_evaluation_count were unchanged from Goal5198's 32^3 telemetry
  (`3.64M` and `400.6M`), and the warm route did not improve (`~2.32s`). The
  code change was reverted locally and on the POD, and the POD native library
  was rebuilt back to mainline. This is route-local no-go/control evidence only:
  no author performance ratio, no exact paper dataset identity, and no full
  paper reproduction claim.
- Goal5200 is implemented but not yet externally reviewed. It adds an explicit
  experimental generic native CUDA executor for local-grid nearest-state seed.
  POD build, focused tests, and a small actual native call passed, but the
  same-POD full-public comparison showed native CUDA is slower than the current
  auto/Numba seed (`2.436s` route / `0.958s` seed vs `2.258s` route / `0.563s`
  seed). The default route remains auto/Numba. This is route-local no-go/control
  evidence only: no author performance ratio, no exact paper dataset identity,
  no default-route improvement, and no full paper reproduction claim.
- Goal5201 is implemented but not yet externally reviewed. It adds
  diagnostic-only native phase timings for the generic 3-D cell-MBR
  nearest-frontier collector and threads the optional flag through the public
  partner/front-door route. The full-public Dragon/HappyBuddha Level-B route
  still matches the Goal5186 author HDResult. The warm diagnostic artifact
  reports route-level `frontier_rows` about `0.920s`, native frontier total
  about `0.600s`, native OptiX launch / inline nearest work about `0.377s`, and
  native `accel_build` only about `0.0004s`. Therefore prepared cell-MBR accel
  build is not the next meaningful target; the next generic system target is
  inline-nearest execution / work ordering or device-resident front-door state.
  This is diagnostic route-local evidence only: no performance improvement
  claim, no author performance ratio, no exact paper dataset identity, and no
  full paper reproduction claim.
- Goal5202 is implemented but not yet externally reviewed. It adds a generic
  `coordinate_matrix` / `coordinate_matrix_fields` point-column convention and
  makes the local-grid seed plus native 3-D cell-MBR frontier front doors reuse
  that packed matrix instead of rebuilding large coordinate matrices inside
  each helper. The full-public Dragon/HappyBuddha Level-B route still matches
  the Goal5186 author HDResult; metadata reports seed query/target and frontier
  query/target coordinate-matrix reuse as true. The no-timing route reports
  route wall about `2.027s`, compared with the Goal5200 same-POD auto/Numba
  control at about `2.258s`. This is generic route-local RTDL front-door
  improvement evidence only: no author performance ratio, no exact paper
  dataset identity, no author parity claim, and no full paper reproduction
  claim.
- Goal5203 is implemented but not yet externally reviewed. It keeps the legacy
  row-based X-HD input helpers for bounded/reference gates, but changes the hot
  full-public route to load ASCII PLY inputs directly into NumPy coordinate
  matrices and translate those matrices in place before entering the generic
  RTDL columnar route. The full-public Dragon/HappyBuddha Level-B route still
  matches the Goal5186 author HDResult; route wall is about `1.238-1.239s`,
  source+target column construction is about `0.001-0.002s`, and
  `load_full_inputs` is about `1.681s`. This is app-owned input-front-door
  cleanup plus adoption of the generic coordinate-matrix convention, not an
  X-HD-specific RTDL primitive, author performance ratio, exact paper dataset
  identity, author parity claim, or full paper reproduction claim.
- Goal5204 is implemented but not yet externally reviewed. It changes the
  generic `max_nearest_distance_witness_numpy_columns` reducer from full-array
  lexsort to finite max plus tie-only lexsort, with the old full-lexsort
  behavior retained for non-finite distances. The full-public
  Dragon/HappyBuddha Level-B route still matches the Goal5186 author HDResult;
  route wall is about `1.17-1.18s`, `max_nearest_reduction` is about
  `0.0007-0.0008s`, and artifacts self-report
  `max_reduction_strategy=finite_max_then_tie_lexsort`. This is generic
  reducer improvement evidence only: no author performance ratio, no exact
  paper dataset identity, no author parity claim, no X-HD-specific RTDL
  primitive, and no full paper reproduction claim.
- Goal5205 is implemented but not yet externally reviewed. It changes the
  app-owned ASCII PLY matrix loader from Python per-line split/float parsing to
  NumPy `loadtxt` with `max_rows=vertex_count` and `usecols` for coordinate
  columns. The full-public Dragon/HappyBuddha Level-B route still matches the
  Goal5186 author HDResult; `load_full_inputs` drops from about `1.69s` to
  about `0.68s`, total wall for the gate drops from about `3.08-3.09s` to
  about `2.06s`, and route wall remains about `1.16-1.17s`. This is app-owned
  input-front-door improvement evidence only: no author performance ratio, no
  exact paper dataset identity, no author parity claim, no X-HD-specific RTDL
  primitive, and no full paper reproduction claim.
- Goal5206 is implemented but not yet externally reviewed. It is a diagnostic
  / no-go goal rather than an optimization: it decomposes first-use versus
  same-process warm behavior for the current Goal5205 route. The one-shot
  all-source route remains about `1.16-1.17s`, but a near-identical second case
  in the same process reports about `0.61s`; this movement comes mainly from
  `initial_state_seed` dropping from about `0.23s` to `0.02-0.03s` and native
  frontier total dropping from about `0.60s` to `0.39s`. The OptiX launch /
  inline scan itself remains about `0.37-0.38s`. Warm numbers are diagnostic
  only and must not replace the fresh one-shot headline. The explicit seed
  executor control did not justify replacing the current default. No author
  performance ratio, exact paper dataset identity, author parity claim,
  X-HD-specific RTDL primitive, or full paper reproduction claim is authorized.
- Goal5207 is implemented but not yet externally reviewed. It adds an explicit
  app-owned route warmup protocol to the full-public scaling gate via
  `--route-warmup-source-limit`. The warmup case is recorded under top-level
  `route_warmup`, marked `case_role=warmup` and
  `excluded_from_summary_statistics=true`, while measured cases and summary
  statistics remain separate. The full-public Dragon/HappyBuddha artifact with
  warmup `all` and measured `all` still matches the Goal5186 author HDResult;
  warmup case total is about `1.389s`, measured warm route is about `0.626s`,
  and total including load + warmup + measured is about `2.893s`. This is
  regime-separated performance protocol evidence only. It is not a new route
  optimization and does not authorize a warm-only headline, author performance
  ratio, exact paper dataset identity, author parity claim, X-HD-specific RTDL
  primitive, or full paper reproduction claim.
- Goal5208 is implemented but not yet externally reviewed. It tests lower
  generic inline-nearest thresholds under the same Goal5207 explicit warmup
  protocol. Thresholds 384, 256, and 128 all still match the Goal5186 author
  HDResult, but they do not beat the current `max_inline_points=512` default in
  a meaningful way. 384 is only about 3ms faster in measured route wall and has
  worse full-run wall including warmup; 256 and 128 are slower because frontier
  rows and nearest continuation grow sharply. This is no-go evidence only. It
  does not authorize a new route default, warm-only headline, author
  performance ratio, exact paper dataset identity, author parity claim,
  X-HD-specific RTDL primitive, or full paper reproduction claim.
- Goal5209 is implemented but not yet externally reviewed. It adds an
  app-owned experimental `--cell-order` route switch for static generic cell
  primitive ordering before native cell-MBR traversal. `point-count-asc`
  preserves correctness but moves the repeated route median by only about
  1.4ms relative to native order and does not improve case-total median;
  `point-count-desc` is slower. The default remains `cell_order=native`. This
  is no-go / diagnostic evidence only and does not authorize a new route
  default, warm-only headline, author performance ratio, exact paper dataset
  identity, author parity claim, X-HD-specific RTDL primitive, or full paper
  reproduction claim.
- Goal5210 is implemented but not yet externally reviewed. It changes only the
  generic cell-MBR frontier OptiX raygen trace flag from
  `OPTIX_RAY_FLAG_NONE` to `OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT`, because this
  pipeline uses intersection and any-hit programs but no closest-hit program.
  The full-public Dragon/HappyBuddha Level-B route still matches the Goal5186
  author HDResult. Same-POD repeats show no material speedup: route median
  moves from about `0.6159s` to about `0.6116s`, while OptiX launch median does
  not improve (`0.3714s` to `0.3717s`). This is scoped semantic cleanup /
  neutral evidence only and does not authorize a route speedup claim, new route
  default, warm-only headline, author performance ratio, exact paper dataset
  identity, author parity claim, X-HD-specific RTDL primitive, or full paper
  reproduction claim.
- Goal5211 is implemented but not yet externally reviewed. It adds optional,
  app-neutral global-bound early break to the generic cell-MBR inline-nearest
  path through `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v5`. The
  full-public Dragon/HappyBuddha Level-B route still matches the Goal5186 author
  HDResult. Fresh no-warm evidence reports route wall about `0.849s` and full
  total about `1.752s`; explicit-warm measured repeats report route median about
  `0.362s`, case median about `0.541s`, OptiX launch median about `0.053s`, and
  about `409k` early-aborted sources. This is a max-nearest /
  directed-Hausdorff reduction contract: early-aborted per-source witnesses may
  be approximate. It is a route-local Level-B result only and does not authorize
  an author performance ratio, exact paper dataset identity, author parity
  claim, X-HD-specific RTDL primitive, full paper reproduction claim, or default
  enablement for generic nearest-witness APIs.
- Goal5212 is implemented but not yet externally reviewed. It removes
  unnecessary all-source source-subset materialization in the X-HD full-public
  runner: when `source_limit == source_count`, the runner reuses
  `points_a_full` directly and records `source_subset_materialized=false` /
  `source_subset_selection_contract=all_source_no_copy_view`. The Level-B
  Dragon/HappyBuddha route still matches the Goal5186 author HDResult. Fresh
  full total including load moves from Goal5211's about `1.752s` to about
  `1.531s`; this is app-runner/full-gate hygiene rather than native route
  speedup. It does not authorize an author performance ratio, exact paper
  dataset identity, X-HD-specific RTDL primitive, or full paper reproduction
  claim.
- Goal5213 is implemented but not yet externally reviewed. It retests heavier
  initial-state strategies under the Goal5211 global-bound early-break route on
  the public Dragon/HappyBuddha all-source Level-B gate. All tested routes
  still match the Goal5186 author HDResult, but `nearest-cell-mbr`,
  `grid-cell-budget`, and `grid-branch-bound` are dominated by seed
  construction time (`~4.79s`, `~6.67s`, and `~9.44s` seed respectively) and
  are far slower than the `local-grid-cell` baseline (`~0.219s` seed,
  `~0.852s` route). This is a no-go for heavier initial-state defaults. It
  does not weaken Goal5211, and it does not authorize an author performance
  ratio, exact paper dataset identity, X-HD-specific RTDL primitive, or full
  paper reproduction claim.
- The X-HD midterm status packet after Goal5213 is written and review pending:
  `history/internal_docs/xhd_midterm_status_after_goal5213_2026-07-09.md` and
  `history/internal_docs/call_for_review_xhd_midterm_status_after_goal5213_2026-07-09.md`.
- Goal5214 is implemented but not yet externally reviewed. It refreshes exact
  paper dataset availability against the current POD and the author
  paper-branch log index. The current POD lacks `/local`,
  `/local/storage/shared`, and `/local/storage/shared/HDDatasets`; the author
  log index contains 4535 run-all records and 9070 file references rooted under
  `/local/storage/shared/HDDatasets`, but those are paths and metadata, not
  available input files or hashes. Therefore Level-C exact paper dataset
  reproduction remains unsupported; the strongest current claim remains Level-B
  same-source representative reproduction.
- Goal5215 is implemented but not yet externally reviewed. It performs a public
  artifact availability sweep over the X-HD GitHub repository, author
  publication page, paper PDF, web searches, and git refs/trees. The public
  repository exposes source, scripts, and logs but no tracked `.ply/.off/.wkt/.nii`
  style input datasets; `main`, `paper`, and `hybrid` have zero tracked
  dataset-like assets, no tags, and no public release/package dataset bundle
  was found. Therefore public artifacts still do not provide exact paper input
  bytes, hashes, byte-identical converted point sets, or deterministic
  reconstruction provenance. Level-C exact paper dataset reproduction remains
  unsupported; Level-B same-source representative reproduction remains the
  strongest current claim.
- Goal5216 is implemented but not yet externally reviewed. It consolidates the
  Level-B same-source representative X-HD packet for public Stanford
  Dragon/HappyBuddha. The packet records Goal5186 author `hd_exec` HDResult
  `0.12572988867759705` matching the paper-branch log within `1e-6`, and the
  current RTDL route matching that author HDResult with fresh route wall
  `~0.852s`, full gate including input load `~1.531s`, and explicit-warm
  measured route `~0.288s` with warmup reported separately. It keeps exact
  paper dataset reproduction false, author-vs-RTDL performance ratio false,
  author parity false, and full paper reproduction false.
- Goal5217 is implemented but not yet externally reviewed. It records a same-POD
  phase-boundary performance matrix for public Stanford Dragon/HappyBuddha with
  five author repeats, five RTDL fresh repeats, and five RTDL explicit-warm
  repeats. All repeats match the expected author re-run HDResult on public
  data; the author re-run remains distinct from the paper-branch log value.
  Median values are: author internal `Running.AvgTime = 7.722 ms`, author
  process wall `~1.906s`, RTDL fresh route `~0.840s`, RTDL fresh full gate
  including input load `~1.520s`, and RTDL explicit-warm measured route
  `~0.290s` with warmup cost separately recorded. This is a denominator matrix
  only; author-vs-RTDL ratio, exact paper dataset reproduction, author parity,
  warm-only headline, and full paper reproduction remain unauthorized.
- X-HD midterm report after Goal5216 was externally reviewed with
  `approve_with_required_amendments`. The required amendments were applied in
  `history/internal_docs/xhd_midterm_after_goal5216_review_amendment_response_2026-07-09.md`:
  the report now states that the route is exact-value-only for the directed-HD
  scalar with approximate per-source witnesses for early-aborted sources; that
  RTDL matches the author re-run on public data rather than the paper-branch
  log; and that current Level-B evidence is one directed workload
  (Dragon -> HappyBuddha), not broad Level-B paper coverage. The amendment
  response was verified in
  `history/internal_docs/review_xhd_midterm_after_goal5216_amendments_verified_2026-07-09.md`
  with verdict
  `approve_xhd_midterm_level_b_single_workload_status_with_caveats`.
- Goal5218 is implemented but not yet externally reviewed. It probes the
  public official ModelNet40 raw OFF files for one small paper-branch pair
  (`glass_box_0115.off -> glass_box_0081.off`). The public raw OFF vertex
  counts match the author log counts `[1107, 1200]`, but author `hd_exec` on
  those raw OFF files reports `HDResult = 1115.2059326171875` while the
  paper-branch log reports `0.22594279050827026`. Therefore public raw
  ModelNet40 OFF is not currently a valid exact paper input; preprocessing /
  normalization / conversion provenance must be found before ModelNet40 can
  advance toward Level-C exact reproduction.
- Goal5219 is implemented but not yet externally reviewed. It identifies the
  missing ModelNet40 preprocessing contract for the same pair. Author
  `-normalize=true` subtracts each input's per-axis lower bound and divides by
  that input's largest axis extent. Running author `hd_exec` on the official
  public raw OFF files with `-normalize=true` exactly reproduces the
  paper-branch `HDResult = 0.22594279050827026` and logged normalized MBRs for
  `glass_box_0115.off -> glass_box_0081.off`. The X-HD paper app now has an
  app-owned OFF loader and author-compatible normalize transform; the RTDL
  generic route on the normalized OFF inputs matches the author normalized
  result within float-author tolerance (`abs diff ~= 5.29e-08`, tolerance
  `1e-6`) and matches its own exact reference exactly. This remains one-pair
  ModelNet40 evidence only and does not authorize all-pair ModelNet40
  reproduction, exact paper dataset identity, performance ratio, author parity,
  or full X-HD paper reproduction.
- Goal5220 is implemented but not yet externally reviewed. It extends the
  ModelNet40 normalized-public-OFF contract from one pair to a five-pair batch
  across five categories: glass_box, cone, bowl, door, and wardrobe. The batch
  selection deduplicates repeated paper-branch log entries by input paths and
  selects the smallest unique pairs while preferring distinct categories. For
  all five cases, author `hd_exec -normalize=true` on official public raw OFF
  exactly matches the paper-branch HDResult and logged MBRs, and the RTDL
  generic route on the app-owned normalized OFF input matches author within
  `1e-6` float-author tolerance. This supports a small-batch reconstruction
  candidate claim only; it does not authorize all ModelNet40 pairs, exact input
  byte identity, author-vs-RTDL performance ratio, or full X-HD paper
  reproduction.
- Goal5221 is implemented but not yet externally reviewed. It extends the
  ModelNet40 normalized-public-OFF batch to 20 unique pairs/categories and
  passes paper-log `NumPointsPerCell` to the author rerun. Nineteen of twenty
  cases pass: author normalized HDResult equals the paper-branch log,
  normalized MBRs match, and the RTDL normalized route matches author within
  `1e-6`. The one failing case is
  `range_hood_0124.off -> range_hood_0004.off`: paper log
  `0.46497631072998047`, current author XHD rerun `0.466653436422348`, and
  RTDL normalized route `0.46497629417671404`. The paper log reports
  `Algorithm=Hybrid` while the current rerun reports `Algorithm=XHD`; a quick
  current-binary `-variant clover` probe aborts with CUDA illegal memory access.
  This makes ModelNet40 a strong normalized-public-OFF reconstruction candidate
  with one known comparator/regime mismatch, not an all-pair reproduction.
- Goal5222 is implemented but not yet externally reviewed. It investigates the
  Goal5221 `range_hood_0124.off -> range_hood_0004.off` mismatch by building a
  separate `origin/paper` author worktree and running `variant=hybrid` with the
  paper-log parameters. The paper-branch Hybrid comparator reports
  `HDResult = 0.46497631072998047`, exactly matching the paper log, while the
  current main/rt comparator reports `Algorithm=XHD` and
  `HDResult = 0.466653436422348`. The RTDL normalized route from Goal5221
  reports `0.46497629417671404`, matching the paper log and paper-branch Hybrid
  within tolerance. This reclassifies the Goal5221 failure as a comparator
  regime mismatch and motivates algorithm-aware comparator selection for
  ModelNet40 logs. It does not authorize all ModelNet40 reproduction, exact
  dataset byte identity, performance ratio, or full X-HD paper reproduction.
- Goal5223 is implemented but not yet externally reviewed. It updates the
  app-owned ModelNet40 batch runner so author comparator selection follows the
  original paper-log algorithm payload read from the author log blob. On the
  same 20 selected ModelNet40 records, all paper logs report `Algorithm=Hybrid`,
  all 20 use the paper-branch `variant=hybrid` comparator, all 20 author
  reruns match their paper-log HDResult exactly, all 20 MBR checks pass, and all
  20 RTDL normalized routes match author within `1e-6` (max RTDL-author diff
  `1.1170203562116399e-07`). This supports a selected 20-record
  normalized-public-OFF Level-B batch, not all ModelNet40 reproduction, exact
  byte identity, performance ratio, or full X-HD paper reproduction.
- Goal5224 is implemented but not yet externally reviewed. It expands the
  algorithm-aware ModelNet40 gate to 40 selected records, one pair from each
  ModelNet40 category. All 40 paper-log records report `Algorithm=Hybrid`, all
  40 use the paper-branch `variant=hybrid` comparator, all 40 author reruns
  match their paper-log HDResult exactly, all 40 MBR checks pass, and all 40
  RTDL normalized routes match author within `1e-6` (max RTDL-author diff
  `2.8723411737985316e-07`). This is strong 40-category representative
  ModelNet40 evidence, not all 400 unique pairs, all 2000 log records, exact
  byte identity, performance ratio, or full X-HD paper reproduction.
- Goal5225 is implemented but not yet externally reviewed. It adds explicit
  ModelNet40 selection strategies to the app-owned batch runner and probes the
  heaviest unique pairs. Static analysis shows 400 unique ModelNet40 pairs
  across 40 categories, with total point counts ranging from 2,307 to
  2,726,286. The largest-1 probe matches the 2.7M-point
  `airplane_0396 -> airplane_0050` case with RTDL-author diff
  `1.0617538129253923e-07`; the largest-10 probe matches all 10 heaviest pairs,
  with total point counts 942,931..2,726,286, route-wall sum `124.0838s`, and
  full-total sum `164.0274s`. This supports all-400 feasibility, but all-400 is
  not yet complete and should be run with chunking/resume/failure capture.
- Goal5226 is implemented but not yet externally reviewed. It adds the
  operational controls required before the all-400 unique-pair run:
  chunked execution, global case indices, per-case JSON artifacts,
  skip-completed/resume behavior, per-case failure capture, and aggregation
  from case artifacts. Local validation ran 10 focused runner tests OK and 23
  related X-HD loader/normalization tests OK. POD validation on
  `213.173.108.24:13502` passed the same focused 10-test and 23-test suites
  after syncing the updated files into `/root/rtdl_goal5093`. This supports
  starting Goal5227 all-400 chunked execution, but it does not itself prove
  all-400 completion.
- Goal5227 is started but not yet complete and not yet externally reviewed.
  Chunk 0 of the all-400 unique-pair ModelNet40 run completed on POD:
  25 selected cases, 25 matched, 0 failed, max RTDL-author diff
  `1.0617538129253923e-07`, total point range 33,896..2,726,286, route-wall
  sum `134.63958233594894s`, chunk elapsed `200.131474070251s`. The aggregate
  rebuilt from per-case artifacts also reports 25/25. This validates the
  chunk/resume artifact path on real all-400 output, but it proves only 25/400,
  not all-400 completion.
- Goal5227 all-400 execution is now implemented but not externally reviewed.
  All 400 unique ModelNet40 pairs were run under the strict `1e-6` tolerance:
  398 matched, 2 failed, all_cases_matched=false. The two failures are
  near-threshold numeric differences (`1.4973206821644602e-06` and
  `1.0085423763905865e-06`) with author-vs-paper diff 0.0, MBR matched, and
  algorithm matched. Timing totals are recorded (`route_wall_sec` sum
  `433.2045598253608`, RTDL full total `629.2800005152822`, author process wall
  `257.22060713917017`) but no author-vs-RTDL ratio/parity is authorized.
- Goal5228 is implemented but not externally reviewed. It reran the two
  Goal5227 near-threshold failures with diagnostic tolerance `2e-6`; both pass.
  This supports a tolerance/semantic audit but does not retroactively turn
  Goal5227 into 400/400 under `1e-6`.
- Goal5229 is implemented but not externally reviewed. It identifies the better
  semantic fix: the author paper branch uses `RunHausdorffDistanceImpl<float, 3>`,
  so ModelNet40 normalization should use author float-coordinate semantics. The
  app-owned helper `normalize_point_matrix_to_author_float32_unit_box` and
  `--author-float32-normalization` route flag were added. A full all-400 rerun
  with the original `1e-6` tolerance reports 400/400 matched, max RTDL-author
  diff `6.59728109919655e-08`, route-wall sum `396.20282135903835s`, RTDL full
  total `593.3385793119669s`, and author process wall `256.336787045002s`.
  This supersedes tolerance loosening as the preferred resolution, but it still
  does not prove all-2000 records, exact input byte identity, fair performance
  ratio/parity, or full X-HD reproduction.
- Goal5230 is implemented but not externally reviewed. It proves all 2000
  ModelNet40 paper-log records are covered for HDResult value by the 400/400
  unique-pair RTDL result plus duplicate-record equivalence. The paper-log
  structure is 400 unique pairs, exactly five records per pair, with zero value
  signature mismatches and zero missing/unmatched unique cases. Algorithm
  distribution is Early Break 400, Hybrid 1200, Ray Tracing 400; every unique
  pair has Early Break + Hybrid + Ray Tracing records. This is value coverage,
  not 2000 individual reruns and not per-algorithm performance reproduction.
- Goal5231 is implemented but not externally reviewed. It builds a
  denominator-explicit performance matrix for the Goal5229 all-400 matched
  unique-pair run and links it to the Goal5230 all-2000 record coverage result.
  It reports author internal AvgTime, author process wall, RTDL route wall, and
  RTDL full app total as separate denominators. It records diagnostic ratios
  only and explicitly marks `ratios_are_authorized_performance_claims=false`.
  This is performance accounting, not author speedup/parity, not
  algorithm-specific performance reproduction, and not full X-HD paper
  reproduction.
- Goal5232 is implemented but not externally reviewed. It extends the
  Stanford graphics same-source input bridge to
  `graphics_dragon_asian_dragon`. The public AsianDragon archive
  `xyzrgb_dragon.ply.gz` was acquired, its extracted binary-big-endian PLY has
  3,609,600 vertices and matches the author paper-branch log point count, and
  the bridge reports five author run_all records with HDResult
  `0.06536811590194702`. This is Level-B input provenance only: no author/RTDL
  Dragon->AsianDragon HDResult gate, no Figure 6 reproduction, no exact paper
  dataset identity, and no performance ratio are claimed.
- Goal5233 is implemented but not externally reviewed. It generalizes the
  full-public route bridge to use author basename order instead of hard-coded
  Dragon->HappyBuddha paths, adds app-owned binary PLY vertex-matrix loading
  for Stanford `binary_big_endian` inputs, and runs a 16-source
  Dragon->AsianDragon subset route against the full 3,609,600-point target.
  The bounded route matches the exact subset oracle with `route_abs_diff=0.0`
  over 57,753,600 exact pair evaluations, but the local route is slower than
  the exact oracle (`13.799s` route vs `2.105s` exact). This is Level-B bounded
  subset correctness only: no all-source HDResult, no Figure 6, no exact paper
  dataset identity, no author performance ratio, and no full X-HD reproduction
  are claimed.
- Goal5234 is implemented but not externally reviewed. It identifies the
  Dragon->AsianDragon public-data coordinate scale contract: raw public
  AsianDragon gives author `HDResult=52.453487396240234` and does not match the
  paper log, while an app-owned deterministic `scale=0.001` candidate gives
  author `HDResult=0.06536787003278732`, within `2.46e-7` of the paper-log
  value `0.06536811590194702`. The scaled MBR extents match the paper-log MBR
  extents. RTDL also matches an exact 16-source subset oracle under the same
  scaled contract with `route_abs_diff=0.0`, but RTDL remains slower than the
  exact subset oracle. This is still Level-B same-source evidence: no exact
  paper byte identity, no Figure 6 reproduction, no RTDL all-source result, no
  author performance ratio, and no full X-HD reproduction are claimed.
- Goal5235 is implemented but not externally reviewed. It extends the scaled
  Dragon->AsianDragon RTDL bounded route to source limits 16, 64, and 256
  against the full 3,609,600-point scaled AsianDragon target. All three cases
  match exact subset oracles with `route_abs_diff=0.0`. The 64-source and
  256-source routes are faster than the local exact subset oracle, but this is
  not an author-vs-RTDL performance claim. The bounded matrix extrapolates to
  roughly 302M frontier rows for all-source if materialized naively, making
  capacity/streaming or a current-POD explicit-capacity gate the next blocker.
  No all-source HDResult, Figure 6, exact paper identity, author parity, or full
  reproduction is claimed.
- Goal5236 is implemented but not externally reviewed. It uploads the current
  source subset to the POD, rebuilds `librtdl_optix.so` there
  (`sha256=e29f6b523530fa8a5e382f3bb2d64fc93f2f14868a9bf1b9005fde8c649ab1bb`),
  and runs scaled Dragon->AsianDragon bounded OptiX gates for source limits 256
  and 1024 against the full 3,609,600-point scaled target. Both cases match
  exact subset oracles with `route_abs_diff=0.0` and final max witness equality.
  The 1024-source distance is `0.06520984417895137`, close to the paper-log
  all-source value, but it remains a bounded subset value. `per_source_witness_exact=false`
  remains a required caveat. No all-source HDResult, Figure 6, exact paper
  identity, author-vs-RTDL performance ratio, or full X-HD reproduction is
  claimed.
- Goal5237 is implemented but not externally reviewed. It runs the full
  Dragon->scaled AsianDragon source set on the POD with the current-source
  rebuilt OptiX library and matches the Goal5234 author scaled-public HDResult:
  RTDL route distance `0.06536787240753439`, author scaled HDResult
  `0.06536787003278732`, `author_abs_diff=2.3747470656587666e-09`, over
  437,645 source points and 3,609,600 target points. The passing mode uses
  `translate_each_input_to_min_bound` and disables `global_bound_early_break`;
  two diagnostic no-go runs show that no-translate and translate+global-bound
  early-break do not match. This is all-source route-only Level-B same-source
  evidence for one graphics pair, not exact paper input identity, Figure 6
  reproduction, author-vs-RTDL performance parity, or full X-HD reproduction.
- Goal5238 is implemented but not externally reviewed. It audits the author
  X-HD source and confirms that PLY inputs are loaded through `LoadPLY`, which
  independently subtracts each input's per-axis `vmin`
  (`v[i] = (v[i] - vmin[i])`). This explains why the passing Goal5237 route
  requires `translate_each_input_to_min_bound`: it mirrors the author PLY
  loader's app-owned preprocessing contract. A local regression test verifies
  the RTDL app helper's per-axis min-bound subtraction and documents that this
  is not a generic RTDL coordinate transform. No exact paper byte identity,
  Figure 6, performance parity, or full X-HD reproduction is claimed.
- Goal5239 is implemented but not externally reviewed. It builds a same-POD,
  same-input performance matrix for Dragon->scaled AsianDragon after the
  all-source RTDL route match. Correctness remains matched
  (`author_abs_diff=2.3747470656587666e-09`). Author process wall is
  `2.6587867364287376s`, author internal `Running.AvgTime` is
  `83.49680000000001ms`, RTDL full app wall is `31.252301812171936s`, and RTDL
  route direction time is `30.49027620255947s`. Diagnostic labelled ratios show
  RTDL is about `11.75x` slower than author process wall and about `365x`
  slower than author internal AvgTime under that denominator. The dominant RTDL
  phase is `nearest_continuation=28.124958105385303s`. These are
  denominator-explicit diagnostics, not Figure 6 reproduction, not author
  parity, and not full X-HD reproduction.
- Goal5240 is implemented but not externally reviewed. It tests the existing
  generic frontier nearest-continuation executors on the same Dragon->scaled
  AsianDragon all-source exact route. A same-POD `numba` baseline rerun remains
  matched but takes `direction_total=31.01092080026865s` with
  `nearest_continuation=28.445445612072945s`. The existing generic
  `numba_parallel` path remains matched and reduces those phases to
  `10.097781844437122s` and `7.6326252073049545s`; the `auto` route resolves to
  `numba_parallel` and records `direction_total=9.171282961964607s` with
  `nearest_continuation=6.6945535987615585s`. Candidate distance evaluations
  remain `6,417,800,660`, so this is an executor parallelization win, not an
  algorithmic pruning win and not author performance parity.
- Goal5241 is implemented but not externally reviewed. It tests generic
  grid-shape and native CUDA local-grid seed choices on the same
  Dragon->scaled AsianDragon exact route. Stronger seed strategies
  (`nearest-cell-mbr`, `grid-cell-budget`, `grid-branch-bound`) are diagnostic
  no-go routes for this workload because seed cost dominates. Finer generic
  grids reduce candidate work substantially. The best current all-source route
  is `grid_shape=96,60,72`, `local_grid_seed_executor=native_cuda`, and
  `frontier_nearest_executor=auto`; three same-POD repeats all match the author
  HDResult with `author_abs_diff=2.3747470656587666e-09`. Median
  `direction_total=3.0695155784487724s`, median route wall
  `3.322203427553177s`, and median total wall `3.8200959116220474s`.
  Candidate distance evaluations drop from Goal5240's `6,417,800,660` to
  `145,373,825`, and route direction improves about `9.93x` versus Goal5239.
  This is near author process-wall scale under a labelled denominator, but it
  is still far from author internal `Running.AvgTime`, not Figure reproduction,
  not exact paper input identity, and not full X-HD reproduction.
- Goal5242 is implemented but not externally reviewed. It decomposes the
  Goal5241 best Dragon->scaled AsianDragon route and tests the generic native
  frontier inline-nearest threshold. It corrects work accounting: Goal5241's
  `44x` figure is metadata/offload candidate-count reduction only; when native
  inline point evaluations are included, true point-evaluation reduction from
  the 32-grid route to the 96x60x72/max_inline=1024 route is about `5.16x`.
  The best current route is `grid_shape=96,60,72`,
  `local_grid_seed_executor=native_cuda`, `frontier_nearest_executor=auto`,
  and `max_inline_points=1024`; three same-POD repeats all match the author
  HDResult with `author_abs_diff=2.3747470656587666e-09`. Median
  `direction_total=2.8061167374253273s`, median route wall
  `3.059376485645771s`, and median total wall `3.5552977472543716s`.
  Continuation rows are eliminated (`frontier_rows=0`,
  `nearest_continuation~=0.00084s`). Labelled comparison: direction time is
  about `1.055x` slower than author process wall and about `33.6x` slower than
  author internal `Running.AvgTime`. This is still one same-source workload,
  not Figure reproduction, not exact paper input identity, not author internal
  parity, and not full X-HD reproduction.

## Next Required Evidence

Goal5111 produced a tiny same-input author JSON gate packet; Goal5112 executed
it against author `hd_exec` on POD. Goal5113 extended the same gate to a 10x9
bounded WKT fixture. Goal5114 extended it to a 9x8 bounded 3D WKT fixture:

```text
author_binary=hd_exec
variant=rt
input_type=wkt
HDResult=1.0
rtdl_exact_hausdorff=1.0
tolerance=1e-9
matched=true

bounded2d_HDResult=2.0
bounded2d_rtdl_exact_hausdorff=2.0
bounded2d_tolerance=1e-6
bounded2d_matched=true

bounded3d_HDResult=2.0
bounded3d_rtdl_exact_hausdorff=2.0
bounded3d_tolerance=1e-6
bounded3d_matched=true

bounded2d_rtdl_route=public_2d_columnar_hausdorff
bounded2d_rtdl_route_hausdorff=2.0
bounded2d_author_HDResult=2.0
bounded2d_rtdl_route_matched=true

bounded3d_rtdl_route=public_3d_columnar_hausdorff
bounded3d_rtdl_route_hausdorff=2.0
bounded3d_author_HDResult=2.0
bounded3d_rtdl_route_matched=true

directed2d_asymmetric_author_HDResult=0.5
directed2d_asymmetric_directed_a_to_b=0.5
directed2d_asymmetric_directed_b_to_a=9.0
directed2d_asymmetric_symmetric_diagnostic=9.0
directed2d_asymmetric_matched=true
```

## Goal5243 Review Status

- Goal5243 is implemented but not externally reviewed. It instruments and
  optimizes the generic native CUDA local-grid seed path by replacing the
  runtime-compiled seed kernel with a precompiled CUDA helper in
  `librtdl_optix.so`. The POD build now auto-detects the GPU architecture and
  builds with `-arch=sm_89` on the current RTX 4000 Ada POD, avoiding a CUDA
  12.8 / driver 550 runtime PTX JIT incompatibility.
- On the same Dragon -> scaled AsianDragon workload, correctness remains
  matched:

```text
author_abs_diff = 2.3747470656587666e-09
per_source_witness_exact = true
frontier_rows = 0
```

- The seed module phase moves from `0.496675326s` to `0.0s`; median
  precompiled route over three same-POD repeats is:

```text
direction_total = 2.3074675127863884s
route_wall = 2.3075230717658997s
total_wall = 3.056991830468178s
```

- Current labelled comparison:

```text
RTDL route_wall / author process wall = 0.868x
RTDL total_wall / author process wall = 1.150x
RTDL direction_total / author internal Running.AvgTime = 27.64x slower
```

- Claim boundary:

```text
single-workload Level-B checkpoint only
not full paper reproduction
not exact paper byte identity
not paper-log exact match
not Figure reproduction
not author internal parity
not multi-workload Level-B completion
```

## Goal5244 Review Status

- Goal5244 is implemented but not externally reviewed. It performs a POD
  grid-shape sweep after the Goal5243 precompiled seed fix and adds a generic
  optional grid-cell point ordering mode.
- The grid-shape sweep shows that `96x60x72` remains best among the tested
  shapes. Finer grids reduce inline point evaluations but increase frontier
  OptiX launch time.
- All tested shapes remain matched against the author value:

```text
author_abs_diff = 2.3747470656587666e-09
per_source_witness_exact = true
frontier_rows = 0
```

- The new optional order is:

```text
cell_point_order = input-stable
contract = cell_id_then_input_order
```

- Same-POD comparison at `96x60x72`:

```text
input-stable direction_total = 2.3042124956846237s
point-id     direction_total = 2.3126574978232384s
```

- Claim boundary:

```text
single-workload Level-B checkpoint only
input-stable is a small generic option, not a major speedup
grid-shape tuning is no-go for this workload, not a universal grid-shape proof
not full paper reproduction
not exact paper byte identity
not Figure reproduction
not author internal AvgTime parity
not multi-workload Level-B completion
```

- Review packet:

```text
history/internal_docs/goal5244_xhd_frontier_grid_shape_and_grid_point_order_result_2026-07-09.md
history/internal_docs/call_for_review_goal5244_xhd_frontier_grid_shape_and_grid_point_order_2026-07-09.md
```

## Goal5245 Review Status

- Goal5245 is implemented but not externally reviewed. It adds a generic native
  CUDA executor for `grid-branch-bound` nearest-witness seeding and an explicit
  `--skip-frontier-if-exact-seed` route shortcut.
- The implementation is app-neutral: grid branch-bound nearest witness, not
  X-HD/Hausdorff/paper-specific core logic.
- POD result summary:

```text
Numba grid-branch-bound route      = 31.3390s
native CUDA + frontier             = 3.6386s
native CUDA + exact-seed skip       = 2.4508s
native CUDA + skip + input-stable   = 2.4748s
```

- All variants matched the author rerun:

```text
author_abs_diff = 2.3747470656587666e-09
matched = true
```

- Performance decision:

```text
current best Goal5244 route ~= 2.3042s
native exact seed + skip    ~= 2.4508s
```

- Therefore Goal5245 is a capability success but a performance no-go for the
  current X-HD Level-B workload. It should remain behind explicit flags and not
  become the default route.
- Review packet:

```text
history/internal_docs/goal5245_native_grid_branch_bound_seed_result_2026-07-09.md
history/internal_docs/call_for_review_goal5245_native_grid_branch_bound_seed_2026-07-09.md
```

## Goal5246 Review Status

- Goal5246 is implemented but not externally reviewed. It adds a generic native
  CUDA/Thrust 3-D grid-cell MBR builder and route selector:

```text
rtdl_cuda_point_grid_cell_mbrs_3d
point_grid_cell_mbrs_native_3d_cuda_columns(...)
--grid-cell-builder native_cuda
```

- The builder preserves the generic point-grid cell-column contract and avoids
  X-HD/Hausdorff/paper-specific native semantics.
- Same-POD Dragon -> scaled AsianDragon evidence, three repeats:

```text
numpy grid builder median direction_total       = 2.320133849978447s
native_cuda grid builder median direction_total = 2.0793236047029495s
```

- Correctness remained matched in all six POD runs:

```text
author_abs_diff = 2.3747470656587666e-09
matched = true
```

- Goal5246 is now the best measured route for the single Dragon -> scaled
  AsianDragon Level-B public workload. It does not close full X-HD paper
  reproduction, exact paper byte identity, Figure reproduction, or author
  internal `Running.AvgTime` parity.
- Review packet:

```text
history/internal_docs/goal5246_native_grid_cell_mbr_builder_result_2026-07-09.md
history/internal_docs/call_for_review_goal5246_native_grid_cell_mbr_builder_2026-07-09.md
```

## Goal5247 Review Status

- Goal5247 is implemented but not externally reviewed. It combines the
  Goal5246 native grid builder with the generic max-nearest global-bound early
  break.
- It is the current best scalar `HDResult` route for Dragon -> scaled
  AsianDragon:

```text
median direction_total = 0.9754644557833672s
median total_sec = 1.7241097316145897s
```

- Correctness:

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
```

- Required caveat:

```text
per_source_witness_exact = false
early_break_count median = 428,711 / 437,645 sources
```

- Goal5247 may be described as scalar exact for the author `HDResult`, but not
  as exact per-source witness output.
- Denominator separation:

```text
RTDL route / author process wall = 0.367x
RTDL total / author process wall = 0.648x
RTDL route / author internal Running.AvgTime = 11.82x slower
```

- Review packet:

```text
history/internal_docs/goal5247_scalar_global_bound_native_grid_route_result_2026-07-09.md
history/internal_docs/call_for_review_goal5247_scalar_global_bound_native_grid_route_2026-07-09.md
```

## Goal5248 Review Status

- Goal5248 is implemented but not externally reviewed.
- It runs the Goal5247 scalar `HDResult` route on a second selected large
  Level-B public workload:

```text
ModelNet40 airplane_0036.off -> airplane_0515.off
```

- Three same-POD repeats matched the prior author JSON:

```text
author_hd_result = 0.09761668741703033
rtdl distance    = 0.09761668669590366
author_abs_diff  = 7.211266722650933e-10
matched          = true for all 3 repeats
```

- Median timings:

```text
route_sec = 0.6935913562774658
total_sec = 2.4796682223677635
```

- Required caveat:

```text
validation_mode = author-only
per_source_witness_exact = false
```

- This strengthens the scalar route from one selected public workload family to
  two selected public workload families, but does not prove all ModelNet40
  scalar-route coverage, exact per-source witnesses, exact paper byte-input
  identity, Figure reproduction, or author internal `Running.AvgTime` parity.
- Review packet:

```text
history/internal_docs/goal5248_modelnet40_second_level_b_scalar_route_result_2026-07-09.md
history/internal_docs/call_for_review_goal5248_modelnet40_second_level_b_scalar_route_2026-07-09.md
```

## Goals5249-5250 Review Status

- Goals5249-5250 are implemented but not externally reviewed.
- Goal5249 updates the ModelNet40 batch harness to expose current scalar route
  switches:

```text
--grid-cell-builder native_cuda
--global-bound-early-break
```

- Goal5249 POD result:

```text
selected_count = 10
matched_case_count = 10
failed_case_count = 0
max author_abs_diff = 3.139302651167242e-08
route_sec median = 0.092891626060009
```

- Goal5250 POD result on the largest selected ModelNet40 unique pair:

```text
airplane_0396.off -> airplane_0050.off
total points = 2,726,286
matched = true
author_abs_diff = 1.6001468206017222e-09
route_wall_sec = 1.0025392025709152
total_sec = 7.558594815433025
```

- Required caveats:

```text
validation_mode = author-only
per_source_witness_exact = false
```

- These goals strengthen selected ModelNet40 scalar route evidence but do not
  prove all ModelNet40 scalar coverage, exact per-source witnesses, exact paper
  byte-input identity, Figure reproduction, or author internal
  `Running.AvgTime` parity.
- Review packet:

```text
history/internal_docs/goal5249_modelnet40_scalar_batch10_route_result_2026-07-09.md
history/internal_docs/goal5250_modelnet40_largest_pair_scalar_route_result_2026-07-09.md
history/internal_docs/call_for_review_goals5249_5250_modelnet40_scalar_batch_and_largest_pair_2026-07-09.md
```

## Goal5251 Review Status

- Goal5251 is implemented but not externally reviewed.
- It found a correctness bug in the generic native OptiX global-bound
  early-break route:

```text
pre-fix batch40 = 39 / 40 matched
failed case = chair_0162.off -> chair_0131.off
pre-fix abs diff = 0.0009493921217607892
```

- Root cause:

```text
global-bound publication did not distinguish exact completed queries from
queries that had emitted deferred frontier rows
```

- Native fix:

```text
src/native/optix/rtdl_optix_workloads.cpp
optixSetPayload_6(2u) when kind == 2 deferred frontier rows are emitted
```

- Fixed POD evidence:

```text
chair + global-bound matched, abs diff = 2.8536356611041924e-10
ModelNet40 batch40 fixed = 40 / 40 matched
largest selected ModelNet40 pair fixed = matched
```

- Required caveat:

```text
per_source_witness_exact = false
```

- Review packet:

```text
history/internal_docs/goal5251_global_bound_publish_safety_and_modelnet40_batch40_result_2026-07-09.md
history/internal_docs/call_for_review_goal5251_global_bound_publish_safety_and_batch40_2026-07-09.md
```

## Goal5252 - ModelNet40 All-400 Scalar Route

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5252_modelnet40_all400_scalar_route_result_2026-07-09.md
history/internal_docs/call_for_review_goal5252_modelnet40_all400_scalar_route_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5252_modelnet40_all400_scalar_route_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5252_modelnet40_all400_scalar_route_full_artifacts_2026-07-09.tar.gz
```

Summary:

```text
400 / 400 unique ModelNet40 pair identities matched author reruns.
max author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = false
```

Carry-forward review questions:

```text
1. Does all-400 unique-pair coverage plus Goal5230 duplicate mapping justify a
   bounded scalar-HDResult ModelNet40 paper-log coverage statement?
2. Is the missing-nearest fallback generic and acceptable as a correctness
   safety net?
3. Does the tent fallback outlier require immediate algorithmic follow-up before
   any performance summary?
4. Are denominator-separated performance numbers fair and sufficiently
   non-misleading?
```

## Goal5254 - ModelNet40 Route-Label Performance Matrix

Status:

```text
implemented_review_pending
```

## Goals5251-5254 Consolidated Review Packet

Status:

```text
call_for_review_ready
```

Review entrypoint:

```text
history/internal_docs/call_for_review_goals5251_5254_xhd_modelnet40_current_route_consolidated_2026-07-09.md
```

Purpose:

```text
One strict review packet for the current ModelNet40 route evidence:
global-bound safety fix, all-400 scalar route, all-400 exact-witness route, and
route-label performance matrix.
```

Evidence:

```text
history/internal_docs/goal5254_modelnet40_route_label_performance_matrix_2026-07-09.md
history/internal_docs/call_for_review_goal5254_modelnet40_route_label_performance_matrix_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5254_modelnet40_route_label_performance_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/summarize_modelnet40_route_matrix.py
```

Summary:

```text
Goal5252 fast scalar route and Goal5253 exact-witness route now have a shared
same-case performance matrix with explicit author process and author AvgTime
denominators.
```

Carry-forward review questions:

```text
1. Are the two route labels separated strongly enough?
2. Is the performance interpretation denominator-safe?
3. Should route labels be mandatory in the final X-HD reproduction report?
```

## Goal5253 - ModelNet40 All-400 Exact-Seed Witness Route

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5253_modelnet40_all400_exact_seed_witness_route_result_2026-07-09.md
history/internal_docs/call_for_review_goal5253_modelnet40_all400_exact_seed_witness_route_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_artifacts_2026-07-09.tar.gz
```

Summary:

```text
400 / 400 unique ModelNet40 pair identities matched author reruns.
per_source_witness_exact = true for 400 / 400.
missing_nearest_fallback_count = 0 for 400 / 400.
```

Carry-forward review questions:

```text
1. Is Goal5253 now the correct functional-completeness anchor for ModelNet40?
2. Is Goal5252 still the correct scalar-performance anchor?
3. Are the two route labels sufficiently separated to avoid misleading
   performance or correctness claims?
```

## Goal5255 - RTDL hd_exec-Compatible Entrypoint

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_result_2026-07-09.md
history/internal_docs/call_for_review_goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
```

Summary:

```text
Adds an app-owned RTDL entrypoint that accepts the author's key hd_exec flags
and writes author-shaped HDResult / Running JSON while preserving explicit
RTDL route labels and claim boundaries.
```

Carry-forward review questions:

```text
1. Is HDResult correctly directed input1 -> input2 rather than symmetric max?
2. Are route labels strong enough to prevent performance/correctness mixing?
3. Does Running.AvgTime need even stronger wording as RTDL route wall time, not
   author internal phase time?
```

## Goal5256 - RTDL hd_exec GPU Route POD Smoke

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke_result_2026-07-09.md
history/internal_docs/call_for_review_goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_fast_scalar_pod.json
tests/goal5256_xhd_rtdl_hd_exec_pod_artifact_test.py
```

Summary:

```text
The Goal5255 hd_exec-compatible runner executed both bounded 3-D GPU route
labels on a live RTX 4000 Ada POD and wrote author-shaped HDResult / Running
JSON with RTDL route metadata.
```

Carry-forward review questions:

```text
1. Does this prove the user-facing entrypoint can reach GPU routes?
2. Is tiny-fixture per_source_witness_exact=true for fast-scalar sufficiently
   caveated?
3. Is Running.AvgTime too easy to confuse with author internal AvgTime?
```

## Goal5257 - RTDL hd_exec ModelNet40 Pair Bridge

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5257_xhd_rtdl_hd_exec_modelnet40_pair_result_2026-07-09.md
history/internal_docs/call_for_review_goal5257_xhd_rtdl_hd_exec_modelnet40_pair_2026-07-09.md
history/internal_docs/call_for_review_goals5255_5257_xhd_hd_exec_entrypoint_to_modelnet40_consolidated_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_exact_witness_hd_exec_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_fast_scalar_hd_exec_pod.json
tests/goal5257_xhd_rtdl_hd_exec_modelnet40_pod_artifact_test.py
```

Summary:

```text
The hd_exec-compatible RTDL entrypoint ran a real public ModelNet40 OFF pair
through both GPU route labels and matched the author rerun HDResult within
1e-6 tolerance.
```

Carry-forward review questions:

```text
1. Does this properly remain a one-pair entrypoint bridge, not all-400 proof?
2. Is Running.AvgTime labeling safe enough?
3. Should future bulk ModelNet40 reruns go through the hd_exec-compatible
   wrapper or keep using the batch harness with this bridge as user-facing proof?
```

## Goal5258 - hd_exec Running Time Semantics Hardening

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5258_xhd_hd_exec_running_time_semantics_hardening_result_2026-07-09.md
history/internal_docs/call_for_review_goal5258_xhd_hd_exec_running_time_semantics_hardening_2026-07-09.md
history/internal_docs/call_for_review_goals5255_5258_xhd_hd_exec_entrypoint_consolidated_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

Summary:

```text
Adds explicit TimeSemantics metadata to author-shaped Running.AvgTime fields so
they are not misread as author internal AvgTime parity.
```

Carry-forward review questions:

```text
1. Is TimeSemantics strong enough?
2. Should the JSON use a different top-level timing field in addition to
   author-shaped Running.AvgTime?
```

## Goal5259 - hd_exec Summary Batch Bridge

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5259_xhd_hd_exec_summary_batch_bridge_result_2026-07-09.md
history/internal_docs/call_for_review_goal5259_xhd_hd_exec_summary_batch_bridge_2026-07-09.md
history/internal_docs/call_for_review_goals5255_5259_xhd_hd_exec_user_entrypoint_batch_consolidated_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5259_modelnet40_first3_hd_exec_batch_exact_witness_pod.json
tests/goal5259_xhd_rtdl_hd_exec_summary_batch_test.py
tests/goal5259_xhd_rtdl_hd_exec_modelnet40_batch_pod_artifact_test.py
```

Summary:

```text
Adds an app-owned summary-driven batch bridge over the hd_exec-compatible
entrypoint. POD first-3 ModelNet40 exact-witness route matched 3 / 3 cases.
```

Carry-forward review questions:

```text
1. Is first-3 enough only as a bridge proof?
2. Should all-400 eventually rerun through this wrapper for UX consistency?
3. Does the bridge clearly leave Goals5252-5254 as all-400 evidence?
```

## Goal5260 - hd_exec-Compatible All-400 ModelNet40 Batch

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5260_xhd_hd_exec_all400_modelnet40_batch_result_2026-07-09.md
history/internal_docs/call_for_review_goal5260_xhd_hd_exec_all400_modelnet40_batch_2026-07-09.md
history/internal_docs/call_for_review_goals5255_5260_xhd_hd_exec_user_entrypoint_all400_consolidated_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
tests/goal5260_xhd_hd_exec_all400_batch_artifact_test.py
```

Summary:

```text
All 400 unique public ModelNet40 pair identities represented in the paper-branch
log index were run through the hd_exec-compatible batch bridge under the
cell-mbr-exact-witness route label. 400 / 400 matched author rerun HDResult.
```

Carry-forward review questions:

```text
1. Does this supersede first-3 as the user-entrypoint batch evidence?
2. Does this become the ModelNet40 functional anchor?
3. Are exact paper byte-input identity and Figure reproduction still clearly
   excluded?
```

## Goal5261 - hd_exec Entrypoint All-400 Performance Matrix

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5261_xhd_hd_exec_entrypoint_performance_matrix_result_2026-07-09.md
history/internal_docs/call_for_review_goal5261_xhd_hd_exec_entrypoint_performance_matrix_2026-07-09.md
history/internal_docs/call_for_review_goals5255_5261_xhd_hd_exec_user_entrypoint_all400_and_performance_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_hd_exec_entrypoint_performance_matrix.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
tests/goal5261_xhd_hd_exec_entrypoint_performance_matrix_test.py
```

Summary:

```text
Builds a denominator-separated all-400 performance matrix for the
hd_exec-compatible entrypoint. RTDL route-wall sum is 420.31s; author process
wall sum is 255.04s; author internal Running.AvgTime sum is 2794.79ms. Ratios
must be denominator-labeled: route/process-wall = 1.65x slower; route/author
internal AvgTime = 150.39x slower.
```

Carry-forward review questions:

```text
1. Is the matrix arithmetic reproducible from Goal5253/Goal5260 JSON?
2. Is matching by case_name sufficient to prevent denominator mismatches?
3. Should the author internal AvgTime ratio remain in the main matrix as a
   phase-gap warning or move to an appendix?
```

## Current Review Packet After Goal5261

```text
history/internal_docs/call_for_review_goals5255_5261_xhd_hd_exec_user_entrypoint_all400_and_performance_2026-07-09.md
```

Goals5255-5261 remain implemented_review_pending until an external review is present.

## Goal5262 - X-HD User Entrypoint Docs And Manifest Status

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5262_xhd_user_entrypoint_docs_and_manifest_status_result_2026-07-09.md
history/internal_docs/call_for_review_goal5262_xhd_user_entrypoint_docs_and_manifest_status_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
tests/goal5262_xhd_user_entrypoint_docs_status_test.py
```

Summary:

```text
Updates the X-HD README and manifest to reflect the current user-facing
hd_exec-compatible entrypoint state:
xhd_public_modelnet40_all400_hd_exec_entrypoint_complete__full_paper_incomplete.
It records Goal5260 all-400 public ModelNet40 correctness evidence and Goal5261
denominator-separated performance matrix while keeping full-paper, exact dataset,
figure, speedup, and parity claims false.
```

Carry-forward review questions:

```text
1. Is this status string accurate and not too strong?
2. Are old README statements about representative input availability now fixed?
3. Are the denominator-labeled performance ratios safe in user-facing docs?
```

## Current Review Packet After Goal5262

```text
history/internal_docs/call_for_review_goals5255_5262_xhd_hd_exec_entrypoint_all400_performance_and_docs_2026-07-09.md
```

Goals5255-5262 remain implemented_review_pending until an external review is present.

## Goal5263 - hd_exec Entrypoint Graphics Dragon/HappyBuddha

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5263_xhd_hd_exec_graphics_dragon_happy_entrypoint_result_2026-07-09.md
history/internal_docs/call_for_review_goal5263_xhd_hd_exec_graphics_dragon_happy_entrypoint_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json
tests/goal5263_xhd_hd_exec_graphics_dragon_happy_pod_artifact_test.py
```

Summary:

```text
Runs the full-public Stanford Graphics Dragon -> HappyBuddha Level-B
representative pair through the RTDL hd_exec-compatible entrypoint. Both
cell-mbr-fast-scalar and cell-mbr-exact-witness match the Goal5186 author rerun
HDResult within 1e-6; exact-witness reports per_source_witness_exact=true.
This is public same-source representative evidence, not exact paper byte-input
identity or full paper reproduction.
```

Carry-forward review questions:

```text
1. Is Goal5186 author rerun HDResult the correct comparator for this Level-B
   user-entrypoint graphics gate?
2. Are fast-scalar and exact-witness route labels/witness contracts clear?
3. Does the README/manifest addition preserve exact-paper and performance
   boundaries?
```

## Current Review Packet After Goal5263

```text
history/internal_docs/call_for_review_goals5255_5263_xhd_hd_exec_entrypoint_modelnet40_graphics_performance_docs_2026-07-09.md
```

Goals5255-5263 remain implemented_review_pending until an external review is present.

## Goal5264 - hd_exec Entrypoint Graphics Dragon/AsianDragon

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5264_xhd_hd_exec_graphics_dragon_asian_entrypoint_result_2026-07-09.md
history/internal_docs/call_for_review_goal5264_xhd_hd_exec_graphics_dragon_asian_entrypoint_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json
tests/goal5264_xhd_hd_exec_graphics_dragon_asian_pod_artifact_test.py
```

Summary:

```text
Runs the Stanford Graphics Dragon -> AsianDragon scaled 1e-3 same-source
candidate through the RTDL hd_exec-compatible entrypoint using the
cell-mbr-exact-witness route. It matches the Goal5239 author rerun HDResult
within 1e-6 with abs diff about 2.37e-9, point counts 437645/3609600,
translate-min preprocessing, route wall about 2651.05ms, and
per_source_witness_exact=true. The paper-log drift remains visible and this
does not prove exact paper byte-input identity or full paper reproduction.
```

Carry-forward review questions:

```text
1. Is Dragon -> AsianDragon scaled 1e-3 acceptable as Level-B same-source /
   scaled-candidate evidence?
2. Does the report keep author-rerun match separate from paper-log drift?
3. Is the README/manifest status string still honest after adding this second
   graphics representative?
```

## Current Review Packet After Goal5264

```text
history/internal_docs/call_for_review_goals5255_5264_xhd_hd_exec_entrypoint_modelnet40_graphics_performance_docs_2026-07-09.md
```

Goals5255-5264 remain implemented_review_pending until an external review is present.

## Goal5265 - hd_exec Entrypoint Graphics ThaiStatuette/HappyBuddha

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5265_xhd_hd_exec_graphics_thai_happy_entrypoint_result_2026-07-09.md
history/internal_docs/call_for_review_goal5265_xhd_hd_exec_graphics_thai_happy_entrypoint_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_statuette_scaled_1e-3_candidate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_author_thai_happy_scaled_rt_gpu_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json
tests/goal5265_xhd_hd_exec_graphics_thai_happy_pod_artifact_test.py
```

Summary:

```text
Acquires public Stanford XYZRGB ThaiStatuette, prepares an app-owned 1e-3
scaled PLY candidate matching the paper-log coordinate scale, runs author
hd_exec on ThaiStatuette scaled -> HappyBuddha, and runs the RTDL
hd_exec-compatible exact-witness route. RTDL matches author rerun within 1e-6
with abs diff about 6.34e-9 and per_source_witness_exact=true. This remains
Level-B same-source/scaled candidate evidence, not exact paper byte-input
identity or full paper reproduction.
```

Carry-forward review questions:

```text
1. Is the 1e-3 ThaiStatuette scaling justified by the paper-branch MBR scale?
2. Does author rerun matching paper log within 1e-6 make this a valid Level-B
   graphics representative gate?
3. Are route timing and author Running.AvgTime kept denominator-separated?
```

## Current Review Packet After Goal5265

```text
history/internal_docs/call_for_review_goals5255_5265_xhd_hd_exec_entrypoint_modelnet40_graphics_performance_docs_2026-07-09.md
```

Goals5255-5265 remain implemented_review_pending until an external review is present.

## Goal5266 - hd_exec Entrypoint Graphics ThaiStatuette/AsianDragon

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5266_xhd_hd_exec_graphics_thai_asian_entrypoint_result_2026-07-09.md
history/internal_docs/call_for_review_goal5266_xhd_hd_exec_graphics_thai_asian_entrypoint_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5266_author_thai_asian_scaled_rt_gpu_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json
tests/goal5266_xhd_hd_exec_graphics_thai_asian_pod_artifact_test.py
```

Summary:

```text
Runs the Stanford Graphics ThaiStatuette scaled 1e-3 -> AsianDragon scaled 1e-3
same-source/scaled candidate through author hd_exec and the RTDL
hd_exec-compatible exact-witness route. RTDL matches the author rerun within
1e-6 with abs diff about 1.10e-8, point counts 4999996/3609600,
translate-min preprocessing, route wall about 10770.02ms, and
per_source_witness_exact=true. This remains Level-B same-source/scaled
candidate evidence, not exact paper byte-input identity, not full paper
reproduction, and not performance parity.
```

Carry-forward review questions:

```text
1. Is ThaiStatuette -> AsianDragon scaled 1e-3 acceptable as Level-B
   same-source/scaled-candidate evidence?
2. Does the packet keep author rerun, paper-log match, and RTDL route timing
   separate without performance overclaim?
3. Does completing this fourth graphics representative gate justify the current
   entrypoint status while still leaving full-paper completion open?
```

## Current Review Packet After Goal5266

```text
history/internal_docs/call_for_review_goals5255_5266_xhd_hd_exec_entrypoint_modelnet40_graphics_performance_docs_2026-07-09.md
```

Goals5255-5266 remain implemented_review_pending until an external review is present.

## Goal5267 - Full Paper Coverage Gap Matrix

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5267_xhd_full_paper_coverage_gap_matrix_result_2026-07-09.md
history/internal_docs/call_for_review_goal5267_xhd_full_paper_coverage_gap_matrix_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json
tests/goal5267_xhd_full_paper_coverage_gap_matrix_test.py
```

Summary:

```text
Maps current entrypoint evidence to the full paper target. It records
ModelNet40 all-400 plus four Stanford Graphics gates as strong Level-B
evidence, keeps Figure 5-11 in not_reproduced status, and selects Figure 6
pruning-effectiveness phase/counter mapping as the next substantive
algorithmic target. It does not claim full paper reproduction, exact paper
byte-input identity, author RT-core equivalence, or performance parity.
```

Carry-forward review questions:

```text
1. Is it correct to keep all paper Figures 5-11 unreproduced despite the
   stronger entrypoint evidence?
2. Is Figure 6 the right next target after Dragon -> AsianDragon entrypoint
   evidence?
3. Does the matrix avoid using Level-B same-source evidence as exact paper
   byte-input identity?
```

## Goal5268 - Figure 6 Pruning Phase/Counter Mapping

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5268_xhd_figure6_pruning_phase_counter_mapping_result_2026-07-09.md
history/internal_docs/call_for_review_goal5268_xhd_figure6_pruning_phase_counter_mapping_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_figure6_pruning_phase_counter_mapping_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_fig6_noopt_dragon_asian_scaled_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_fig6_eb_dragon_asian_scaled_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_fig6_eb_prune_dragon_asian_scaled_profile_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_fig6_xhd_dragon_asian_scaled_profile_pod.json
tests/goal5268_xhd_figure6_pruning_mapping_test.py
```

Summary:

```text
Maps author Figure 6 pruning-effectiveness flags, script variants, and
profiling counters for Dragon -> AsianDragon on the current Level-B
same-source/scaled candidate. NoOpt, EB, and EB+Prune profiling variants match
the author reference HD and expose Hits / ComparedPoints. The LB=256/full-XHD
profiling variant is not correctness-clean on this candidate: check=true aborts
with Wrong HausdorffDistance. Therefore Figure 6 remains not_reproduced.
```

Carry-forward review questions:

```text
1. Is the author Figure 6 flag/script/counter mapping correct?
2. Is it correct to block any Figure 6 reproduction claim until the LB=256
   correctness issue is resolved?
3. Does this packet keep Level-B phase/counter evidence separate from exact
   paper byte-input identity and performance-ratio claims?
```

## Goal5269 - Figure 6 LB=256 Correctness Probe

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5269_xhd_figure6_lb256_correctness_probe_result_2026-07-09.md
history/internal_docs/call_for_review_goal5269_xhd_figure6_lb256_correctness_probe_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5269_figure6_lb256_correctness_probe_2026-07-09.json
tests/goal5269_xhd_figure6_lb256_correctness_probe_test.py
```

Summary:

```text
Classifies the Goal5268 LB=256/full-XHD failure. The author paper-branch log
records LB=256 on exact /local/storage/shared/HDDatasets graphics paths, but
those exact files are unavailable on the current POD and the current
public/scaled candidate has slightly different MBRs. On the current candidate,
lb=32..1152 gives the same wrong HDResult, while lb>=1280 in the refined scan
is correctness-clean; lb=1024 check=true aborts and lb=2048 check=true passes.
This blocks Figure 6 reproduction from the Level-B candidate.
```

Carry-forward review questions:

```text
1. Is it correct to classify this as a Level-B candidate/provenance gap rather
   than a Figure 6 reproduction?
2. Is lb=2048 correctly treated as a diagnostic substitute only, not a paper
   Figure 6 setting?
3. Does this leave exact paper byte-input identity and Figure 6 reproduction
   open?
```

## Goal5270 - Figure 6 Exact-Input Availability / Diagnostic Decision

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5270_xhd_figure6_exact_input_availability_decision_result_2026-07-09.md
history/internal_docs/call_for_review_goal5270_xhd_figure6_exact_input_availability_decision_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5270_figure6_exact_input_availability_decision_2026-07-09.json
tests/goal5270_xhd_figure6_exact_input_decision_test.py
```

Summary:

```text
Confirms that the author exact Figure 6 inputs under
/local/storage/shared/HDDatasets/graphics are unavailable on the current POD,
while only Level-B candidate files under /tmp/xhd_goal5234/data are present.
Figure 6 remains not_reproduced. The project may create a separately named
Level-B pruning diagnostic, but must not publish it as Figure 6 or use lb=2048
as a substitute for the author's lb=256 Figure 6 setting.
```

Carry-forward review questions:

```text
1. Does the exact-input availability probe justify keeping Figure 6 blocked?
2. Is it correct to authorize only a separately named Level-B diagnostic while
   exact inputs remain unavailable?
3. Does the packet preserve the claim boundary against full paper reproduction,
   exact paper byte-input identity, Figure 6 reproduction, and performance
   ratio claims?
```

## Goal5271 - Level-B Pruning Diagnostic

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5271_xhd_level_b_pruning_diagnostic_result_2026-07-09.md
history/internal_docs/call_for_review_goal5271_xhd_level_b_pruning_diagnostic_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5271_level_b_pruning_diagnostic_2026-07-09.json
tests/goal5271_xhd_level_b_pruning_diagnostic_test.py
```

Summary:

```text
Creates a separately named Level-B pruning diagnostic on the current
public/scaled Dragon -> AsianDragon candidate. The primary diagnostic includes
only correctness-clean noopt, eb, and eb_prune profile rows; it records EB and
Prune reductions in AvgTime and ComparedPoints. The author Figure 6 lb=256
setting remains invalid on this candidate, and lb=2048 remains only a
candidate-level correctness-clean control, not a Figure 6 substitute.
```

Carry-forward review questions:

```text
1. Is the primary diagnostic correctly limited to correctness-clean rows?
2. Are lb=256 and lb=2048 framed correctly?
3. Does the packet avoid Figure 6, exact input, author RT-core, and performance
   ratio overclaims?
```

## Goal5272 - Figure 11 Author Memory Log Matrix

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5272_xhd_figure11_author_memory_log_matrix_result_2026-07-09.md
history/internal_docs/call_for_review_goal5272_xhd_figure11_author_memory_log_matrix_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5272_figure11_author_memory_log_matrix_2026-07-09.json
tests/goal5272_xhd_figure11_author_memory_log_matrix_test.py
```

Summary:

```text
Extracts the author-side Figure 11 memory matrix from draw_mem.py and logs/mem.
The artifact records NN-KD, NN-Clover, and X-HD total memory for geospatial and
graphics workloads, plus the X-HD breakdown fields BVH, Grid, MBRs B, WL, and
WL Heavy Peak. This is author-log matrix evidence only; Figure 11 remains
not_reproduced until RTDL has a comparable memory accounting boundary.
```

Carry-forward review questions:

```text
1. Does the artifact correctly encode draw_mem.py's memory summation contract?
2. Is the X-HD breakdown enough to define the next RTDL memory instrumentation
   target?
3. Does the packet avoid claiming Figure 11 reproduction or memory parity?
```

## Goal5273 - RTDL Memory Accounting Boundary For Figure 11

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5273_xhd_rtdl_memory_accounting_boundary_result_2026-07-09.md
history/internal_docs/call_for_review_goal5273_xhd_rtdl_memory_accounting_boundary_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5273_rtdl_memory_accounting_boundary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py
tests/goal5273_xhd_rtdl_memory_accounting_test.py
tests/goal5273_xhd_rtdl_memory_accounting_boundary_artifact_test.py
```

Summary:

```text
Defines an explicit RTDL-side memory accounting boundary for the author Figure
11 X-HD fields. Grid and MBRs B are estimated from generic route metadata; WL is
estimated only when frontier_row_capacity is present; BVH and WL Heavy Peak are
explicitly unavailable, not silently zero. This is an accounting boundary only:
Figure 11 remains not_reproduced and no memory parity or exact allocator claim
is made.
```

Carry-forward review questions:

```text
1. Is the author-field to RTDL-status mapping honest?
2. Are unavailable fields represented as unavailable with bytes=null?
3. Does the artifact avoid comparing RTDL estimated totals to author memory logs
   as same-denominator measurements?
4. Is the next blocker correctly identified as native allocator/BVH/heavy
   worklist telemetry or explicit status-bearing integration into hd_exec output?
```

## Goal5274 - hd_exec-Compatible Memory Accounting Integration

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5274_xhd_hd_exec_memory_accounting_integration_result_2026-07-09.md
history/internal_docs/call_for_review_goal5274_xhd_hd_exec_memory_accounting_integration_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5274_hd_exec_memory_accounting_attached_example_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
tests/goal5274_xhd_hd_exec_memory_accounting_integration_test.py
tests/goal5274_xhd_hd_exec_memory_accounting_artifact_test.py
```

Summary:

```text
Adds opt-in --include-memory-accounting to the app-owned RTDL hd_exec-compatible
entrypoint. When enabled, status-bearing RTDL accounting is attached under
Running.Repeats[0].Memory and RTDL.memory_accounting. The object is explicitly
not the author's raw Figure 11 Memory schema: unavailable fields remain
unavailable, public-columnar routes fail closed, and Figure 11 remains
not_reproduced.
```

Carry-forward review questions:

```text
1. Is the opt-in Running.Repeats[0].Memory object clear enough that users will
   not mistake it for author Figure 11 parity?
2. Is it correct to keep this as status-bearing accounting rather than a raw
   numeric dict while BVH and WL Heavy Peak are unavailable?
3. Does this close only the output-integration task, leaving native allocator /
   BVH / heavy-worklist telemetry as the next blocker?
```

## Goal5275 - Native Cell-MBR Memory Telemetry

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5275_xhd_native_memory_telemetry_result_2026-07-09.md
history/internal_docs/call_for_review_goal5275_xhd_native_memory_telemetry_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5275_tiny3d_native_memory_telemetry_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5275_stanford_sample256_native_memory_telemetry_pod_2026-07-09.json
tests/goal5275_xhd_native_memory_telemetry_contract_test.py
tests/goal5275_xhd_native_memory_telemetry_artifact_test.py
```

Summary:

```text
Adds an optional native telemetry symbol for the generic OptiX 3-D cell-MBR
nearest-frontier route and maps measured GAS output-buffer bytes to the
status-bearing RTDL BVH field when available. POD evidence shows telemetry in
hd_exec-compatible output for tiny3D (BVH=896 bytes) and Stanford sample256
(BVH=7552 bytes). This reduces the opaque BVH gap but does not reproduce Figure
11, does not measure WL Heavy Peak, and does not claim author memory parity or
exact GPU allocator peak accounting.
```

Carry-forward review questions:

```text
1. Is accel_output_bytes an honest status-bearing BVH measurement, or too narrow
   to map into the author-facing BVH field?
2. Are transient build workspace and route device buffers correctly kept as
   RTDL-only fields rather than folded into author Figure 11 memory?
3. Is a bounded RTDL memory row now defensible, or is peak allocator /
   heavy-worklist telemetry still required first?
```

## Goal5276 - RTDL Bounded Memory Matrix

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5276_xhd_rtdl_bounded_memory_matrix_result_2026-07-09.md
history/internal_docs/call_for_review_goal5276_xhd_rtdl_bounded_memory_matrix_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5276_rtdl_bounded_memory_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/xhd_rtdl_memory_matrix.py
tests/goal5276_xhd_rtdl_bounded_memory_matrix_test.py
```

Summary:

```text
Builds a bounded/status-bearing RTDL memory matrix from Goal5275 hd_exec
telemetry artifacts. The matrix has two rows, measured BVH rows=2, WL Heavy Peak
unavailable rows=2, and same_denominator_author_figure11=false. This makes the
RTDL memory evidence reviewable as a table but still does not reproduce Figure
11 or authorize author memory parity.
```

Carry-forward review questions:

```text
1. Is "bounded RTDL memory matrix" the correct claim, or does the artifact need
   a narrower name?
2. Does the matrix correctly refuse author-vs-RTDL memory ratios?
3. Is peak/heavy-worklist telemetry required next, or should review accept that
   the current RTDL route has no author-like heavy-worklist denominator?
```

## Goal5277 - Memory Denominator Alignment Decision

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5277_xhd_memory_denominator_alignment_decision_result_2026-07-09.md
history/internal_docs/call_for_review_goal5277_xhd_memory_denominator_alignment_decision_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5277_memory_denominator_alignment_decision_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5276_rtdl_bounded_memory_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py
Paper-reproduction-apps/x-hd-paper/scripts/xhd_rtdl_memory_matrix.py
tests/goal5277_xhd_memory_denominator_alignment_decision_test.py
tests/goal5276_xhd_rtdl_bounded_memory_matrix_test.py
tests/goal5273_xhd_rtdl_memory_accounting_test.py
```

Summary:

```text
Audits the author X-HD source for Figure 11 memory denominators and records a
formal non-comparability decision. Author WL is in_queue + miss_queue
(2 * n_points_a * sizeof(uint32_t)); author WL Heavy Peak is the peak
heavy-cell offload queue. RTDL current WL is generic frontier row-table
capacity, and RTDL exposes no author-like heavy-cell offload peak. The updated
RTDL memory matrix therefore keeps same_denominator_author_figure11=false and
Figure 11 remains not_reproduced.
```

Carry-forward review questions:

```text
1. Does the author source evidence correctly establish the WL and WL Heavy Peak
   denominators?
2. Does the updated RTDL WL status avoid implying same-denominator comparison?
3. Is it correct to require a generic heavy-cell/offload worklist API plus peak
   queue telemetry before any Figure 11 parity claim?
4. Does the packet avoid claiming Figure 11 reproduction, author memory parity,
   or memory ratios?
```

## Goal5278 - Generic Heavy-Offload Worklist API Design

Status:

```text
design_ready_review_pending
```

Evidence:

```text
history/internal_docs/goal5278_generic_heavy_offload_worklist_api_design_2026-07-09.md
history/internal_docs/call_for_review_goal5278_generic_heavy_offload_worklist_api_design_2026-07-09.md
```

Summary:

```text
Defines the generic system API direction required to close the Goal5277 Figure
11 denominator gap: a generic heavy/offload worklist plus peak telemetry. The
design keeps app-specific X-HD meanings out of core, requires a non-X-HD
consumer before X-HD Figure 11 mapping, and states that WL / WL Heavy Peak can
only be mapped after same-denominator in/miss and heavy-offload queue telemetry
exists.
```

Carry-forward review questions:

```text
1. Is the proposed worklist schema generic enough?
2. Are the telemetry fields sufficient to align with author WL / WL Heavy Peak?
3. Is the non-X-HD consumer gate required before X-HD mapping?
4. Should the project pursue this API now or stop Figure 11 under the current
   denominator-not-aligned decision?
```

## Goal5279 - Generic Heavy-Offload Worklist Reference

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5279_generic_heavy_offload_worklist_reference_result_2026-07-09.md
history/internal_docs/call_for_review_goal5279_generic_heavy_offload_worklist_reference_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5279_generic_heavy_offload_worklist_reference_2026-07-09.json
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
tests/goal5279_generic_heavy_offload_worklist_test.py
```

Summary:

```text
Implements the first concrete system step from Goal5278: a generic
heavy/offload worklist row schema plus a NumPy/CPU reference helper. The helper
emits active/miss/deferred work rows, fails closed on capacity overflow, and
records status-bearing queue / peak telemetry. A non-X-HD facility-backlog
consumer exercises the same helper.
```

Carry-forward review questions:

```text
1. Is the row schema generic enough, or too shaped by X-HD Figure 11?
2. Are queue capacity / byte / peak row telemetry fields sufficient for the
   next native telemetry ABI spike?
3. Should this helper remain public now, or stay internal until Goal5280 adds a
   stronger non-X-HD consumer packet?
4. Does this correctly avoid claiming Figure 11 reproduction, author memory
   parity, native backend completion, or performance?
```

## Goal5280 - Heavy-Offload Non-XHD Consumer Gate

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5280_heavy_offload_non_xhd_consumer_gate_result_2026-07-09.md
history/internal_docs/call_for_review_goal5280_heavy_offload_non_xhd_consumer_gate_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5280_heavy_offload_non_xhd_consumer_gate_2026-07-09.json
tests/goal5280_heavy_offload_non_xhd_consumer_gate_test.py
```

Summary:

```text
Adds a stronger non-X-HD consumer gate for the Goal5279 worklist helper. The
consumer is a retry/backlog scheduler, not a geometry, Hausdorff, paper, or
X-HD workload. It exercises active, miss, and deferred rows plus fail-closed
overflow behavior.
```

Carry-forward review questions:

```text
1. Is this non-X-HD consumer sufficient to treat the helper as generic?
2. Should the public helper be marked provisional until Goal5281 native
   telemetry exists?
3. Does this correctly keep Figure 11, memory parity, native completion, and
   performance claims unauthorized?
```

## Goal5281 - Native Heavy/Offload Telemetry ABI Spike

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5281_native_heavy_offload_telemetry_result_2026-07-09.md
history/internal_docs/call_for_review_goal5281_native_heavy_offload_telemetry_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5281_native_heavy_offload_telemetry_pod_2026-07-09.json
tests/goal5281_native_heavy_offload_telemetry_contract_test.py
tests/goal5281_native_heavy_offload_telemetry_artifact_test.py
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_prelude.h
src/rtdsl/optix_runtime.py
```

Summary:

```text
Adds a native v2 telemetry ABI for the generic OptiX 3-D cell-MBR
nearest-frontier route. The v2 ABI preserves v1 compatibility and reports
generic in-queue capacity, miss-queue capacity, heavy/offload row capacity,
peak offload rows, and peak offload queue bytes. POD evidence confirms the v2
symbol is exported and a tiny native route collects schema-v2 telemetry with
six offload rows and 96 peak queue bytes.
```

Carry-forward review questions:

```text
1. Is the v2 telemetry ABI generic enough and backward-compatible with v1?
2. Does the POD artifact prove runtime telemetry rather than source-only
   declaration?
3. Is the current miss_queue_capacity=0 semantics acceptable for the generic
   cell-MBR route?
4. Does this correctly avoid claiming Figure 11 reproduction, author memory
   parity, same-denominator comparison, or performance improvement?
5. Is Goal5282 now the right X-HD bounded mapping goal?
```

## Goal5282 - X-HD Bounded Offload Mapping

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5282_xhd_bounded_offload_mapping_result_2026-07-09.md
history/internal_docs/call_for_review_goal5282_xhd_bounded_offload_mapping_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5282_author_offload_mapping_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_offload_mapping.py
tests/goal5282_xhd_offload_author_mapping_test.py
```

Summary:

```text
Maps Goal5281 generic native v2 heavy/offload telemetry into author-shaped
X-HD fields. OffloadingSize row-count shape maps to 6 rows, and the
author-width WL Heavy Peak candidate is 48 bytes, but RTDL measured queue bytes
are 96 bytes because the current generic queue uses 64-bit id pairs. WL remains
not aligned because native in_queue_capacity is attempted frontier hits rather
than author in_queue + miss_queue over source points.
```

Carry-forward review questions:

```text
1. Is the OffloadingSize row-count shape mapping valid?
2. Is it correct to keep same_denominator_author_figure11=false because byte
   width and WL semantics remain different?
3. Should the next step be a shape-only Figure 11 candidate row, or should
   Figure 11 be closed as denominator-not-aligned under the current route?
4. Does this correctly avoid claiming Figure 11 reproduction, author memory
   parity, same-denominator comparison, or memory/performance ratios?
```

## Goal5283 - X-HD Figure 11 Disposition

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5283_xhd_figure11_disposition_result_2026-07-09.md
history/internal_docs/call_for_review_goal5283_xhd_figure11_disposition_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5283_figure11_disposition_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure11_disposition.py
tests/goal5283_xhd_figure11_disposition_test.py
```

Summary:

```text
Consolidates author Figure 11 logs, RTDL bounded memory matrix, and Goal5282
offload mapping. The artifact keeps one shape-only candidate but marks it as
not a Figure 11 row. Current decision: Figure 11 is closed under the current
RTDL route as denominator-not-aligned after native mapping. No memory ratio,
author parity, or Figure 11 reproduction claim is authorized.
```

Carry-forward review questions:

```text
1. Is closing the current Figure 11 line as denominator-not-aligned justified?
2. Does the shape-only candidate remain clearly non-Figure-11 and non-ratio?
3. Are the reopen requirements sufficient if the owner later wants to build a
   denominator-aligned generic native worklist?
```

## Goal5284 - X-HD Figure 9 Auto-Tune Semantics Matrix

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5284_xhd_figure9_auto_tune_semantics_result_2026-07-09.md
history/internal_docs/call_for_review_goal5284_xhd_figure9_auto_tune_semantics_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_auto_tune_matrix.py
tests/goal5284_xhd_figure9_auto_tune_matrix_test.py
```

Summary:

```text
Maps the author paper-branch run_all/auto_tune logs for Figure 9. The logs
contain 1814 auto_tune records over 907 unique pairs, with complete coverage of
two observed config labels: n_points_cell_false_max_hit_false and
n_points_cell_true_max_hit_true. Running.NumPointsPerCell is [8] across these
records, so the extracted run_all auto_tune logs are not a multi-value grid-size
sweep. Goal5284 therefore keeps Figure 9 as not_reproduced and recommends
source/script mapping for the actual Figure 9 driver before any more RTDL route
work.
```

Carry-forward review questions:

```text
1. Are the auto_tune counts and paired-config coverage correct?
2. Is it correct to say these logs are useful author-log mapping but not Figure
   9 reproduction?
3. Is the absence of a multi-value grid-size sweep sufficiently prominent?
4. Should the next step inspect author scripts/source for the actual Figure 9
   plotting or grid-tuning driver?
```

## Goal5285 - X-HD Figure 9 Source / Script Audit

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5285_xhd_figure9_source_script_audit_result_2026-07-09.md
history/internal_docs/call_for_review_goal5285_xhd_figure9_source_script_audit_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5285_figure9_source_script_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_source_audit.py
tests/goal5285_xhd_figure9_source_script_audit_test.py
```

Summary:

```text
Audits the pinned author paper-branch source/scripts for Figure 9 provenance.
The source contains a Figure-9-like auto-tune plotting script that saves
auto-tune.pdf and expects four variants, but the current run_all/auto_tune logs
contain only two of those variants. Training sweeps exist under logs/train, but
they are not the same denominator as the plot script's run_all/auto_tune inputs.
Figure 9 remains not_reproduced.
```

Carry-forward review questions:

```text
1. Is the plot script and active draw call identification correct?
2. Is the four-expected-variant vs two-observed-run_all-variant gap correct?
3. Is it correct not to promote logs/train sweeps into Figure 9 reproduction?
4. Should the next step recover the missing author-side plot denominator before
   any more RTDL route work for Figure 9?
```

## Goal5286 - X-HD Figure 9 Branch Availability Audit

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5286_xhd_figure9_branch_availability_audit_result_2026-07-09.md
history/internal_docs/call_for_review_goal5286_xhd_figure9_branch_availability_audit_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5286_figure9_branch_availability_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_branch_availability_audit.py
tests/goal5286_xhd_figure9_branch_availability_audit_test.py
```

Summary:

```text
Audits paper/main/hybrid for the Figure 9 variants missing after Goal5285. The
paper branch still has only the two observed run_all configs and a checked-in
auto-tune.pdf; main and hybrid have no run_all auto_tune logs or Figure-9-like
script/PDF files. Figure 9 remains not_reproduced.
```

Carry-forward review questions:

```text
1. Is it correct that the missing variants are not present on main or hybrid?
2. Is it correct to treat checked-in auto-tune.pdf as evidence but not as a
   reproducible Figure 9 denominator?
3. Should Figure 9 now either regenerate missing variants, map train sweeps, or
   close as source-mapped but not reproduced?
```

## Goal5287 - X-HD Figure 9 Disposition

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5287_xhd_figure9_disposition_result_2026-07-09.md
history/internal_docs/call_for_review_goal5287_xhd_figure9_disposition_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5287_figure9_disposition_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_disposition.py
tests/goal5287_xhd_figure9_disposition_test.py
```

Summary:

```text
Consolidates Goals5284-5286 and closes the current Figure 9 line as
author-denominator-missing. The plot script expects four variants, current logs
provide two, main/hybrid do not recover the missing variants, checked-in PDF is
not a reproducible denominator, and training sweeps require an externally
reviewed mapping before use.
```

Carry-forward review questions:

```text
1. Is closing the current Figure 9 line as author-denominator-missing justified?
2. Are the reopen conditions sufficient?
3. Is it correct to move to another full-paper blocker unless the owner
   explicitly authorizes regenerating the missing variants?
```

## Goal5288 - X-HD Figure 5 Timing Denominator Audit

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5288_xhd_figure5_timing_denominator_audit_result_2026-07-09.md
history/internal_docs/call_for_review_goal5288_xhd_figure5_timing_denominator_audit_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure5_timing_denominator_audit.py
tests/goal5288_xhd_figure5_timing_denominator_audit_test.py
```

Summary:

```text
Audits Figure 5 author timing denominator. Author run_all logs cover 2535
records / 507 complete pairs across BraTS, geo, and graphics, with 2 auto_tune
+ 1 eb_gpu + 1 hybrid_gpu + 1 rt_gpu per pair. Current RTDL evidence lacks
BraTS and geo full workload gates, and author internal timing is not denominator
aligned with RTDL route/process wall. Figure 5 remains not_reproduced.
```

Carry-forward review questions:

```text
1. Are the Figure 5 author-log counts and complete-pair structure correct?
2. Is it correct to forbid a Figure 5 performance ratio under current evidence?
3. Should the next execution target be a bounded same-POD Figure 5 subset or
   Figure 6 phase/counter mapping?
```

## Goal5289 - X-HD Figure 5 Bounded Same-POD Probe

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5289_xhd_figure5_bounded_same_pod_probe_result_2026-07-09.md
history/internal_docs/call_for_review_goal5289_xhd_figure5_bounded_same_pod_probe_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5289_figure5_bounded_same_pod_probe_2026-07-09.json
tests/goal5289_xhd_figure5_bounded_same_pod_probe_test.py
```

Summary:

```text
Runs a bounded same-POD Figure 5 graphics probe on the currently available
Dragon -> AsianDragon scaled-1e-3 candidate. The POD is reachable through the
current wrapper and both author `hd_exec` and RTDL run on the same POD, but
author X-HD/LB=256 returns HDResult 0.06545527279376984 while the RTDL exact
route returns 0.06536787240753439. The value mismatch means this candidate is
a no-go for Figure 5 reproduction/performance comparison, and no ratio is
authorized.
```

Carry-forward review questions:

```text
1. Is it correct to classify this same-POD probe as a no-go because
   matched_value=false?
2. Is it correct to refuse author-vs-RTDL performance ratios even though both
   runs happened on the same POD?
3. Should the next Figure 5 work search for a value-matched candidate before
   running expensive RTDL timings, or move to another paper blocker?
```

## Goal5290 - X-HD Figure 5 Graphics Author-Value Precheck

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5290_xhd_figure5_graphics_author_value_precheck_result_2026-07-09.md
history/internal_docs/call_for_review_goal5290_xhd_figure5_graphics_author_value_precheck_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5290_figure5_graphics_author_value_precheck_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5290_author_value_probe_raw_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure5_graphics_author_value_precheck.py
tests/goal5290_xhd_figure5_graphics_author_value_precheck_test.py
```

Summary:

```text
Runs an author-only value precheck for the available Dragon -> AsianDragon
input variants before any further RTDL timing. The paper-log HDResult is
0.06536811590194702. The unscaled POD author run returns 52.4535, and the
scaled-1e-3 POD author run returns 0.0654553. Neither variant matches the paper
log within tolerance, so continue_to_rtdl_timing=false and no Figure 5 ratio is
authorized.
```

Carry-forward review questions:

```text
1. Is the paper-log target value extraction correct?
2. Does the POD stdout evidence support the unscaled and scaled author values?
3. Is it correct to stop this candidate before any further RTDL timing?
4. Should future Figure 5 candidates require author-only value precheck before
   expensive RTDL execution?
```

## Goal5291 - X-HD Figure 5 Dragon -> HappyBuddha Candidate Matrix

Status:

```text
implemented_review_pending
```

Evidence:

```text
history/internal_docs/goal5291_xhd_figure5_dragon_happy_candidate_matrix_result_2026-07-09.md
history/internal_docs/call_for_review_goal5291_xhd_figure5_dragon_happy_candidate_matrix_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5291_figure5_dragon_happy_candidate_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure5_dragon_happy_candidate_matrix.py
tests/goal5291_xhd_figure5_dragon_happy_candidate_matrix_test.py
```

Summary:

```text
Consolidates Dragon -> HappyBuddha as the strongest current Figure 5 graphics
Level-B candidate. The paper-branch log value is 0.12572969496250153, the author
rerun value is 0.12572988867759705, and the RTDL route value is
0.12572988629271128, all within 1e-6. The matrix keeps paper-log timing, author
rerun timing, RTDL fresh route timing, and RTDL explicit-warm timing separated.
No author-vs-RTDL ratio is authorized; exact paper dataset identity and full
Figure 5 reproduction remain unproved.
```

Carry-forward review questions:

```text
1. Is the Dragon -> HappyBuddha paper-log value extraction correct?
2. Does the evidence support classifying this as a value-matched Level-B
   graphics candidate?
3. Is the denial of exact paper dataset identity and Figure 5 full reproduction
   correctly stated?
4. Are the timing denominators separated enough to forbid an author-vs-RTDL
   ratio?
5. Does the report correctly carry forward the Goal5211/5212 approximate
   witness caveat?
```

## Consolidated Review Packet - Goals5288-5291 Figure 5

Status:

```text
ready_for_external_review
```

Packet:

```text
history/internal_docs/call_for_review_goals5288_5291_xhd_figure5_packet_2026-07-09.md
```

Purpose:

```text
Review the current Figure 5 evidence as one decision packet: author denominator
coverage, Dragon -> AsianDragon no-go, Dragon -> HappyBuddha Level-B
value-matched candidate, and the continued refusal to report a performance
ratio or full Figure 5 reproduction claim.
```

Expected review outcomes:

```text
approve_goals5288_5291_figure5_packet__dragon_happy_level_b_candidate_only
revise_figure5_packet_claim_boundary_or_denominator
block_figure5_packet_due_to_value_or_evidence_error
```

## Consolidated Review Packet - Goals5268-5271 Figure 6

Status:

```text
ready_for_external_review
```

Packet:

```text
history/internal_docs/call_for_review_goals5268_5271_xhd_figure6_packet_2026-07-09.md
```

Purpose:

```text
Review the current Figure 6 evidence as one decision packet: author
flags/script/profiling counter mapping, the LB=256 correctness blocker on the
current Level-B candidate, exact input unavailability, and the separately named
Level-B pruning diagnostic.
```

Expected review outcomes:

```text
approve_goals5268_5271_figure6_packet__level_b_diagnostic_only
revise_figure6_packet_claim_boundary_or_lb_substitute
block_figure6_packet_due_to_incorrect_counter_or_input_evidence
```

## Global Status Handoff - After Goal5291

Status:

```text
project_state_handoff
```

File:

```text
history/internal_docs/xhd_global_status_after_goal5291_2026-07-09.md
```

Purpose:

```text
Records the current global X-HD state after the Goal5216 midterm amendment
sign-off and the Figure 5 / Figure 6 consolidated packets. This is not an
external review verdict and does not upgrade any implemented / review-pending
goal.
```

Summary:

```text
Current strongest evidence remains one public Stanford Dragon -> HappyBuddha
Level-B same-source representative workload. RTDL matches the author binary
re-run directed-HD scalar on that public data, not the paper log. Exact paper
dataset identity, Figure 5 reproduction, Figure 6 reproduction, full paper
reproduction, and author-vs-RTDL ratios remain unauthorized. The Goal5211 route
is exact-value-only; per-source witnesses are approximate for early-aborted
sources.
```

## Goal5292 - X-HD Figure 7 Load-Balance Source / Log Audit

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5292_xhd_figure7_load_balance_audit_result_2026-07-09.md
history/internal_docs/call_for_review_goal5292_xhd_figure7_load_balance_audit_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5292_figure7_load_balance_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure7_load_balance_audit.py
tests/goal5292_xhd_figure7_load_balance_audit_test.py
```

Summary:

```text
Audits author-side Figure 7 load-balance / heavy-cell offload evidence.  The
pinned author source contains run_lb.sh and draw_lb.py, and checked-in run_all
rt_gpu logs contain LB=256 profiling-style fields.  However, checked-in
lb_comparison logs have total_json_count=0 and there is no LB=0 counterpart.
Therefore Figure 7 remains not reproduced and no RTDL/author load-balance
parity or performance ratio is authorized.
```

Carry-forward review questions:

```text
1. Does run_lb.sh truly provide only graphics pairs while draw_lb.py expects
   both geo and graphics lb_comparison directories?
2. Is the absence of checked-in lb_comparison JSON logs correctly measured?
3. Is it correct that run_all rt_gpu logs have profiling-style fields but only
   LB=256 records?
4. Is the conclusion "Figure 7 not reproduced under current evidence" justified?
5. Are the next steps correctly restricted to author lb_comparison regeneration
   or a separately named Level-B diagnostic?
```

Expected review outcomes:

```text
approve_goal5292_figure7_load_balance_audit__lb_comparison_missing_figure7_not_reproduced
revise_goal5292_figure7_audit_claim_boundary_or_script_mapping
block_goal5292_due_to_incorrect_author_log_or_script_evidence
```

## Goal5293 - X-HD Figure 8 Radius-Strategy Source / Log Audit

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5293_xhd_figure8_radius_strategy_audit_result_2026-07-09.md
history/internal_docs/call_for_review_goal5293_xhd_figure8_radius_strategy_audit_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5293_figure8_radius_strategy_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure8_radius_strategy_audit.py
tests/goal5293_xhd_figure8_radius_strategy_audit_test.py
```

Summary:

```text
Audits author-side Figure 8 radius-growing strategy evidence.  The pinned author
source contains run_radius_tuning.sh and draw_tune_radius.py, aligned on
add/double/adaptive strategies and geo/graphics categories.  However,
checked-in logs/tune_radius has total_json_count=0 and the paper-branch run_all
mapping has no explicit Figure 8 radius-strategy records.  Therefore Figure 8
remains not reproduced and no RTDL/author radius-strategy parity or performance
ratio is authorized.
```

Carry-forward review questions:

```text
1. Does run_radius_tuning.sh truly define geo/graphics add/double/adaptive runs?
2. Does draw_tune_radius.py truly expect rt_gpu_radius_add/double/adaptive logs
   for both geo and graphics?
3. Is the absence of checked-in logs/tune_radius JSON records correctly measured?
4. Is it correct that run_all provides no Figure 8 radius-strategy records?
5. Is the conclusion "Figure 8 not reproduced under current evidence" justified?
```

Expected review outcomes:

```text
approve_goal5293_figure8_radius_strategy_audit__tune_radius_logs_missing_figure8_not_reproduced
revise_goal5293_figure8_audit_claim_boundary_or_script_mapping
block_goal5293_due_to_incorrect_author_log_or_script_evidence
```

## Goal5294 - X-HD Figure 10 Scalability / Overlap Source-Log Audit

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5294_xhd_figure10_scalability_overlap_audit_result_2026-07-09.md
history/internal_docs/call_for_review_goal5294_xhd_figure10_scalability_overlap_audit_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5294_figure10_scalability_overlap_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure10_scalability_overlap_audit.py
tests/goal5294_xhd_figure10_scalability_overlap_audit_test.py
```

Summary:

```text
Audits author-side Figure 10 scalability / overlap evidence. The pinned author
source contains run_scalability.sh and draw_scalability.py, aligned on
size and translate/overlap sweeps over all_nodes.wkt. However, checked-in
logs/scalability has total_json_count=0. The paper-branch run_all mapping has
4535 workload-family records, but those records do not identify Figure 10
scale/overlap subsets, overlap-controlled input generation, overlap/selectivity
diagnostics, or exact input hashes. Therefore Figure 10 remains not reproduced
and no RTDL/author scalability parity, overlap parity, or performance ratio is
authorized.
```

Carry-forward review questions:

```text
1. Does run_scalability.sh truly define size and translate/overlap sweeps over
   all_nodes.wkt?
2. Does draw_scalability.py truly expect eb/nn/clover/rt gpu logs under both
   scal_vary_size and scal_vary_translate?
3. Is the absence of checked-in logs/scalability JSON records correctly measured?
4. Is it correct that run_all provides workload-family records but no Figure 10
   scale/overlap labels or diagnostics?
5. Is the conclusion "Figure 10 not reproduced under current evidence" justified?
```

Expected review outcomes:

```text
approve_goal5294_figure10_scalability_overlap_audit__scalability_logs_missing_figure10_not_reproduced
revise_goal5294_figure10_audit_claim_boundary_or_script_mapping
block_goal5294_due_to_incorrect_author_log_or_script_evidence
```

## Consolidated Review Packet - Goals5292-5294 Figures 7 / 8 / 10

Status:

```text
implemented_review_pending
```

File:

```text
history/internal_docs/call_for_review_goals5292_5294_xhd_figures7_8_10_author_matrix_missing_packet_2026-07-09.md
```

Purpose:

```text
Asks external review to verify the author-side source/log audit conclusion for
Figures 7, 8, and 10: scripts exist, but the numeric matrices expected by the
author plotting scripts are missing, so no RTDL comparison or figure
reproduction claim is authorized yet.
```

Expected review outcomes:

```text
approve_goals5292_5294_figures7_8_10_author_matrix_missing_packet
revise_figures7_8_10_packet_claim_boundary_or_script_mapping
block_figures7_8_10_packet_due_to_incorrect_author_log_evidence
```

## Goal5295 - X-HD Figures 7 / 8 / 10 POD Dataset Availability

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5295_xhd_figures7_8_10_pod_dataset_availability_result_2026-07-09.md
history/internal_docs/call_for_review_goal5295_xhd_figures7_8_10_pod_dataset_availability_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5295_figures7_8_10_pod_dataset_availability_2026-07-09.json
tests/goal5295_xhd_figures7_8_10_pod_dataset_availability_test.py
```

Summary:

```text
Checks whether the current POD can regenerate the missing author matrices for
Figures 7/8/10. The POD wrapper preflight succeeds and the author build exists,
but /local/storage/shared/HDDatasets is missing. All required Figure 7 graphics,
Figure 8 geo/graphics, and Figure 10 all_nodes inputs under that root are
missing. A partial Dragon/Asian temporary subset exists but is not enough for
full author matrix regeneration and must not be promoted to paper input status.
```

Expected review outcomes:

```text
approve_goal5295_pod_dataset_availability__hddatasets_missing_figures7_8_10_regeneration_blocked
revise_goal5295_dataset_path_or_claim_boundary
block_goal5295_due_to_incorrect_pod_or_dataset_evidence
```

## Goal5296 - X-HD Level-B Dragon -> AsianDragon Author LB Diagnostic

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5296_xhd_level_b_dragon_asian_lb_diagnostic_result_2026-07-09.md
history/internal_docs/call_for_review_goal5296_xhd_level_b_dragon_asian_lb_diagnostic_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5296_level_b_dragon_asian_lb_diagnostic_2026-07-09.json
tests/goal5296_xhd_level_b_lb_diagnostic_test.py
```

Summary:

```text
Runs author hd_exec on the temporary POD Dragon -> AsianDragon input with
lb=0 and lb=256. Both return HDResult=52.453487396240234. On this input,
lb=256 reduces iteration-3 compared points and RTTime but adds heavy offload
work and is slower by author Running.AvgTime and process wall. This is
author-only Level-B diagnostic evidence, not Figure 7 reproduction, not RTDL
execution, and not a performance ratio.
```

Expected review outcomes:

```text
approve_goal5296_level_b_dragon_asian_author_lb_diagnostic_not_figure7
revise_goal5296_lb_diagnostic_claim_boundary_or_input_status
block_goal5296_due_to_incorrect_author_lb_evidence
```

## Goal5297 - X-HD Dataset Acquisition Manifest

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5297_xhd_dataset_acquisition_manifest_result_2026-07-09.md
history/internal_docs/call_for_review_goal5297_xhd_dataset_acquisition_manifest_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5297_dataset_acquisition_manifest_2026-07-09.json
tests/goal5297_xhd_dataset_acquisition_manifest_test.py
```

Summary:

```text
Turns the current X-HD dataset blocker into an executable acquisition plan.
The POD is usable but lacks /local/storage/shared/HDDatasets. The local
workspace has public Stanford graphics candidates for Dragon, HappyBuddha,
AsianDragon, and ThaiStatuette with hashes, so Level-B same-source graphics
diagnostics can proceed after upload. BraTS, Census/TIGER, and OSM remain
acquisition/provenance blocked. No exact paper dataset, figure reproduction, or
performance-ratio claim is authorized.
```

Recommended next:

```text
Goal5298: upload missing public Stanford graphics files to POD through
scripts/current_pod_ssh.py and run author-only Level-B graphics value prechecks
before any new RTDL comparison.
```

Expected review outcomes:

```text
approve_goal5297_dataset_acquisition_manifest__level_b_graphics_upload_next
revise_goal5297_dataset_manifest_claim_boundary_or_asset_status
block_goal5297_due_to_incorrect_pod_or_dataset_evidence
```

## Goal5298 - X-HD Author-Only Graphics Level-B Precheck

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5298_xhd_author_graphics_precheck_result_2026-07-09.md
history/internal_docs/call_for_review_goal5298_xhd_author_graphics_precheck_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5298_author_graphics_precheck_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/dragon_happy_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/dragon_asian_scaled_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/thai_happy_scaled_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/thai_asian_scaled_author.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5298_author_graphics_precheck.py
tests/goal5298_xhd_author_graphics_precheck_test.py
```

Summary:

```text
Uploads/consolidates public Stanford graphics files under /tmp/xhd_goal5298/data
on the current POD and runs author hd_exec only. Three cases match paper-branch
author-log HDResult within 1e-6: Dragon->HappyBuddha,
ThaiStatuette-scaled->HappyBuddha, and ThaiStatuette-scaled->AsianDragon-scaled.
Dragon->AsianDragon-scaled remains unmatched with abs diff about 8.7e-5. No
RTDL route, figure reproduction, exact dataset claim, or performance ratio is
authorized.
```

Expected review outcomes:

```text
approve_goal5298_author_graphics_precheck__three_of_four_level_b_value_matched
revise_goal5298_claim_boundary_or_case_mapping
block_goal5298_due_to_incorrect_author_value_or_upload_evidence
```

## Goal5299 - X-HD ThaiStatuette -> HappyBuddha RTDL Level-B Comparison

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5299_xhd_thai_happy_rtdl_comparison_result_2026-07-09.md
history/internal_docs/call_for_review_goal5299_xhd_thai_happy_rtdl_comparison_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_level_b_rtdl_comparison_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_exact_witness_process_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_fast_scalar_process_pod.json
tests/goal5299_xhd_thai_happy_rtdl_comparison_test.py
```

Summary:

```text
Runs RTDL on the Goal5298 value-matched ThaiStatuette scaled 1e-3 ->
HappyBuddha public Stanford case. Both the exact-witness and fast-scalar RTDL
routes match the Goal5298 author rerun scalar HDResult within 1e-6
(`abs diff ~= 6.3e-9`). The exact-witness route reports route wall about 5.00s
and `per_source_witness_exact=true`. The fast-scalar route reports route wall
about 1.00s and `per_source_witness_exact=false` because global-bound early
break leaves most per-source witnesses approximate. No author-vs-RTDL ratio,
Figure reproduction, exact dataset status, or author RT-core equivalence is
authorized.
```

Expected review outcomes:

```text
approve_goal5299_thai_happy_level_b_rtdl_comparison__scalar_matched_no_ratio
revise_goal5299_witness_or_denominator_claim_boundary
block_goal5299_due_to_incorrect_value_or_route_evidence
```

## Goal5300 - X-HD ThaiStatuette -> AsianDragon RTDL Level-B Comparison

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5300_xhd_thai_asian_rtdl_comparison_result_2026-07-09.md
history/internal_docs/call_for_review_goal5300_xhd_thai_asian_rtdl_comparison_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_level_b_rtdl_comparison_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_exact_witness_process_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_fast_scalar_process_pod.json
tests/goal5300_xhd_thai_asian_rtdl_comparison_test.py
```

Summary:

```text
Runs RTDL on the Goal5298 value-matched ThaiStatuette scaled 1e-3 ->
AsianDragon scaled 1e-3 public Stanford case. Both the exact-witness and
fast-scalar RTDL routes match the Goal5298 author rerun scalar HDResult within
1e-6 (`abs diff ~= 1.10e-8`). The exact-witness route reports route wall about
10.76s and `per_source_witness_exact=true`. The fast-scalar route reports route
wall about 12.51s and `per_source_witness_exact=false`; on this case it is
slower because it emits about 4.66M frontier rows and spends most route time in
nearest continuation. No author-vs-RTDL ratio, Figure reproduction, exact
dataset status, or author RT-core equivalence is authorized.
```

Expected review outcomes:

```text
approve_goal5300_thai_asian_level_b_rtdl_comparison__scalar_matched_no_ratio
revise_goal5300_claim_boundary_or_witness_status
block_goal5300_due_to_incorrect_value_or_route_evidence
```

## Consolidated Review Packet - Goals5291 / 5298 / 5299 / 5300 Graphics Level-B

Status:

```text
ready_for_external_review
```

File:

```text
history/internal_docs/call_for_review_goals5291_5300_xhd_graphics_level_b_packet_2026-07-09.md
```

Purpose:

```text
Asks external review to verify the current public Stanford graphics Level-B
evidence set: Dragon->HappyBuddha, Thai->HappyBuddha, and Thai->Asian are
scalar value-matched with RTDL evidence, while Dragon->Asian remains a no-go.
The packet explicitly refuses Figure 5 reproduction, exact paper dataset
status, full paper reproduction, author-vs-RTDL ratios, and any claim that
fast-scalar universally beats exact-witness.
```

Expected review outcomes:

```text
approve_goals5291_5300_xhd_graphics_level_b_packet__three_value_matched_rtdl_cases_no_ratio
revise_graphics_level_b_packet_claim_boundary_or_witness_status
block_graphics_level_b_packet_due_to_incorrect_value_or_evidence
```

## Consolidated Review Packet - Goals5292-5296 Figures 7 / 8 / 10 Blocker + Level-B LB

Status:

```text
implemented_review_pending
```

File:

```text
history/internal_docs/call_for_review_goals5292_5296_xhd_figures7_8_10_blocker_and_level_b_lb_packet_2026-07-09.md
```

Purpose:

```text
Asks external review to verify the combined conclusion: Figures 7/8/10 author
numeric matrices are missing, the current usable POD lacks the exact HDDatasets
root needed to regenerate them, and the temporary Dragon/Asian lb=0/lb=256
author diagnostic is only a Level-B diagnostic rather than Figure 7
reproduction or RTDL comparison.
```

Expected review outcomes:

```text
approve_goals5292_5296_figures7_8_10_blocker_and_level_b_lb_packet
revise_goals5292_5296_claim_boundary_or_dataset_lb_evidence
block_goals5292_5296_due_to_incorrect_author_or_pod_evidence
```

## Consolidated Review Packet - Goals5292-5295 Figures 7 / 8 / 10

Status:

```text
implemented_review_pending
```

File:

```text
history/internal_docs/call_for_review_goals5292_5295_xhd_figures7_8_10_regeneration_blocker_packet_2026-07-09.md
```

Purpose:

```text
Asks external review to verify the combined conclusion: Figures 7/8/10 author
numeric matrices are missing, and the current usable POD lacks the exact
HDDatasets root needed to regenerate them. Therefore the blocker is author-side
dataset/matrix availability, not RTDL route implementation.
```

Expected review outcomes:

```text
approve_goals5292_5295_figures7_8_10_regeneration_blocker_packet
revise_figures7_8_10_regeneration_packet_claim_boundary_or_dataset_paths
block_figures7_8_10_regeneration_packet_due_to_incorrect_author_or_pod_evidence
```

## Goal5301 - X-HD Non-Graphics Dataset Provenance Matrix

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5301_xhd_non_graphics_dataset_provenance_result_2026-07-09.md
history/internal_docs/call_for_review_goal5301_xhd_non_graphics_dataset_provenance_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5301_non_graphics_dataset_provenance_matrix_2026-07-09.json
tests/goal5301_xhd_non_graphics_dataset_provenance_test.py
```

Summary:

```text
Consolidates X-HD non-graphics dataset provenance after graphics Level-B
progress. It does not run POD, author code, or RTDL code. It records that exact
paper input identity still requires file/hash provenance or deterministic
author regeneration; count/Gini matching is not sufficient. BraTS is
registration/license gated; OSM Lakes/Parks/AllNodes are public but blocked by
snapshot/filter/conversion/scale; Census/TIGER-like public geo inputs are the
highest-priority non-graphics next target.
```

Expected review outcomes:

```text
approve_goal5301_non_graphics_dataset_provenance__census_tiger_next
revise_goal5301_dataset_priority_or_claim_boundary
block_goal5301_due_to_incorrect_dataset_provenance_classification
```

## Goal5302 - X-HD Census/TIGER Source Resolution

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5302_xhd_census_tiger_source_resolution_result_2026-07-09.md
history/internal_docs/call_for_review_goal5302_xhd_census_tiger_source_resolution_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5302_census_tiger_source_resolution_plan_2026-07-09.json
tests/goal5302_xhd_census_tiger_source_resolution_test.py
```

Summary:

```text
Resolves the first concrete Census/TIGER-like geo source/conversion plan.
Author run_fig5.sh lists dtl_cnty.wkt -> uszipcode.wkt and
USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt as 2D WKT
inputs with normalize=false. The author WKT loader emits polygon outer-ring
vertices, linestring vertices, and points. Probe-verified official TIGER2023
candidates exist for national COUNTY and ZCTA520, while BG and AREAWATER are
shard-based from the current probes. County-ZCTA is recommended as the first
executable Level-B geo candidate. No geo input artifact, author/RTDL comparison,
exact dataset recovery, or performance ratio is claimed.
```

Expected review outcomes:

```text
approve_goal5302_census_tiger_source_resolution__county_zcta_first
revise_goal5302_source_choice_or_conversion_contract
block_goal5302_due_to_incorrect_author_contract_or_source_probe
```

## Goal5303 - X-HD County-ZCTA ArcGIS Bounded Fixture

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5303_xhd_county_zcta_arcgis_bounded_fixture_result_2026-07-09.md
history/internal_docs/call_for_review_goal5303_xhd_county_zcta_arcgis_bounded_fixture_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5303_county_zcta_arcgis_bounded_fixture.py
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/manifest.json
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/dtl_cnty_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/uszipcode_arcgis_bounded.wkt
tests/goal5303_xhd_county_zcta_arcgis_bounded_fixture_test.py
```

Summary:

```text
Creates the first concrete bounded County-ZCTA WKT fixture from ArcGIS
name-matched County and ZIP/ZCTA FeatureServer sources. The artifact records
hashes, feature counts, object ids, sample names, bounding boxes, and
author-loader outer-ring point-count estimates. This is Level-B
ingestion/conversion evidence only: no author hd_exec run, no RTDL run, no
exact paper input claim, no geo correctness claim, no Figure 5 claim, and no
performance ratio. The first County rows are Alabama counties and the first
ZIP/ZCTA rows are Alaska ZCTAs, so geographic representativeness is not
claimed.
```

Expected review outcomes:

```text
approve_goal5303_county_zcta_arcgis_bounded_fixture__level_b_only
revise_goal5303_fixture_source_or_claim_boundary
block_goal5303_due_to_invalid_wkt_artifact_or_overclaim
```

## Goal5304 - X-HD County-ZCTA Author Ingestion

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5304_xhd_county_zcta_author_ingestion_result_2026-07-09.md
history/internal_docs/call_for_review_goal5304_xhd_county_zcta_author_ingestion_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5304_county_zcta_author_ingestion_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/goal5304_raw/author_county_zcta_arcgis_bounded.json
Paper-reproduction-apps/x-hd-paper/results/goal5304_raw/author_stdout.txt
Paper-reproduction-apps/x-hd-paper/results/goal5304_raw/author_stderr.txt
tests/goal5304_xhd_county_zcta_author_ingestion_test.py
```

Summary:

```text
Runs author hd_exec on the Goal5303 bounded ArcGIS County-ZCTA WKT fixture on
the current POD. Author ingestion succeeds and produces HDResult
65.44752502441406 with point counts 38034 / 50272 and Running.AvgTime 6.169ms.
This is author-only Level-B ingestion evidence. RTDL has not run on this
fixture; no author/RTDL correctness, exact paper input, geo correctness,
Figure 5, performance ratio, or full-paper claim is authorized.
```

Expected review outcomes:

```text
approve_goal5304_county_zcta_author_ingestion__author_hd_exec_passed
revise_goal5304_author_command_or_claim_boundary
block_goal5304_due_to_invalid_author_ingestion_evidence_or_overclaim
```

## Goal5305 - X-HD County-ZCTA RTDL Partner Gate

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5305_xhd_county_zcta_rtdl_partner_gate_result_2026-07-09.md
history/internal_docs/call_for_review_goal5305_xhd_county_zcta_rtdl_partner_gate_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5305_county_zcta_rtdl_triton_summary_pod.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5305_county_zcta_rtdl_numba_gate.py
tests/goal5305_xhd_wkt_author_loader_semantics_test.py
tests/goal5305_xhd_county_zcta_rtdl_partner_gate_test.py
```

Summary:

```text
Extends the X-HD app-owned WKT front door to author-compatible geometry point
streams and runs the same bounded ArcGIS County-ZCTA WKT fixture through RTDL's
generic directed max-nearest partner route. The successful POD route uses
partner="triton" with dense_point_nearest_tiled and matches the Goal5304 author
HDResult 65.44752502441406 within tolerance: RTDL HDResult
65.44751976280666, abs_diff 5.2616073986655465e-06 <= 1e-5. The initial Numba
partner attempt is recorded as a POD PTX/toolchain no-go, not an algorithmic
mismatch. This is Level-B bounded same-fixture scalar correctness only; no exact
paper dataset, Figure 5, author RT-core equivalence, performance ratio, or full
paper reproduction claim is authorized.
```

Expected review outcomes:

```text
approve_goal5305_county_zcta_rtdl_partner_gate__level_b_bounded_match
revise_goal5305_wkt_semantics_or_claim_boundary
block_goal5305_due_to_invalid_author_rtdl_comparison_or_overclaim
```

## Goal5306 - X-HD WaterBodies -> BlockGroups ArcGIS Bounded Fixture

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5306_xhd_water_bg_arcgis_bounded_fixture_result_2026-07-09.md
history/internal_docs/call_for_review_goals5306_5307_xhd_water_bg_bounded_author_rtdl_gate_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5306_water_bg_arcgis_bounded_fixture.py
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/manifest.json
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USADetailedWaterBodies_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USACensusBlockGroupBoundaries_arcgis_bounded.wkt
tests/goal5306_xhd_water_bg_arcgis_bounded_fixture_test.py
```

Summary:

```text
Creates a bounded ArcGIS WKT fixture for the second X-HD Figure-5 geo pair:
USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt. The fixture
uses name-matched ArcGIS FeatureServer sources, requests the first 5 water
features and first 5 block-group features by OBJECTID, and writes one WKT
geometry per line. Author-loader point-count estimates are 124 / 894. This is
Level-B ingestion/conversion evidence only; no exact paper input, Figure 5,
geo correctness, author/RTDL correctness, or performance claim is authorized.
```

Expected review outcomes:

```text
approve_goals5306_5307_water_bg_bounded_author_rtdl_gate
revise_goals5306_5307_source_fixture_or_claim_boundary
block_goals5306_5307_due_to_invalid_author_rtdl_comparison_or_overclaim
```

## Goal5307 - X-HD WaterBodies -> BlockGroups Author/RTDL Gate

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5307_xhd_water_bg_author_rtdl_gate_result_2026-07-09.md
history/internal_docs/call_for_review_goals5306_5307_xhd_water_bg_bounded_author_rtdl_gate_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5307_water_bg_author_rtdl_partner_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/goal5307_raw/author_water_bg_arcgis_bounded.json
Paper-reproduction-apps/x-hd-paper/results/goal5307_raw/rtdl_water_bg_arcgis_bounded_triton_summary_raw_goal5305_runner.json
tests/goal5307_xhd_water_bg_author_rtdl_gate_test.py
```

Summary:

```text
Runs author hd_exec and RTDL's generic Triton partner route on the Goal5306
bounded WaterBodies->BlockGroups WKT fixture. Author HDResult is
72.38665008544922; RTDL HDResult is 72.38664516014835; abs_diff is
4.925300871150284e-06 <= 1e-5. This is Level-B bounded same-fixture scalar
correctness only. It does not authorize exact paper input recovery, geo Figure
5 reproduction, author RT-core equivalence, performance ratio, or full paper
reproduction.
```

Expected review outcomes:

```text
approve_goals5306_5307_water_bg_bounded_author_rtdl_gate
revise_goals5306_5307_source_fixture_or_claim_boundary
block_goals5306_5307_due_to_invalid_author_rtdl_comparison_or_overclaim
```

## Goal5308 - X-HD Geo Exact / Full-Public Decision

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5308_xhd_geo_exact_full_public_decision_result_2026-07-09.md
history/internal_docs/call_for_review_goal5308_xhd_geo_exact_full_public_decision_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5308_geo_exact_full_public_decision_2026-07-09.json
tests/goal5308_xhd_geo_exact_full_public_decision_test.py
history/internal_docs/xhd_geo_level_b_bounded_packet_goals5302_5307_2026-07-09.md
```

Summary:

```text
Consolidates the geo WKT line after Goals5302-5307. Both Figure-5 WKT pair
names have bounded same-fixture scalar matches, but exact paper WKT files are
still unavailable locally and on the current POD. Paper-log point counts
(9.44M/43.95M and 22.82M/52.27M) are much larger than the bounded fixtures
(38K/50K and 124/894). Goal5308 keeps exact/Figure-5/full-paper/performance
claims blocked and authorizes a full-public ArcGIS point-count/MBR probe as the
next step.
```

Expected review outcomes:

```text
approve_goal5308_geo_exact_full_public_decision__bounded_not_figure5
revise_goal5308_due_to_missing_or_inaccurate_paper_log_provenance
block_goal5308_due_to_bounded_to_figure5_overclaim
```

## Goal5313 - X-HD WaterBodies/BG Author Config Alignment

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5313_xhd_water_bg_author_config_alignment_result_2026-07-09.md
history/internal_docs/call_for_review_goal5313_xhd_water_bg_author_config_alignment_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_n_points_cell_alignment_summary.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_author_water_bg_full_public_n_points_cell_8.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_witness_distance_probe.json
tests/goal5313_xhd_water_bg_n_points_cell_alignment_test.py
```

Summary:

```text
Explains the WaterBodies->BlockGroups mismatch from Goals5311-5312 as an
author configuration denominator issue. Paper-branch logs use
n_points_cell=8; Goal5311 used the author default n_points_cell=15. Rerunning
author hd_exec on the same full-public WKT candidate with -n_points_cell=8
reproduces the paper-log HDResult exactly. The RTDL exact-witness pair is
self-consistent in float64, and that same pair's float32 distance equals the
author/paper value.
```

Expected review outcomes:

```text
approve_goal5313_xhd_water_bg_author_config_alignment
revise_goal5313_due_to_insufficient_author_config_or_numeric_evidence
block_goal5313_due_to_overclaim_or_invalid_denominator
```

## Goal5314 - X-HD WaterBodies/BG Corrected Comparison Summary

Status:

```text
implemented_review_pending
```

Files:

```text
history/internal_docs/goal5314_xhd_water_bg_corrected_comparison_summary_result_2026-07-09.md
history/internal_docs/call_for_review_goal5314_xhd_water_bg_corrected_comparison_summary_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5314_water_bg_corrected_comparison_summary.json
tests/goal5314_xhd_water_bg_corrected_comparison_summary_test.py
```

Summary:

```text
Publishes the corrected WaterBodies->BlockGroups comparison layer. The valid
paper-log denominator is author hd_exec on the full-public WKT candidate with
n_points_cell=8, not the Goal5311 default n_points_cell=15 run. The RTDL
exact-witness float64 value differs from the author/paper float32 value by
1.305780185645311e-06, so the summary records an explicit 2e-6 tolerance
boundary. Goal5311 remains config-sensitivity evidence rather than being
deleted.
```

Expected review outcomes:

```text
approve_goal5314_xhd_water_bg_corrected_comparison_summary
revise_goal5314_due_to_bad_supersession_or_tolerance_boundary
block_goal5314_due_to_figure5_or_performance_overclaim
```
