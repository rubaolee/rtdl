# Goal 163 Report: OptiX Correctness Reaudit

## Decision

Current `main` passes a bounded OptiX correctness reaudit on the accepted
historical OptiX test surface after the visual-demo hitcount parity repair.

## Fresh Linux Reaudit

Environment:

- host: `lestat@192.168.1.20`
- fresh clone directory:
  - `/home/lestat/work/rtdl_v03_optix_audit`
- audited commit:
  - `a44ef2e`

Preparation:

- `git clone ... /home/lestat/work/rtdl_v03_optix_audit`
- `git checkout a44ef2e`
- `make build-optix`

## Reaudited OptiX Test Modules

The Linux reaudit reran this bounded historical OptiX-related slice:

- `tests.goal43_optix_validation_test`
- `tests.goal44_optix_benchmark_test`
- `tests.goal45_optix_county_zipcode_test`
- `tests.goal47_optix_goal41_large_checks_test`
- `tests.goal65_vulkan_optix_linux_comparison_test`
- `tests.goal99_optix_cold_prepared_run1_win_test`
- `tests.goal110_baseline_runner_backend_test`
- `tests.goal110_segment_polygon_hitcount_closure_test`
- `tests.goal146_jaccard_backend_surface_test`
- `tests.optix_embree_interop_test`
- `tests.goal162_optix_visual_demo_parity_test`

Result:

- `55` tests
- `OK`

## Visual-Demo Post-Fix Smoke Rerun

Command:

```bash
cd /home/lestat/work/rtdl_v03_optix_audit
PYTHONPATH=src:. python3 examples/rtdl_orbit_lights_ball_demo.py \
  --backend optix \
  --compare-backend cpu \
  --width 96 \
  --height 96 \
  --triangles 1024 \
  --frames 4 \
  --vertical-samples 4 \
  --output-dir build/goal163_optix_visual_smoke
```

Observed result:

- all `4` frames reported `matches: true` against CPU
- total query time:
  - `0.3524457230232656 s`
- total shading time:
  - `0.3101279080437962 s`
- query share:
  - `0.5319344243381052`

## What Was Fixed

The bug was in the OptiX `ray_tri_hitcount` line exposed by the new visual demo.

Concrete pre-fix symptom:

- one failing frame had a row mismatch such as:
  - CPU `504`
  - OptiX `505`

Current code change:

- `src/native/rtdl_optix.cpp`
- `tests/goal162_optix_visual_demo_parity_test.py`

## Honest Boundary

The repair is correctness-first.

Current accepted meaning:

- OptiX now returns parity-clean accepted rows for the reaudited
  `ray_tri_hitcount` visual-demo surface
- but the fix currently uses a full exact host-side replacement of the final
  hit counts after the OptiX execution for `ray_tri_hitcount`

So this is:

- a correct accepted result path

and not yet:

- a claim of fully native-only OptiX closure for every internal step of that
  workload

## Conclusion

The bounded historical OptiX surface is now back in an acceptable state on
current `main`:

- fresh Linux clone
- build succeeds
- historical OptiX unittest slice passes
- visual-demo smoke parity is clean

That is enough to say the specific correctness regression was real, fixed, and
retested across the known OptiX-facing task surface.
