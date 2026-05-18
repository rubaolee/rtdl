# Goal2348: RTNN External Runner For v2.2

Date: 2026-05-18

Status: implemented locally; pod execution pending

## Purpose

Add the first executable harness for the v2.2 RTNN nearest-neighbor campaign.
This is infrastructure for comparing RTDL against the open RTNN implementation
on the same hardware and generated inputs.

The harness does not change RTDL runtime behavior yet. It exists so the next
runtime extension is driven by measured evidence rather than intuition.

## What Landed

New script:

`scripts/goal2348_rtnn_v2_2_external_runner.py`

The script can:

- generate deterministic RTNN-format point-cloud text files (`x,y,z` per line);
- parse RTNN timing output lines such as `time search compute: ... ms`;
- patch a disposable external RTNN checkout for CUDA 12 compatibility;
- run an external RTNN `optixNSearch` binary with explicit radius/K/search
  policy metadata;
- run the current RTDL 2-D OptiX fixed-radius count-threshold smoke path when
  a built `librtdl_optix.so` is available;
- emit JSON artifacts with claim boundaries.

New test:

`tests/goal2348_rtnn_v2_2_external_runner_test.py`

## Claim Boundary

Goal2348 does not claim:

- full RTNN reproduction;
- RTDL speedup over RTNN;
- paper-dataset equivalence;
- broad RT-core speedup;
- that current RTDL already has the needed generic 3-D radius+K fast path.

The current RTDL smoke subcommand is intentionally labeled as a 2-D smoke row,
not paper-equivalent RTNN evidence.

## Example Local Smoke

```text
py -3 scripts\goal2348_rtnn_v2_2_external_runner.py generate \
  --point-file scratch\goal2348_smoke_points.txt \
  --point-count 5 \
  --dimension 3 \
  --seed 2348 \
  --json-out scratch\goal2348_smoke_generate.json
```

Result:

```text
generated.format = rtnn_csv_xyz
generated.point_count = 5
generated.dimension = 3
claim_boundary.paper_dataset = false
claim_boundary.synthetic_input_only = true
```

## Pod Usage

After cloning and building RTNN on an RTX pod:

```text
python3 scripts/goal2348_rtnn_v2_2_external_runner.py patch-rtnn-cuda12 \
  --rtnn-root scratch/rtnn_goal2346 \
  --json-out docs/reports/goal2348_rtnn_cuda12_patch.json

python3 scripts/goal2348_rtnn_v2_2_external_runner.py generate \
  --point-file scratch/goal2348_ppp_3d_262144.txt \
  --point-count 262144 \
  --dimension 3 \
  --seed 2348 \
  --json-out docs/reports/goal2348_ppp_3d_262144_generate.json

python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-rtnn \
  --rtnn-binary scratch/rtnn_goal2346/src/build/bin/optixNSearch \
  --rtnn-cwd scratch/rtnn_goal2346/src/build \
  --rtnn-library-dir scratch/rtnn_goal2346/src/build/lib \
  --point-file scratch/goal2348_ppp_3d_262144.txt \
  --search-mode radius \
  --radius 0.02 \
  --k-max 50 \
  --partition \
  --auto-batch \
  --approx-mode 0 \
  --row-label ppp_3d_radius_k50_partitioned \
  --json-out docs/reports/goal2348_rtnn_ppp_3d_radius_k50_partitioned.json
```

The first accepted comparison run must pair each RTNN row with a same-hardware
RTDL row and record whether the RTDL row is current-v2.1 2-D smoke evidence or
new v2.2 3-D bounded-neighbor evidence.

The CUDA 12 patch subcommand only edits an external RTNN checkout. It adds
missing Thrust includes and updates legacy NVRTC intrinsic names; it does not
change RTDL source or RTNN algorithms.

## Validation

Validated locally:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2348_rtnn_v2_2_external_runner_test \
  tests.goal2346_v2_2_rtnn_campaign_test \
  tests.goal2349_v2_2_rtnn_local_linux_optix_dev_test
```

Result:

```text
Ran 16 tests
OK
```

## Verdict

`accept-with-boundary`

The harness is ready for pod use. The RTDL runtime extension itself remains the
next engineering task.
