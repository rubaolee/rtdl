# Goal3518: v2.8 Benchmark Matrix Refresh

Date: 2026-06-05

Status: internal matrix refresh; not a release packet.

## Purpose

Refresh the v2.8 benchmark-app matrix so reviewers and users can see, in one place, how each promoted benchmark app is currently meant to run:

- `primitive_only`: the recommended path is a generic RTDL primitive or fused native reduction.
- `partner_needed`: the recommended path requires an explicit user-visible partner continuation.
- `prepared_execution_needed`: the app needs the prepared-execution workflow: prepare/cache, warm, steady-state run, and explain timings.

This report deliberately does not authorize release, public speedup wording, whole-app speedup wording, broad RT-core wording, true-zero-copy wording, paper reproduction claims, hidden partner selection, hidden dispatch, full RayJoin overlay completion claims, or app-specific native-engine behavior.

## Source Of Truth

New code source:

- `src/rtdsl/v2_8_benchmark_matrix.py`
- `tests/goal3518_v2_8_benchmark_matrix_test.py`

Primary evidence sources:

- Goal2654 accepted 10-app comparison refresh
- Goal2797-2803 seven-app current packet
- Goal2965 RayDB primitive-first same-contract decision gate
- Goal3143/3160 Hausdorff partner/front-door evidence
- Goal3151 v2.8 front-door adoption audit
- Goal3443, Goal3492, Goal3509, Goal3511, and Goal3517 RayJoin overlay prepared-execution chain

## Current Matrix

All cells are filled. When a phase is not available from the source artifact, the cell says why instead of using a bare placeholder.

| App | Row | Class | Partner | Setup sec/status | Warmup sec/status | Steady sec | Correctness | Claim boundary |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- |
| hausdorff_xhd | hausdorff_xhd_exact_rt_nearest_witness | primitive_only | none on the promoted RT-core path; Numba exact partner front door remains a separate fallback/reference | not_separately_recorded_in_goal2801; one RTDL warmup captures first-run setup | 0.896931632 | 0.007444375 | matches exact CuPy grid baseline with zero distance error | no claim to beat X-HD or optimized CuPy grid |
| spatial_rayjoin | spatial_rayjoin_count_parity_prepared | prepared_execution_needed | none for the scalar count/parity path | 0.000174500 | two warmup repeats recorded by Goal2799, not reported as one aggregate | 0.000161098 | all three count/parity rows match CPU references | count/parity only; not full RayJoin paper reproduction or full overlay |
| spatial_rayjoin | spatial_rayjoin_overlay_area_exact_prepared | prepared_execution_needed | CuPy for the exact-area tile-task continuation | 0.192737129 | 0.386260449 | 0.069889469 | matches Shapely/GEOS total within 1e-8; 1086 positive rows observed | no RayJoin reproduction, no rtdl-beats-RayJoin, and no full overlay-geometry claim |
| rt_dbscan | rt_dbscan_grouped_stream_components | partner_needed | CuPy for component continuation | not_separately_recorded_in_goal2802; tail median excludes whole packet orchestration | not separately reported in Goal2802 current packet | 0.302337887 | grouped stream signature matches prepared CuPy grid signature | no IPDPS paper reproduction or broad DBSCAN speedup claim |
| robot_collision | robot_collision_prepared_anyhit_pose_flag | prepared_execution_needed | none | legacy_total_only_from_goal2654; current v2.8 phase refresh still needed | legacy_total_only_from_goal2654 | 0.001614130 | accepted app-level parity evidence from Goal2654 | Tier-C/no-regression style evidence; no public speedup claim |
| contact_manifold | contact_manifold_prepared_witness_collection | primitive_only | none on the accepted current path | legacy_total_only_from_goal2654; current v2.8 phase refresh still needed | legacy_total_only_from_goal2654 | 0.018476400 | accepted app-level parity evidence from Goal2654 | Tier-C/no-regression style evidence; no public speedup claim |
| raydb_style | raydb_style_count_primitive_first | primitive_only | none; Triton hit-stream path is deliberately not promoted for fused scalar reductions | same-contract gate reports prepared primitive median; setup excluded by gate contract | not separately reported in Goal2965 gate | 0.000459385 | all count comparisons pass | internal decision gate only; no public speedup claim |
| raydb_style | raydb_style_sum_primitive_first | primitive_only | none; Triton hit-stream path is deliberately not promoted for fused scalar reductions | same-contract gate reports prepared primitive median; setup excluded by gate contract | not separately reported in Goal2965 gate | 0.002161583 | all sum comparisons pass | internal decision gate only; no public speedup claim |
| barnes_hut | barnes_hut_membership_plus_vector_sum | partner_needed | CuPy selected for vector sum by measured same-contract timing | frontier lowering is included in the largest-case total; vector partner timing is separate | vector warmups recorded as two repeats, not reported as one aggregate | 18.033107738 | rows match between Embree and OptiX; first case reference-validated | no author-code comparison, no paper reproduction, no automatic Triton selection |
| librts_spatial_index | librts_prepared_aabb_index_query | prepared_execution_needed | none | 0.408870804 | three warmups per query row, not reported as one aggregate | 0.001551950 | all query counts match CPU reference | Tier-C/no-regression harness; no partner or public RT claim |
| rtnn | rtnn_ranked_summary_cuda_graph | prepared_execution_needed | none on the promoted RTDL path; CuPy grid remains same-contract opponent | 1.940580351 | nine steady runs reported; warmup not reported as one aggregate | 0.017263921 | ranked aggregate matches CuPy grid for all distributions | Tier-B same-contract opponent; no claim to beat RTNN paper |
| triangle_counting | triangle_counting_generic_rt_summary | primitive_only | none required on the fastest primitive row | 0.001550044 | not separately aggregated in Goal2797 | 0.000413392 | triangle count matches oracle in every row | canonical harness only; no public speedup claim |

## What This Says

The matrix is now complete at the promoted-app level: all 10 benchmark apps are represented, and multi-contract apps are split into explicit rows instead of being collapsed into one vague cell.

The strongest v2.8 pattern is prepared execution. Spatial RayJoin overlay now has a clear prepared path:

1. Load prepared binary payload cache: `0.192737129` sec.
2. Warm the active relation stream: `0.386260449` sec across three calls.
3. Run steady state as relation stream plus planner plus executor: `0.0038709240034222603 + 0.05171292740851641 + 0.014305617660284042 = 0.069889469` sec.
4. Validate against Shapely/GEOS: `0.268093143` sec.

The matrix also preserves the current weak spots:

- `robot_collision` and `contact_manifold` still rely on accepted Goal2654 total timing, not fresh v2.8 split timing.
- `rt_dbscan` has a strong grouped-stream tail number, but preparation/warmup are not separately exposed by Goal2802.
- `barnes_hut` has a large total row because the measured path includes frontier lowering and membership; the vector partner timing is already separated.

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal3518_v2_8_benchmark_matrix_test
Ran 5 tests in 0.001s
OK
```

The test enforces:

- all 10 promoted apps are covered;
- all three classes are used;
- every timing-status cell is explicit;
- the RayJoin overlay and Hausdorff rows are present;
- all release, speedup, RT-core, zero-copy, paper-reproduction, and app-specific-engine flags remain false.

## Next Pod Refresh

The next pod run should not be a blind full packet. It should target the matrix gaps:

1. refresh `robot_collision` with phase-separated setup/warmup/steady timing;
2. refresh `contact_manifold` with phase-separated setup/warmup/steady timing;
3. refresh `rt_dbscan` with preparation/warmup separated from grouped-stream tail timing;
4. optionally rerun the full 12-row matrix on current HEAD after those gaps are closed.
