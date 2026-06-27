# Goal 191 Report: v0.3 Comprehensive Verification

## Outcome

Completed.

This goal executed the final bounded pre-release verification sweep for the `v0.3`
line across:

- early workload/runtime surfaces
- backend/runtime slices
- bounded visual-demo entrypoints

The sweep deliberately excluded expensive Windows HD rerenders and instead used small
artifacts and direct smoke execution where they materially verified the current path.

## Verification Slice

### 1. Core workload and language/runtime slice

Command:

- `PYTHONPATH=src:. python3 -m unittest tests.test_core_quality tests.rtdsl_language_test tests.rtdsl_simulator_test tests.baseline_integration_test tests.goal10_workloads_test tests.goal110_segment_polygon_hitcount_closure_test tests.goal138_polygon_pair_overlap_area_rows_test tests.goal140_polygon_set_jaccard_test tests.goal146_jaccard_backend_surface_test tests.rtdsl_ray_query_test`

Result:

- `Ran 141 tests in 0.053s`
- `OK`
- `2 skipped`

Coverage represented:

- language core lowering and semantics
- early workload surface
- segment/polygon hitcount
- polygon overlap rows
- polygon-set Jaccard
- ray/triangle hitcount
- baseline integration paths

### 2. Backend/runtime and bounded 3D slice

Command:

- `PYTHONPATH=src:. python3 -m unittest tests.rtdsl_embree_test tests.rtdsl_vulkan_test tests.goal43_optix_validation_test tests.goal162_visual_demo_test tests.goal162_optix_visual_demo_parity_test tests.goal164_spinning_ball_3d_demo_test tests.goal166_orbiting_star_ball_demo_test tests.goal178_smooth_camera_orbit_demo_test tests.goal179_smooth_camera_linux_backend_test tests.goal187_v0_3_audit_test`

Result:

- `Ran 71 tests in 8.576s`
- `OK`
- `18 skipped`

Coverage represented:

- Embree runtime
- Vulkan runtime
- OptiX validation path
- bounded 3D spinning-ball support
- bounded visual demo wrappers
- bounded moved visual-demo path audit

### 3. Direct visual-demo smoke execution

Commands:

- `python3 examples/visual_demo/rtdl_lit_ball_demo.py --backend cpu_python_reference --compare-backend cpu_python_reference --width 24 --height 24 --triangles 24 --output build/goal191_direct_smoke/lit_ball.ppm`
- `python3 examples/visual_demo/rtdl_orbit_lights_ball_demo.py --backend cpu_python_reference --compare-backend cpu_python_reference --width 24 --height 24 --triangles 24 --frames 2 --vertical-samples 24 --output-dir build/goal191_direct_smoke/orbit_lights`
- `python3 examples/visual_demo/rtdl_orbiting_star_ball_demo.py --backend cpu_python_reference --compare-backend cpu_python_reference --width 20 --height 20 --latitude-bands 6 --longitude-bands 12 --frames 2 --jobs 1 --show-light-source --temporal-blend-alpha 0.10 --phase-mode uniform --output-dir build/goal191_direct_smoke/orbit`
- `python3 examples/visual_demo/rtdl_smooth_camera_orbit_demo.py --backend cpu_python_reference --compare-backend cpu_python_reference --width 20 --height 20 --latitude-bands 6 --longitude-bands 12 --frames 2 --jobs 1 --temporal-blend-alpha 0.10 --phase-mode uniform --output-dir build/goal191_direct_smoke/smooth`

Result:

- all four commands completed successfully
- bounded image/video artifacts were written under:
  - `/Users/rl2025/rtdl_python_only/build/goal191_direct_smoke/`

## Failure Found During The Sweep

One real release-gate issue surfaced:

- `tests.goal162_visual_demo_test` still imported:
  - `examples.rtdl_orbit_lights_ball_demo`
- `tests.goal162_optix_visual_demo_parity_test` also imported the old flat path

Fix applied:

- both tests now import:
  - `examples.visual_demo.rtdl_orbit_lights_ball_demo`

Additional direct-execution fixes were already carried through earlier in the Goal 190 line:

- `examples/visual_demo/rtdl_lit_ball_demo.py`
- `examples/visual_demo/rtdl_orbit_lights_ball_demo.py`

both now restore `REPO_ROOT` / `src` bootstrap for direct CLI execution from the new directory.

## Pass / Skip / Failure Accounting

- passed tests:
  - `141 + 71 = 212`
- skipped tests:
  - `2 + 18 = 20`
- failed tests at final state:
  - `0`
- fixed blockers found during the sweep:
  - `1`

## Deferred / Bounded Exclusions

- no long Windows HD rerenders
- no new large production video generation
- no release packaging yet

These exclusions were intentional and consistent with Goal 191 scope.

## Conclusion

Goal 191 succeeded as a bounded but comprehensive pre-release verification pass.
The final repo shape now has fresh evidence across:

- early workloads
- language/runtime lowering
- CPU / Embree / OptiX / Vulkan bounded paths
- the reorganized `examples/visual_demo/` application layer

The sweep also served its intended release-gate function by catching and fixing a stale
post-reorganization test import before release.
