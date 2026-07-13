# X-HD Paper Reproduction App

This directory tracks the RTDL paper-reproduction line for:

```text
X-HD: Fast Hausdorff Distance Computation with Ray Tracing
ICS 2026
DOI: https://doi.org/10.1145/3797905.3800509
Author code: https://github.com/pwrliang/X-HD
```

## Paper And Artifact

Author homepage / paper page:

```text
https://gengl.me/publications/ics26/
```

Pinned public source snapshot used for the initial audit:

```text
repository: https://github.com/pwrliang/X-HD.git
branch: main
commit: 7bf41c8442d059c94f4178355c6d5a10571d9658
commit_date: 2026-06-13 16:59:42 -0400
```

The author executable described by the repository README is:

```text
./bin/hd_exec \
  -input1 <path> \
  -input2 <path> \
  -n_dims <2|3> \
  -input_type <image|wkt|ply|off> \
  -variant <eb|nn|itk|clover|rt> \
  -execution <cpu|gpu> \
  -json <summary.json>
```

`variant=rt` is the X-HD algorithm in the paper.

The RTDL paper app now provides an app-owned entrypoint with the same key flags:

```text
python Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  -input1 <path> \
  -input2 <path> \
  -n_dims <2|3> \
  -input_type <wkt|ply|off> \
  -variant <eb|nn|itk|clover|rt> \
  -execution <cpu|gpu> \
  -json <summary.json> \
  --rtdl-route <auto|public-columnar|cell-mbr-fast-scalar|cell-mbr-exact-witness>
```

This runner writes `HDResult` and `Running` fields in an author-compatible JSON
shape, but the route is explicitly labeled under `RTDL.route_label`. `HDResult`
uses the proven author contract: directed `input1 -> input2`. The runner does
not claim author RT-core algorithm equivalence or performance parity.

Variant handling is deliberately value-oriented:

```text
variant=rt:
  RTDL computes the directed HDResult with an explicitly labeled RTDL route.
  This is still not author RT-core kernel or performance equivalence.

variant=eb|nn|itk|clover:
  RTDL accepts the author-style flag and returns a directed HDResult using the
  selected generic RTDL route. This is value-compatible output only; the
  author's variant-specific algorithm and timing denominator are not reproduced.
```

## RTDL Program

Existing RTDL Hausdorff/X-HD-style assets already exist under:

```text
examples/current/research_benchmarks/hausdorff_xhd/
```

Important current routes:

- exact CPU/OpenMP and CUDA/CuPy witness baselines;
- `rtdl_rt_threshold_search`: prepared fixed-radius decision search;
- `rtdl_rt_nearest_witness`;
- grouped nearest-witness routes;
- seeded/pruned and active-frontier X-HD-style routes;
- device-column / Numba argmax witness route.

These are not yet a paper app. They are benchmark/research assets that must be
connected to the pinned author artifact and same-input comparators before any
X-HD paper reproduction claim.

## App-Owned Code

App-owned pieces for this paper line:

- author `hd_exec` build/run wrapper;
- paper dataset provenance and workload selection;
- WKT/PLY/image fixture preparation;
- author JSON parser and comparator;
- exact Hausdorff tolerance policy;
- performance-regime selection and fair matrix.

These pieces are not RTDL language features.

## Reproduction Scope

Current status:

```text
xhd_same_input_directed_hdresult_reproduction_complete__externally_reviewed_and_approved
```

The owner-approved completion criterion is now deliberately scoped:

```text
same input files -> same directed input1-to-input2 HDResult within tolerance
```

Goal5451 closes that criterion with seven primary matched cases across a
directed-definition fixture, public graphics, bounded geo, and full-public geo.
Its machine-readable packet is:

```text
results/xhd_goal5451_same_input_hdresult_closeout.json
```

External review:

```text
history/internal_docs/review_goal5451_xhd_same_input_hdresult_closeout_verified_2026-07-10.md
verdict = approve_goal5451_xhd_same_input_directed_hdresult_closeout
```

This does not claim recovery of the original paper input bytes, reproduction of
all paper figures, author internal worklist/hash parity, author RT-core
algorithm equivalence, or performance parity/speedup. The previous external
artifact search is retained as provenance history but is no longer an active
blocker for this owner-approved scope.

This is stronger than the original bounded same-input completion, but it is
still not an all-artifact/all-figure X-HD paper result. The current strongest user-facing RTDL
entrypoint evidence is:

```text
script = scripts/run_xhd_rtdl_hd_exec.py
batch_bridge = scripts/run_xhd_rtdl_hd_exec_summary_batch.py
route_label = cell-mbr-exact-witness
dataset_contract = public ModelNet40 pair identities represented in the paper-branch log index
case_count = 400
matched_case_count = 400
failed_case_count = 0
max_author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = true for all 400 cases
```

Primary user-entrypoint evidence:

```text
results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json
results/xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json
results/xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json
results/xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json
```

The all-400 ModelNet40 evidence is public-data author-rerun evidence. It does
not prove exact original paper byte-input identity and does not reproduce all
paper datasets or figures.

The same `hd_exec`-compatible RTDL entrypoint also covers the full-public
Stanford Graphics Dragon -> HappyBuddha Level-B representative pair:

```text
input1 = data/external/stanford/dragon_recon/dragon_vrip.ply
input2 = data/external/stanford/happy_recon/happy_vrip.ply
preprocessing = translate_each_input_to_min_bound
author rerun HDResult = 0.12572988867759705
RTDL HDResult = 0.12572988629271128
abs_diff ~= 2.38e-9

fast scalar route:
  artifact = results/xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json
  route_label = cell-mbr-fast-scalar
  per_source_witness_exact = false
  RTDL route wall ~= 536.22 ms

exact witness route:
  artifact = results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json
  route_label = cell-mbr-exact-witness
  per_source_witness_exact = true
  RTDL route wall ~= 620.92 ms
```

This is same-source/public representative evidence for a graphics workload. It
still does not prove exact paper byte-input identity or author RT-core algorithm
equivalence.

The same entrypoint also covers the Stanford Graphics Dragon -> AsianDragon
scaled same-source candidate:

```text
input1 = data/external/stanford/dragon_recon/dragon_vrip.ply
input2 = data/external/stanford/asian_dragon_scaled_1e-3.ply
preprocessing = translate_each_input_to_min_bound
author rerun HDResult = 0.06536787003278732
paper log HDResult = 0.06536811590194702
RTDL HDResult = 0.06536787240753439
author_abs_diff ~= 2.37e-9
rtdl_vs_paper_log_abs_diff ~= 2.43e-7

exact witness route:
  artifact = results/xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json
  route_label = cell-mbr-exact-witness
  per_source_witness_exact = true
  RTDL route wall ~= 2651.05 ms
```

This is useful Level-B same-source/scaled-candidate evidence and closes another
graphics pair through the user-facing entrypoint. The paper-log drift is kept
visible because it is the fingerprint that this is not exact paper byte-input
identity.

The same entrypoint now also covers ThaiStatuette -> HappyBuddha:

```text
input1 = data/external/stanford/thai_statuette_scaled_1e-3.ply
input2 = data/external/stanford/happy_recon/happy_vrip.ply
preprocessing = translate_each_input_to_min_bound
paper log HDResult = 0.21912434697151184
author rerun HDResult = 0.21912431716918945
RTDL HDResult = 0.2191243235042005
author_abs_diff ~= 6.34e-9
rtdl_vs_paper_log_abs_diff ~= 2.35e-8

exact witness route:
  artifact = results/xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json
  route_label = cell-mbr-exact-witness
  per_source_witness_exact = true
  RTDL route wall ~= 5013.23 ms
```

ThaiStatuette is a public Stanford XYZRGB source candidate scaled by the
app-owned `1e-3` preprocessing step to match the paper-log coordinate scale.
The scaled candidate is Level-B evidence only; it does not prove exact paper
byte-input identity.

The same scaled ThaiStatuette candidate now also covers ThaiStatuette -> AsianDragon:

```text
input1 = data/external/stanford/thai_statuette_scaled_1e-3.ply
input2 = data/external/stanford/asian_dragon_scaled_1e-3.ply
preprocessing = translate_each_input_to_min_bound
paper log HDResult = 0.28763845562934875
author rerun HDResult = 0.28763842582702637
RTDL HDResult = 0.2876384148709406
author_abs_diff ~= 1.10e-8
rtdl_vs_paper_log_abs_diff ~= 4.08e-8

exact witness route:
  author artifact = results/xhd_goal5266_author_thai_asian_scaled_rt_gpu_pod.json
  artifact = results/xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json
  route_label = cell-mbr-exact-witness
  per_source_witness_exact = true
  RTDL route wall ~= 10770.02 ms
```

This is another Level-B same-source/scaled-candidate graphics gate through the
user-facing entrypoint. It is still not exact paper byte-input identity, not
author RT-core algorithm equivalence, and not performance parity.

Current strongest representative route status:

```text
Level B same-source full-public Dragon -> HappyBuddha
source points = 437645
target points = 543652
author HDResult = 0.12572988867759705
RTDL route distance = 0.12572988629271128
author_abs_diff ~= 2.38e-9
current best RTDL route wall ~= 1.17-1.18s
current best load_full_inputs ~= 0.68s
current best full gate total ~= 2.06s
explicit warmup measured route ~= 0.626s (warmup cost reported separately)
```

This route uses generic RTDL grid/cell-MBR/frontier/inline-nearest machinery
with a dense-lookup local-grid seed, `max_inline_points=512`,
payload-current-best pruning inside the native inline-nearest traversal, and
intersection-stage pruning before `optixReportIntersection` when the payload
current best already excludes a cell. Goal5202 adds generic packed coordinate
matrix reuse for seed and frontier front doors; Goal5203 changes the app-owned
PLY input front door to load directly into NumPy coordinate matrices instead of
materializing Python tuple rows first; Goal5204 replaces the generic
max-nearest reducer's full-row lexsort with finite max plus tie-only lexsort;
Goal5205 changes the app-owned ASCII PLY matrix loader to use NumPy column
loading, reducing user-visible public-input loading while leaving the route
algorithm unchanged. It is not exact paper dataset reproduction, not full paper
reproduction, and not an author-vs-RTDL performance ratio.

First target:

```text
bounded_same_input_author_json_gate
```

The first executable goal built and ran the author `hd_exec` on a tiny
same-input fixture and compared:

- `HDResult`;
- the directed `input1 -> input2` Hausdorff reference used by the author
  executable;
- input point counts and dimensionality;
- author JSON phase fields such as `Running.AvgTime` and `Running.Repeats`;
- tolerance against RTDL exact witness output.

Current bounded packet:

```text
data/fixtures/tiny2d_a.wkt
data/fixtures/tiny2d_b.wkt
data/fixtures/tiny2d_expected.json
data/fixtures/directed2d_asymmetric_a.wkt
data/fixtures/directed2d_asymmetric_b.wkt
scripts/run_xhd_author_json_gate.py
results/tiny2d_local_reference_summary.json
results/tiny2d_author_gate_summary_pod.json
results/tiny2d_author_hd_exec_output_pod.json
results/directed2d_asymmetric_author_gate_summary_pod.json
results/directed2d_asymmetric_author_hd_exec_output_pod.json
results/xhd_author_build_patch_goal5112.diff
```

The POD author summary is bounded same-input evidence:

```text
author_hd_result = 1.0
author_comparison_reference = directed_a_to_b
author_comparison_reference_value = 1.0
abs_diff = 0.0
tolerance = 1e-9
matched = true
```

A second bounded 10x9 WKT fixture also matched:

```text
fixture = bounded2d
author_hd_result = 2.0
author_comparison_reference = directed_a_to_b
author_comparison_reference_value = 2.0
abs_diff = 0.0
tolerance = 1e-6
matched = true
```

A directed-asymmetric 2D fixture was added to make the author directed
`input1 -> input2` contract behaviorally distinguishable from a symmetric
Hausdorff max:

```text
fixture = directed2d_asymmetric
author_hd_result = 0.5
author_comparison_reference = directed_a_to_b
author_comparison_reference_value = 0.5
exact_reference.directed_b_to_a = 9.0
exact_reference.hausdorff = 9.0
matched = true
```

A third bounded 3D 9x8 WKT fixture also matched:

```text
fixture = bounded3d
author_hd_result = 2.0
author_comparison_reference = directed_a_to_b
author_comparison_reference_value = 2.0
abs_diff = 0.0
tolerance = 1e-6
matched = true
```

The paper app now has bounded 2D and 3D RTDL routes:

```text
script = scripts/run_xhd_rtdl_route_gate.py
route = rtdl_numpy_columns_2d
author_hd_result = 2.0
author_comparison_reference = directed_a_to_b
author_comparison_distance = 2.0
exact_reference.hausdorff = 2.0
abs_diff = 0.0
tolerance = 1e-6
matched = true

route = rtdl_numpy_columns_2d
fixture = directed2d_asymmetric
author_hd_result = 0.5
author_comparison_reference = directed_a_to_b
author_comparison_distance = 0.5
exact_reference.hausdorff = 9.0
abs_diff = 0.0
tolerance = 1e-6
matched = true

route = rtdl_numpy_columns_3d
author_hd_result = 2.0
author_comparison_reference = directed_a_to_b
author_comparison_distance = 2.0
exact_reference.hausdorff = 2.0
abs_diff = 0.0
tolerance = 1e-6
matched = true
```

These routes use RTDL public columnar Hausdorff APIs inside the paper app:
`point_rows_to_numpy_columns` / `directed_hausdorff_2d_numpy_columns` for 2D,
and `point_rows_to_numpy_columns_3d` /
`directed_hausdorff_3d_numpy_columns` for 3D. They do not claim the author X-HD
RT-core algorithm or any performance result.

Exact paper byte-inputs were not available in the author checkout or on the
current POD. Author experiment logs reference external paths under
`/local/storage/shared/HDDatasets`, but that data root was absent in the
available environment. Later goals acquired same-source/public representative
inputs such as Stanford Graphics meshes and public ModelNet40 OFF files, and
those have separate author-rerun/RTDL gates. These representative results do not
prove exact paper byte-input identity.

The author binary required a build-compatibility patch for the current POD
toolchain: OptiX headers were pinned to v7.7.0 for the driver ABI, and three
Thrust `transform_reduce` lambdas were wrapped with explicit CCCL return-type
declarations. This is recorded as an `Author+BuildPatch` route, not raw author
source execution.

## Performance Scope

No author-vs-RTDL performance claim is authorized for this bounded closeout.

The bounded phase matrix is:

```text
results/xhd_bounded_performance_matrix_2026-07-08.json
```

It separates author `Running.AvgTime`, author process wall, and RTDL local route
timing. It intentionally reports no speedup or parity ratio because the
denominators and hardware do not align.

Current all-400 ModelNet40 user-entrypoint performance matrix:

```text
results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json

RTDL hd_exec route-wall sum = 420.31053318828344 s
RTDL hd_exec batch case-wall sum = 600.8750001639128 s
Author process-wall sum = 255.03741998970509 s
Author internal Running.AvgTime sum = 2794.7910000000006 ms

RTDL route / author process-wall = 1.648034759782505x slower
RTDL route / author internal AvgTime = 150.3906850953375x slower
```

The two ratios above use different denominators and must remain labeled. The
author internal `Running.AvgTime` ratio is a phase/algorithm gap warning, not a
fair user-facing process-wall comparison. The matrix does not claim speedup,
performance parity, exact paper byte-input identity, or full paper reproduction.

Future performance matrices must separate:

- author loading/preprocessing;
- author BVH/grid setup;
- author `ReportedTime` / `Running.AvgTime`;
- RTDL prepare/setup;
- RTDL exact witness or threshold query;
- host output/comparator work;
- cold process vs warm long-lived process.

Current Level-B route accounting:

```text
Goal5191 best route:
  local-grid seed + native inline-nearest max_inline_points=512
  frontier_rows = 0
  route_wall ~= 3.65s

Goal5192 telemetry:
  inline_cell_hit_count = 12,003,138
  inline_point_evaluation_count = 1,242,677,739

Goal5193 no-go:
  grid-cell-budget seed variants matched but did not beat local-grid
  inline320/384/448 matched but did not beat inline512

Goal5194 payload current-best pruning:
  native any-hit now prunes later cells using the updated payload nearest state
  warmed no-telemetry route_wall median ~= 3.46s
  telemetry inline point evals: 1.24B -> 0.40B

Goal5195 intersection-stage current-best pruning:
  native intersection skips optixReportIntersection for cells already excluded
  by payload current best in inline-nearest/no-pruned-row mode
  warmed route_wall ~= 2.6s
  native frontier / inline stage ~= 0.93-0.94s

Goal5196 local-grid dense lookup:
  local-grid / budget / branch-bound seed helpers now use a dense encoded-cell
  -> compact-cell lookup table when grid volume is below a safe cap, with
  binary-search fallback for large grids
  full-public route_wall ~= 2.26s
  local-grid seed ~= 0.55s
  budget1/budget2 and branch-bound dense variants matched but did not beat
  dense local-grid

Goal5197 intersection attribute + lazy row distance:
  native intersection passes min_sq to any-hit via OptiX attributes, and any-hit
  computes row-only min/max distances lazily only when a row is emitted
  full-public route remains matched at about 2.25-2.28s
  treated as a generic cleanup / neutral optimization, not a new speedup
  headline

Goal5198 grid-shape telemetry:
  24^3 fails the empty-frontier route with 155,511 attempted rows at capacity 0
  32^3 remains the current default: route ~= 2.24s, inline evals ~= 400.6M
  48^3 / 64^3 / 128^3 reduce point evals but increase seed and cell-hit cost
  route walls worsen to ~= 3.16s / 6.76s / 10.72s
  conclusion: simple grid-shape tuning is a no-go for this route

Goal5199 trace-tmax bound:
  tested bounding the generic OptiX cell-MBR ray tmax by radius or initial
  current-best distance plus epsilon
  matched author HDResult, but inline cell hits and point evals were unchanged
  final2 route ~= 2.32s vs current best ~= 2.24-2.28s
  conclusion: trace-tmax tuning is a no-go; the temporary code change was
  reverted and the 32^3 default route remains unchanged

Goal5200 native CUDA local-grid seed:
  implemented an explicit experimental generic native CUDA executor for the
  local-grid nearest-state seed
  same-POD control auto/Numba route ~= 2.258s, seed ~= 0.563s
  same-POD native_cuda route ~= 2.436s, seed ~= 0.958s
  conclusion: native CUDA seed is correct but slower for the current route;
  keep the default local-grid seed executor as auto/Numba

Goal5201 cell-MBR frontier native phase timing:
  added diagnostic native phase timings for the generic 3-D cell-MBR
  nearest-frontier collector
  warm diagnostic route ~= 2.229s, still matched author HDResult
  route-level frontier_rows ~= 0.920s
  native frontier total ~= 0.600s
  native OptiX launch / inline nearest work ~= 0.377s
  native accel build ~= 0.0004s
  conclusion: prepared cell-MBR accel build is not the next target; the next
  generic target is inline-nearest execution / work ordering or device-resident
  front-door state, not accel-build caching

Goal5202 packed coordinate matrix reuse:
  added a generic coordinate_matrix / coordinate_matrix_fields point-column
  convention and made the local-grid seed plus native cell-MBR frontier helpers
  reuse it
  full-public route still matched author HDResult
  matrix reuse flags are true for seed query/target and frontier query/target
  no-timing route_wall ~= 2.027s
  same-POD Goal5200 auto/Numba control route_wall ~= 2.258s
  conclusion: this removes repeated front-door coordinate packing and is the
  previous best route-local Level-B RTDL result

Goal5203 NumPy matrix input loader:
  keeps the old row-based loader for bounded/reference gates, but loads the
  hot full-public PLY route directly into NumPy coordinate matrices
  full-public route still matched author HDResult
  route_wall ~= 1.238-1.239s
  source+target column construction: ~= 0.535s -> ~= 0.001-0.002s
  load_full_inputs: ~= 2.518s -> ~= 1.681s
  conclusion: this removes tuple-row / matrix repacking at the app input
  front door and is the previous best route-local Level-B RTDL result

Goal5204 linear max-nearest reduction:
  changes generic max_nearest_distance_witness_numpy_columns from full-array
  lexsort to finite max plus tie-only lexsort, with non-finite fallback
  full-public route still matched author HDResult
  max_nearest_reduction ~= 0.072s -> ~= 0.0007-0.0008s
  route_wall ~= 1.17-1.18s
  conclusion: this removes the small generic max-reducer floor and is the
  current best route-local Level-B RTDL result

Goal5205 fast ASCII PLY matrix loader:
  changes the app-owned PLY matrix loader from Python per-line split/float
  parsing to np.loadtxt(max_rows=vertex_count, usecols=coordinate_indices)
  full-public route still matched author HDResult
  load_full_inputs ~= 1.69s -> ~= 0.68s
  route_wall remains ~= 1.16-1.17s
  full gate total ~= 3.08-3.09s -> ~= 2.06s
  conclusion: this reduces user-visible input loading, not the route-local
  algorithmic floor

Goal5206/Goal5207 warm-regime accounting:
  Goal5206 diagnoses first-use vs same-process warm behavior
  Goal5207 adds --route-warmup-source-limit to record warmup separately
  explicit all-source warmup case_total ~= 1.389s
  measured warm route_wall ~= 0.626s
  measured warm case_total ~= 0.809s
  total including load + warmup + measured ~= 2.893s
  conclusion: warm route numbers are valid only with their warmup/preparation
  cost and must not replace the fresh one-shot route headline
```

The telemetry run explains the remaining native inline-nearest floor, but it
uses atomic counters and is diagnostic. It must not replace the no-telemetry
route as the performance route, and it does not authorize an author-vs-RTDL
performance ratio.

Goal5201 phase timing is also diagnostic. It is used to choose the next generic
system target, not to claim a new performance headline. Goal5202, Goal5203,
Goal5204, and Goal5205 are route-local / app-front-door improvements, but
still do not authorize an author-vs-RTDL performance ratio.

The current default route is 32^3 dense-lookup local-grid-cell plus inline512
plus payload-current-best pruning, intersection-stage current-best pruning,
intersection attribute min-distance reuse, lazy row distance computation, and
empty-frontier passthrough.

## Boundary

Not claimed:

- full X-HD paper reproduction;
- exact paper dataset reproduction;
- author performance parity;
- whole-program speedup;
- universal Hausdorff acceleration;
- that existing `hausdorff_xhd` benchmark results are paper reproduction results.

The app may reuse existing RTDL Hausdorff assets, but any paper claim must go
through the author artifact comparator.
