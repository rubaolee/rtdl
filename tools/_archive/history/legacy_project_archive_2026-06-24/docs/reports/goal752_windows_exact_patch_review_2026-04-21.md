# Goal752 Windows Exact Patch Review Reply

## Verdict

ACCEPT.

Windows Codex reviewed the exact patch bundle from `ed205eb` through `f25d69a`, applied it cleanly to a scratch checkout, ran feasible Windows checks, and found no blocking issue. The earlier Goal749 stale-origin limitation is resolved by this patch-bundle review: I could inspect the exact Goal748/750/751 code, tests, harness, reports, and docs even though the commits are not yet on GitHub `origin/main`.

Windows Codex did not push and did not commit.

## Checkout / Patch Application Notes

- Base checkout used for scratch review: `C:\Users\Lestat\rtdl_goal752_patch_review`
- Base commit before patch: `ed205eb472ad8b097993f93d0abc2ca65c754e11`
- Patch bundle: `Z:\extra-1\rtdl_codex_bridge\to_windows\GOAL752_MAC_LINUX_OPTIX_FIX_EXACT_PATCH_BUNDLE.patch`
- Patch range reviewed:
  - `4471cd3 Record Windows post-Embree bridge validation`
  - `cb42f4f Add scaled OptiX robot performance harness`
  - `2283013 Fix OptiX short-ray any-hit reporting`
  - `b0cedf8 Fix OptiX short segment-polygon reports`
  - `152c3ce Record Gemini consensus on OptiX interval fixes`
  - `f25d69a Record Goal748 robot OptiX erratum`
- `git apply --check` passed.
- `git apply` passed.
- Changes were left as uncommitted scratch working-tree changes in the review checkout only.

## Tests Run And Results

PASS:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m py_compile scripts/goal748_optix_robot_scaled_perf.py tests/goal748_optix_robot_scaled_perf_test.py tests/goal751_robot_optix_erratum_doc_test.py tests/goal637_optix_native_any_hit_test.py tests/goal671_optix_prepared_anyhit_count_test.py tests/goal110_segment_polygon_hitcount_closure_test.py
```

PASS, 8 tests:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest -v tests.goal748_optix_robot_scaled_perf_test tests.goal751_robot_optix_erratum_doc_test tests.goal510_app_perf_doc_refresh_test
```

PASS with native OptiX unavailable on Windows host, 17 tests / 9 skipped:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest -v tests.goal637_optix_native_any_hit_test tests.goal671_optix_prepared_anyhit_count_test tests.goal110_segment_polygon_hitcount_closure_test
```

The short-ray and short-segment native tests skipped because this Windows host does not have native OptiX available. Portable prepared-count fallback tests, CPU tests, and Embree tests passed.

PASS:

```powershell
git diff --check
```

PASS, 9 tests:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest -v tests.goal511_feature_guide_v08_refresh_test tests.goal526_v0_8_public_doc_stale_phrase_test tests.goal751_robot_optix_erratum_doc_test tests.goal510_app_perf_doc_refresh_test
```

PASS:

```powershell
$env:PYTHONPATH='src;.'
py -3 scripts/goal497_public_entry_smoke_check.py
```

Result: JSON reported `"valid": true`.

PASS:

```powershell
$env:PYTHONPATH='src;.'
py -3 scripts/goal515_public_command_truth_audit.py
```

Result: JSON reported `"valid": true`, `command_count: 248`, `public_doc_count: 14`.

PASS, direct Goal748 harness smoke with CPU and Embree rows:

```powershell
$env:PYTHONPATH='src;.'
$env:RTDL_EMBREE_PREFIX='C:\Users\Lestat\vendor'
$env:RTDL_VCVARS64='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat'
$env:PATH='C:\Users\Lestat\vendor\bin;' + $env:PATH
py -3 scripts/goal748_optix_robot_scaled_perf.py --backend cpu_rows --backend embree_rows --pose-count 4 --obstacle-count 2 --repeats 1 --warmups 0
```

Result: `cpu_rows` and `embree_rows` both reported `hit_edge_count: 3`, `matches_oracle: true`, `row_count: 16`.

One non-result note: I initially tried two stale/incorrect module names based on shorthand in the Mac/Linux status (`tests.goal511_release_docs_goal509_boundary_test` and `tests.goal526_v08_current_scope_docs_test`). They failed with `ModuleNotFoundError`. I then listed the real test files and reran the actual modules above, which passed.

## Findings

### No P0/P1 Findings

No correctness blocker was found in the exact patch.

### P2 Notes

1. Native OptiX could not be executed on Windows.

   The review confirms the source/test logic and runs portable Windows checks, but the new short-ray and short-segment OptiX regression tests skip on this host because native OptiX is unavailable. This is expected for the Windows worker role as stated in Goal749/752. Linux validation remains the execution authority for native OptiX traversal.

2. The Goal748 harness validates hit-count parity, not full row identity, for cross-backend performance summaries.

   This is acceptable for the stated robot hit-edge count and prepared scalar-count purpose. The harness clearly labels row backends as `per_ray_dict_rows` and prepared count as `native_scalar_hit_edge_count`, and it separates CPU oracle validation from backend timing. Future witness-row claims should keep using row-level tests or add a row-identity check.

## Required Review Checks

### 1. Exact Patch Bundle Inspected

Yes. I inspected the patch bundle directly and applied it to a scratch checkout. This resolves the Goal749 stale-origin limitation.

### 2. OptiX Interval-Local Fix Semantics

ACCEPT.

The two risky sites fixed by the patch are exactly the ones with normalized directions and short world-space trace intervals:

- 2D ray/triangle any-hit: raygen normalizes `(dx, dy)` and traces with `tmax = r.tmax * len`.
- segment/polygon hitcount: raygen normalizes the segment direction and traces with `tmax = len`.

Replacing fixed `optixReportIntersection(0.5f, 0u)` with:

```cpp
float hit_t = optixGetRayTmin() + 1.0e-6f;
if (hit_t > optixGetRayTmax()) hit_t = optixGetRayTmax();
optixReportIntersection(hit_t, 0u);
```

is semantically correct for these any-hit/count-only workloads. The predicate has already decided whether a hit exists; the reported `t` is not used as a closest-hit distance or as public output. It only needs to lie inside the OptiX ray interval so the any-hit program is invoked.

### 3. Regression Tests

ACCEPT.

The new tests are targeted and would catch the old fixed-`0.5f` bug on a native OptiX machine:

- `test_optix_native_any_hit_2d_matches_cpu_for_short_rays` uses a `0.25`-length vertical ray that should hit a triangle. The old `t=0.5` report lies outside the trace interval.
- `test_prepared_anyhit_count_matches_cpu_for_short_rays` protects the prepared scalar count path with the same short-ray shape.
- `test_optix_matches_python_reference_for_short_segment_inside_polygon` uses a segment from `(0.1, 0.1)` to `(0.35, 0.1)` inside a polygon, so old `t=0.5` would be outside `tmax=len=0.25`.

These are small, direct, and regression-focused.

### 4. Goal748 Harness

ACCEPT.

The harness cleanly separates:

- deterministic case construction;
- optional CPU oracle validation;
- row backends (`cpu_rows`, `embree_rows`, `optix_rows`);
- OptiX prepared scalar count (`optix_prepared_count`);
- `prepare_scene_sec`;
- `prepare_rays_sec`;
- backend execution timing;
- row materialization versus scalar output shape;
- GTX 1070 / RTX RT-core claim boundary.

The JSON artifacts also preserve those boundaries. The large no-oracle run is honestly labeled with oracle validation disabled, while still comparing backend hit counts against each other.

### 5. Public-Doc Erratum

ACCEPT.

The Goal751 erratum correctly marks old Goal509 OptiX robot evidence as superseded/suspect after the short-ray bug, without weakening CPU/Embree evidence incorrectly. The wording in README, docs index, support matrix, tutorial, release-facing examples, examples README, and the Goal509 report distinguishes:

- CPU/Embree robot evidence remains usable.
- Old pre-fix Goal509 OptiX robot evidence is suspect/superseded.
- Goal748 post-fix parity/timing should be used for current OptiX robot discussion.
- GTX 1070 timing is traversal/whole-call evidence only, not RTX RT-core speedup evidence.

The new Goal751 doc tests cover the public-doc erratum and the old Goal509 report qualification.

### 6. Portable Windows Checks

Completed as listed above. Native OptiX could not run and skipped, as expected. Portable harness/doc/public checks passed.

## Earlier Goal749 Limitation

Resolved. Goal749 was limited because the later Mac/Linux commits were not available from GitHub `origin/main`. Goal752 provided the exact patch bundle, and Windows applied/reviewed that bundle directly.

## Windows Codex File Changes

Windows Codex did not modify mainline source or push/commit anything.

Files written outside the scratch checkout:

- `Z:\extra-1\rtdl_codex_bridge\from_windows\GOAL752_WINDOWS_EXACT_PATCH_REVIEW_REPLY.md`
- `Z:\extra-1\rtdl_codex_bridge\status\windows_codex_status.md`

Scratch checkout changes were produced only by applying the provided patch bundle to `C:\Users\Lestat\rtdl_goal752_patch_review` for review.

## Final Recommendation

Proceed with the patch series. The interval-local fixes are correct for the reviewed any-hit/count-only paths, the regression tests are targeted, the Goal748 harness is fit for RTX follow-up validation, and the public-doc erratum is appropriately scoped.
