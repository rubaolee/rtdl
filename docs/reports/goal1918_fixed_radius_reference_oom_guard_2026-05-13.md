# Goal1918 - Fixed-Radius Reference OOM Guard

Status: pod-blocker-fix-ready

Date: 2026-05-13

## Context

The first Goal1913 run on the RTX pod reached the Goal1903 fixed-radius batch
after successful local preflight, partner probing, OptiX build, and focused
tests. It completed the torch fixed-radius rows and the cupy size-4096 row, but
failed on the optional dense cupy partner-reference baseline for size 16384.

The failure was:

`cupy.cuda.memory.OutOfMemoryError: Out of memory allocating 2,147,483,648 bytes`

The failing path was the dense all-pairs reference inside
`event_hotspot_flags_partner_columns`, not the v2 native OptiX partner-device
path.

## Fix

Goal1903 now passes the existing Goal1878 `--max-reference-pairs` option with a
default cap:

`FIXED_RADIUS_MAX_REFERENCE_PAIRS=50000000`

Large dense Torch/CuPy reference rows are therefore recorded as skipped instead
of exhausting GPU memory. The v1.8 host-packed, v1.8 prepared, v2 native, and
v2 prepared native OptiX rows still run.

## Boundary

This is a pod-run stability fix. It does not relax parity, provenance, RTX, or
claim-boundary gates, and it does not authorize release wording.
