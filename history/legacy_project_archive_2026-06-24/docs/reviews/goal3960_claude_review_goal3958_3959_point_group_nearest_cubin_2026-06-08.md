# Goal3960: Claude Review of Goal3958-3959 (Point-Group-Nearest CUBIN Hardening)

Date: 2026-06-08
Reviewer: Claude (independent read-only review)

## Scope

Reviewed commits:
- `57a27e52` Goal3958 harden point group nearest CUDA loaders
- `b820b986` Goal3959 refresh current scale after point group hardening

## Findings

### 1. CUBIN conversion correctness

`src/native/optix/rtdl_optix_workloads.cpp` converts exactly three direct CUDA
helper-module load sites (lines ~20344, ~20443, ~20564 post-change) from
`compile_to_ptx(...)` / `cuModuleLoadData(..., ptx.c_str())` to
`compile_to_cubin(...)` / `cuModuleLoadData(..., cubin.data())`:

- `g_point_group_nearest_split_columns` (`point_group_nearest_split_columns_kernel.cu`)
- `g_point_group_nearest_reduce` (`point_group_nearest_max_reduce_kernel.cu`), used
  in both the plain max-distance reduce and the active-frontier reduce reuse path

The `compile_to_cubin`/`cuModuleLoadData(..., cubin.data())` shape matches the
convention already used at numerous other converted sites in the same file
(e.g. lines 1331, 4699, 4855, 19058). **Verdict: accept.**

Note: all three converted sites pass `kPointGroupNearestMaxReduceKernelSrc` as
the CUDA source string — including the split-columns site, whose loaded entry
point is `split_point_group_nearest_columns`. This looks odd at first glance,
but it is **pre-existing** (confirmed via `git show 57a27e52^:...`, line 20344-20346
of the prior tree is identical apart from `compile_to_ptx`/`ptx.c_str()`):
the shared source string evidently contains both kernel functions, and the
`name` argument to `compile_to_cubin` is just a diagnostic label. Goal3958 did
not introduce or alter this; it is out of scope for this hardening goal.

### 2. OptiX RT pipeline PTX paths preserved

Confirmed all `kPointGroupNearestRtKernelSrc` / `kPointGroupThresholdRtKernelSrc`
call sites (lines 20079, 20168, 20245, 20334, 20433, 20544, 20554 in the new
tree) remain on `compile_to_ptx(...)` feeding `build_pipeline(...)` with their
respective raygen entry points (`__raygen__point_group_nearest_probe`,
`__raygen__point_group_threshold_probe`). The diff touches none of these.
**Verdict: accept.**

### 3. Goal3958 pod API smoke evidence

`goal3958_point_group_nearest_api_smoke.json`:
- `source_commit_short: "d9c736c5"`, `git_status_short: [" M ...rtdl_optix_workloads.cpp"]`
  — confirmed `d9c736c5` and `57a27e52^` (`372a391e`) have an *identical*
  `rtdl_optix_workloads.cpp` (`git diff d9c736c5 57a27e52^ -- ...` is empty), so
  applying the Goal3958 native patch on top of `d9c736c5` is equivalent to
  applying it on top of the true parent. This is valid evidence, not a stale
  baseline.
- `all_checks_pass: true`, and all seven named checks
  (`query_ids_match_raw_rows`, `neighbor_ids_match_raw_rows`,
  `distances_match_raw_rows`, `reduce_query/neighbor/distance_matches_raw_argmax`,
  `active_frontier_uses_device_reduction`) are `true`, exercising exactly the
  three claimed paths: split-columns helper (device-column query/neighbor/distance
  outputs vs. raw witness rows), max-reduce helper (argmax match), and the
  active-frontier reduce reuse (`native_reduction:
  "point_group_nearest_max_distance_active_frontier"`).
- `split_columns_kernel` / `reduce_kernel` fields name the two converted kernels
  explicitly, tying the smoke run to the converted code paths.
- All claim-authorization flags (`release_authorized`,
  `public_speedup_claim_authorized`, `broad_rt_core_claim_authorized`,
  `true_zero_copy_claim_authorized`, `paper_reproduction_claim_authorized`,
  `rt_core_speedup_claim_authorized`, `v2_6/v2_8_release_authorized`, etc.)
  are `false`. **Verdict: accept** — valid evidence for all three claimed paths.

### 4. Goal3951 inventory now reports 9 collect-k-only sites

The committed `goal3951_..._inventory_2026-06-08.md` table in `57a27e52` lists
exactly 9 remaining rows, all in `src/native/optix/rtdl_optix_api.cpp` and all
named `collect_k_*` kernels (lines 90, 3500, 3589, 3600, 3615, 3625, 3635, 4822,
6664). The three `point_group_nearest_*` rows were removed, the "Recommended
Migration Order" section was correctly updated to drop the now-obsolete
point-group-nearest step, and the Follow-Up note states the count is `9`. The
companion test `goal3951_direct_cuda_ptx_loader_debt_inventory_test.py` was
updated in lockstep (drops the three point-group-nearest entries from
`EXPECTED_DRIVER_LOADED_PTX_KERNELS`, adds them to the "must not remain" assertion
list). **Verdict: accept.**

(Note: the working tree currently has *further*, uncommitted edits to this same
inventory file reducing the count to `0` for a later "Goal3962" — that is
outside the scope of `57a27e52`/`b820b986` and does not affect this review;
flagging only so the next reviewer isn't confused by `git status` showing this
file as modified.)

### 5. Goal3959 clean current-scale packet

`goal3959_..._current_scale_clean_..._cubin.json`:
- `runtime_environment.source_commit_short: "57a27e52"`,
  `working_tree_clean: true`, `nvidia_smi` reports
  `NVIDIA RTX 4000 Ada Generation, 550.127.05, 20475 MiB` — a clean run from the
  pushed Goal3958 commit, as claimed.
- `all_pass: true`, `json_pass_count: 10`, `len(rows) == 10`,
  `validation.status: "accept"`.
- All 10 rows (`hausdorff_xhd_scale_default_optix_threshold`,
  `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default`,
  `rt_dbscan_optix_numba_scale_default_65536_no_validation`,
  `robot_collision_optix_scale_default_1024_no_probe_reference`,
  `contact_manifold_optix_scale_default_grid64`,
  `raydb_style_optix_count_scale_default_262k`,
  `barnes_hut_numba_scale_default_8192`,
  `librts_spatial_index_optix_scale_default_32768`,
  `rtnn_prepared_optix_scale_default_65536`,
  `triangle_counting_optix_rt_graph_2a1_scale_default_2048`) report
  `status: "pass"`, parseable stdout JSON, `claim_flag_violations: []`, and
  nonzero `stdout_bytes`. Top-level and `summary` claim-authorization flags
  (`release_authorized`, `public_speedup_claim_authorized`,
  `broad_rt_core_claim_authorized`, `paper_reproduction_claim_authorized`) are
  all `false`. **Verdict: accept** — valid clean-commit, all-pass evidence.

### 6. Claim-boundary scan

Both report markdown files (`goal3958_..._hardening_2026-06-08.md` and
`goal3959_..._hardening_2026-06-08.md`) explicitly state the standard "does not
authorize" boundary list (release, public speedup, whole-app acceleration,
broad RT-core, true-zero-copy, automatic partner/backend selection, AMD
performance, paper reproduction, package-install, app-specific native-engine
logic). No instance of any of these phrases appears in an authorizing context —
every occurrence in both files is inside a "remain unauthorized"/"does not
authorize" sentence. The smoke and current-scale JSON artifacts likewise carry
all relevant claim flags as `false`. **No accidental authorization found.**

### 7. Remaining direct CUDA loader debt

Per the updated (committed) Goal3951 inventory in `57a27e52`, the remaining
direct driver-loaded PTX debt is the 9 `collect_k_*` sites in
`src/native/optix/rtdl_optix_api.cpp` (lines 90, 3500, 3589, 3600, 3615, 3625,
3635, 4822, 6664), all flagged for conversion "as a cluster" due to historical
tuning branches. (The working tree currently shows uncommitted further work
reducing this to 0, attributed to a future "Goal3962" — not part of this
review's commits.)

## Overall Verdict

**accept**

The native diff is a narrow, mechanical PTX→CUBIN conversion limited to the
three named helper-module loaders, consistent with the established
`compile_to_cubin`/`cuModuleLoadData(..., cubin.data())` pattern elsewhere in
the file. The OptiX RT pipeline PTX paths that feed `build_pipeline` are
untouched. The pod smoke evidence exercises exactly the three converted paths
against raw-row ground truth, and the clean current-scale packet shows all 10
rows passing from the pushed commit with no claim-flag violations. The Goal3951
inventory and its test were updated in lockstep and now correctly report 9
remaining (collect-k-only) sites. No release/public-speedup/whole-app/broad
RT-core/true-zero-copy/AMD/paper-reproduction/package/automatic-partner-selection/
app-specific-engine claims were accidentally authorized anywhere in the chain.
