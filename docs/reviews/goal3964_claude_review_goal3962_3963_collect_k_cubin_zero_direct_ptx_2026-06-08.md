# Goal3964: Claude Review of Goal3962-3963 (Collect-K CUBIN / Zero Direct PTX)

Date: 2026-06-08
Reviewer: Claude (read-only independent review)

## Scope

Independent review of:
- `b745a7e5` Goal3962 harden collect-k CUDA loaders
- `11638bff` Goal3963 refresh current scale after collect-k hardening

## Verdict

`accept`

## Findings

### 1. Collect-K loader conversion to `compile_to_cubin` + `cuModuleLoadData(..., cubin.data())`

Confirmed correct. The diff in `b745a7e5` for `src/native/optix/rtdl_optix_api.cpp`
converts all nine call sites that previously did
`compile_to_ptx(...)` / `cuModuleLoadData(&module, ptx.c_str())` for the seven
listed collect-k kernels (note `collect_k_bounded_i64_row_width2_sort_kernel.cu`
and `collect_k_bounded_i64_row_width2_final_compact_kernel.cu` each load from two
sites) to `compile_to_cubin(...)` / `cuModuleLoadData(&module, cubin.data())`.
Verified directly:

- `grep -n "ptx.c_str()" src/native/optix/rtdl_optix_api.cpp` → no matches.
- `grep -n "cuModuleLoadData" src/native/optix/rtdl_optix_api.cpp` → all nine
  sites now end in `cubin.data()`.
- `compile_to_cubin` is a real, pre-existing helper
  (`rtdl_optix_core.cpp:368`) distinct from `compile_to_ptx`
  (`rtdl_optix_core.cpp:384`), so this is a genuine driver-loader migration, not
  a rename-only change.

### 2. Cooperative-launch smoke RDC-option drop

Confirmed correct and supported by pod evidence, with one minor evidence-trail
gap. The diff drops `{"--relocatable-device-code=true"}` from the
`compile_to_cubin` call for `collect_k_cooperative_launch_smoke_kernel.cu`
(`rtdl_optix_api.cpp:84-89`), and `compile_to_cubin`'s `extra_opts` defaults to
empty, so the CUBIN path now compiles without RDC. The pod API smoke
(`goal3962_collect_k_api_smoke.json`) shows `cooperative_smoke.all_checks_pass:
true`, `status: 0`, `observed_blocks: 2`, `sync_observed_blocks: 2`,
`error: ""` — i.e. the non-RDC CUBIN path loads and launches correctly.

The minor gap: the report (`goal3962_..._hardening_2026-06-08.md:28`) asserts
"the pod retry showed CUBIN plus that option produced an invalid driver image."
The only archived retry artifact
(`goal3962_collect_k_cubin_retry_driver.log`, and the identical
`goal3962_collect_k_api_smoke.stdout.log`) records the **successful** non-RDC
retry only — there is no archived log of the failing RDC+CUBIN attempt (e.g. a
`CUDA_ERROR_INVALID_IMAGE` trace). The empirical conclusion (drop RDC; the
non-RDC CUBIN loads and launches) is independently verified by the passing
smoke, so this does not change the verdict, but the specific causal claim about
*why* rests on an unarchived observation rather than a captured artifact.

### 3. Goal3951 inventory now reports zero remaining direct PTX sites

Confirmed. The updated `goal3951_..._inventory_2026-06-08.md` table now reads
`| none | - | - | - |` and states "current remaining driver-loaded PTX count is
`0`". Independent verification by re-running the scanner's logic by hand:

- `grep -n "cuModuleLoadData" src/native/optix/rtdl_optix_api.cpp` → all nine
  results end in `cubin.data()`.
- `grep -n "cuModuleLoadData" src/native/optix/rtdl_optix_workloads.cpp` → all
  nineteen results end in `cubin.data()`.
- `grep -c "ptx.c_str()" src/native/optix/rtdl_optix_{api,workloads}.cpp` → zero
  in both files.

The scanner pattern (`cuModuleLoadData` + `ptx.c_str()` co-occurring on a line)
correctly returns an empty tuple, matching the updated
`EXPECTED_DRIVER_LOADED_PTX_KERNELS: tuple[str, ...] = ()` in
`tests/goal3951_direct_cuda_ptx_loader_debt_inventory_test.py`. OptiX pipeline
PTX (`compile_to_ptx` calls feeding `optixModuleCreate`/pipeline construction in
`rtdl_optix_workloads.cpp`) remains untouched and out of scope, consistent with
the report's framing — those are not driver `cuModuleLoadData` loads of raw PTX.

### 4. Goal3962 pod API smoke coverage

Confirmed. `goal3962_collect_k_api_smoke.json` covers all four claimed paths:

- `row_width2_small_bitonic`: pass, 1024 unique rows, all four checks true,
  all claim flags false.
- `row_width2_tiled_cub_merge_final`: pass, 8192 unique rows (exercises the CUB
  tile-sort / merge / final-compact cluster), all checks true.
- `dynamic_row_width3_fallback`: pass, 257 unique rows, row width 3 (the
  single-thread fallback path), all checks true.
- `cooperative_smoke`: pass, `status: 0`, 2 observed / 2 synchronized blocks,
  empty error string.

`source_commit_short: e704d1d8` plus `git_status_short: [" M
src/native/optix/rtdl_optix_api.cpp"]` confirms this smoke ran from the clean
parent commit with only the Goal3962 native patch applied — an appropriate
isolation for attributing the result to this change. All claim-authorization
flags (`release_authorized`, `public_speedup_claim_authorized`,
`broad_rt_core_claim_authorized`, `true_zero_copy_claim_authorized`,
`paper_reproduction_claim_authorized`) are `false`, matching the report and the
test assertions in `goal3962_..._test.py::test_collect_k_pod_api_smoke_passed`.

### 5. Goal3963 clean current-scale packet

Confirmed valid evidence. `goal3963_..._current_scale_clean....json` shows:

- `runtime_environment.source_commit_short: "b745a7e5"` (the Goal3962 commit,
  pushed),
- `runtime_environment.working_tree_clean: true`,
- `nvidia_smi`: `NVIDIA RTX 4000 Ada Generation, 550.127.05, 20475 MiB`,
- `all_pass: true`, `json_pass_count: 10`, 10 rows total,
- `validation.status: "accept"`,
- every row has `status: "pass"` and an empty
  `semantic_stdout_check.claim_flag_violations` list (independently verified —
  all ten `"claim_flag_violations": []` occurrences are present, one per row),
- top-level `release_authorized`, `public_speedup_claim_authorized`,
  `broad_rt_core_claim_authorized`, `paper_reproduction_claim_authorized` are
  all `false`.

This matches the report table and the assertions in
`tests/goal3963_..._test.py`.

### 6. Claim-boundary discipline

No accidental authorization found. Both report files explicitly disclaim
release, public-speedup, whole-app-acceleration, broad-RT-core,
true-zero-copy, AMD-performance, paper-reproduction, package-install,
automatic-partner-selection, and app-specific native-engine wording. The pod
smoke JSON and the current-scale JSON both carry `claim_boundary` strings and
per-flag `false` values that are consistent with this. Spot-checked the
`prepared_session_residency_summary` and other embedded sub-reports inside the
Goal3963 packet — they likewise carry `..._authorized: false` flags and
`internal_*_not_release_authorization` status strings. Nothing in this chain
crosses a claim boundary.

### 7. Remaining direct CUDA PTX-loader debt

None remains under the Goal3951 tracked scanner. Independent re-derivation
(item 3 above) confirms zero `cuModuleLoadData(..., ptx.c_str())` sites in
either `rtdl_optix_api.cpp` or `rtdl_optix_workloads.cpp`. OptiX pipeline PTX
compilation (feeding `optixModuleCreate`, not raw driver `cuModuleLoadData`)
remains in place by design and is correctly excluded from this debt
classification — that is a different, intentional loading mechanism, not
leftover debt from the same migration effort.

## Boundary

This review is read-only analysis of internal compatibility-hardening work. It
does not authorize release, public-speedup wording, whole-app acceleration
wording, broad RT-core wording, true-zero-copy wording, AMD performance
wording, paper-reproduction wording, package-install wording, automatic
partner/backend selection, or app-specific native-engine claims.
