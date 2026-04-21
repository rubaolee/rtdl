# Goal667: Apple RT Visibility-Count Closure

Date: 2026-04-20

Status: accepted current-main closure

## Scope

Goal667 closes the Apple RT prepared/prepacked 2D visibility-count work after
source restoration. The implementation is a current-main app path for repeated
Mac visibility/collision queries:

- build a prepared Apple RT 2D triangle-prism scene once
- prepack a reusable 2D ray buffer once
- execute repeated scalar blocked-ray count queries without materializing
  per-ray Python dictionaries

This is not a full emitted-row speedup claim and not a DB/graph Apple
ray-tracing-hardware claim.

## Source Changes

- Restored source-level native exports:
  - `rtdl_apple_rt_prepare_ray_anyhit_2d`
  - `rtdl_apple_rt_run_prepared_ray_anyhit_2d`
  - `rtdl_apple_rt_profile_prepared_ray_anyhit_2d`
  - `rtdl_apple_rt_count_prepared_ray_anyhit_2d`
  - `rtdl_apple_rt_destroy_prepared_ray_anyhit_2d`
- Restored Python public helpers:
  - `rt.prepare_apple_rt_ray_triangle_any_hit_2d(...)`
  - `rt.prepare_apple_rt_rays_2d(...)`
  - `PreparedAppleRtRayTriangleAnyHit2D.run(...)`
  - `PreparedAppleRtRayTriangleAnyHit2D.run_profile(...)`
  - `PreparedAppleRtRayTriangleAnyHit2D.count_profile(...)`
  - packed variants for repeated-query use
- Added release-facing example:
  - `examples/rtdl_apple_rt_visibility_count.py`

## Performance Evidence

Regenerated after rebuilding `build/librtdl_apple_rt.dylib` from current
source:

- Report:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal666_mac_visibility_count_perf_2026-04-20.md`
- Host:
  Apple M4, macOS 26.3, Embree 4.4.0
- Method:
  backend-agreement correctness; repeated-query medians with setup costs
  reported separately

Key repeated-query medians:

| Case | Apple RT packed count | Embree row count | Shapely/GEOS count |
| --- | ---: | ---: | ---: |
| dense blocked, 32768 rays / 8192 triangles | 0.001330064 s | 0.015297282 s | 0.297816304 s |
| mixed visibility, 32768 rays / 8192 triangles | 0.001182773 s | 0.015251223 s | 0.252873766 s |
| sparse clear, 32768 rays / 8192 triangles | 0.000910397 s | 0.014742673 s | 0.196451636 s |

Correct claim:

Apple RT is faster in this harness for the scalar blocked-ray count contract
when the scene and rays are reusable/prepacked.

Incorrect claim:

Apple RT beats Embree for full emitted rows, broad Apple RT workloads, DB
workloads, graph workloads, or non-macOS hosts.

## Public Docs Updated

Updated front-facing docs to expose the example and boundary:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/current_main_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`

## Verification

Commands run:

```bash
make build-apple-rt
PYTHONPATH=src:. python3 -m unittest -v tests.goal603_apple_rt_native_contract_test tests.goal578_apple_rt_backend_test tests.goal651_apple_rt_3d_anyhit_native_test tests.goal659_mac_visibility_collision_perf_test tests.goal652_apple_rt_2d_anyhit_native_test
PYTHONPATH=src:. python3 examples/rtdl_apple_rt_visibility_count.py
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
PYTHONPATH=src:. python3 -m unittest -v tests.goal515_public_command_truth_audit_test tests.goal513_public_example_smoke_test tests.goal646_public_front_page_doc_consistency_test tests.goal645_v0_9_5_release_package_test
PYTHONPATH=src:. build/goal659_shapely_venv/bin/python scripts/goal666_mac_visibility_count_perf.py --warmups 1 --repeats 3 --target-sample-seconds 2.0 --oracle-mode backend_agreement
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
git diff --check
```

Results:

- Focused Apple RT/backend tests: 23 tests OK
- Example output: `blocked_ray_count=2`, `clear_ray_count=2`
- Public command truth audit: valid true, 250 commands, 14 docs
- Public front-page/doc tests: 11 tests OK
- Full local discovery: 1243 tests OK, 180 skips
- `git diff --check`: clean

## AI Review

Claude review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal667_claude_apple_rt_visibility_count_release_review_2026-04-20.md`
- Verdict: PASS
- Non-blocking observation:
  current 2D count path uses `MPSIntersectionTypeNearest` rather than a
  lower-level true any-hit kernel. This is semantically correct for counting
  blocked rays and is a future optimization opportunity, not a release blocker.
  The observation is now reflected in the support matrix, backend maturity
  page, and Apple RT support notes.

Codex verdict:

ACCEPT. The implementation, performance report, docs, and review evidence are
consistent with the narrow scalar blocked-ray count claim.
