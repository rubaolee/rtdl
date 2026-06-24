# Goal1471 v1.5.3 Typed Host Reuse Benchmark

## Verdict

ACCEPTED.

## Scope

- Primitive: `COLLECT_K_BOUNDED`
- Surface: typed host input reuse plus prepared host output
- Backends: embree, optix
- Required backends: embree, optix
- Unique rows: 4096
- Repeats: 4
- Iterations: 20

## Pod Scope

- SSH target: `root@157.157.221.29`
- SSH port: `57142`
- SSH key used from Windows: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_pod`
- Source key copy origin: `Z:\rtdl-dev\id_ed25519_rtdl_codex`
- Pod checkout: `/root/rtdl_goal1467_pod`
- Git commit: `e9694e71`
- GPU: NVIDIA RTX 2000 Ada Generation
- Driver: `570.195.03`

## Results

- `embree`: baseline_materializations=20 typed_materializations=1 delta=19 baseline_total_s=0.311217 typed_total_s=0.104089 ratio=0.334459
- `optix`: baseline_materializations=20 typed_materializations=1 delta=19 baseline_total_s=0.306499 typed_total_s=0.104915 ratio=0.342302

## Boundary

This benchmark records wrapper-level input materialization counts and diagnostic timing for the accepted typed host path only. It does not authorize true zero-copy, public speedup wording, whole-app claims, stable primitive promotion, partner tensor handoff, or release action.
