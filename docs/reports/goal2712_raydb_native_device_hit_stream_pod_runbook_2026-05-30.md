# Goal2712 - RayDB Native Device Hit-Stream Pod Runbook

Date: 2026-05-30

Status: runner prepared; execution requires an RTX pod.

## Purpose

Goal2710 wires RayDB's `paper_rt_optix_device_hit_stream_triton` mode to the
native OptiX device-column hit-stream producer. Goal2712 prepares the pod runner
so the next hardware session can compare the old host-row bridge and the new
native device-column bridge without editing code on the pod.

## Runner Update

Updated `scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py` to:

- print a start line before every warmup/repeat iteration;
- keep the existing per-iteration elapsed progress line;
- record `native_device_column_path_used`;
- record `host_row_bridge_bypassed`;
- record requested/selected gather partner;
- record the Goal2708 `torch_carrier_adapter` explanation;
- record neutral-buffer handoff summaries.

This keeps pod runs auditable: a result is not enough unless the artifact also
shows whether the path actually bypassed host hit rows.

## Dry Run

Windows dry run:

```text
py -3 scripts\goal2685_raydb_device_hit_stream_handoff_pod_runner.py \
  --dry-run \
  --row-counts 1000 \
  --modes count \
  --backends paper_rt_optix_hit_stream_triton,paper_rt_optix_device_hit_stream_triton \
  --output build\goal2712_dry_run.json

status: dry_run
git_head: 2c4ad1b6c1dc9801c450bdb27369c56cc43b79df
```

Local Linux dry run on `192.168.1.20`:

```text
HEAD: 02f86c6e972d580ff5ad489a26e5cc3f5617acaa
status: dry_run
nvidia_smi: NVIDIA GeForce GTX 1070, 580.126.09, 8192 MiB
```

## Pod Command

From a fresh pod checkout at current `origin/main`:

```bash
set -euo pipefail
cd /root/rtdl
git fetch origin main
git reset --hard origin/main

python3 -m pip install --break-system-packages numpy cupy-cuda12x torch triton
mkdir -p /root/vendor
test -d /root/vendor/optix-sdk || git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-sdk /root/vendor/optix-sdk
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk

export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so

python3 scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py \
  --row-counts 10000,100000,1000000 \
  --group-count 128 \
  --modes count,sum,min,max,avg_as_sum_count \
  --backends paper_rt_optix_hit_stream_triton,paper_rt_optix_device_hit_stream_triton \
  --repeats 3 \
  --warmup 1 \
  --output docs/reports/goal2712_raydb_native_device_hit_stream_pod.json
```

## Required Artifact Checks

The pod artifact should be considered useful only if all of these are true:

- `all_correct == true`;
- every `paper_rt_optix_device_hit_stream_triton` case has
  `native_device_column_path_used == true`;
- every device-column case has `host_row_bridge_bypassed == true`;
- every device-column case has `handoff_materializes_host_rows_for_bridge == false`;
- `torch_carrier_adapter.raw_cuda_adapter_required == true` for the
  device-column path;
- all public claim booleans remain false until reviewed.

## Boundary

This runbook is preparation, not evidence. A real RTX pod run is now the next
binding step for same-pointer/no-host-stage and performance claims.
