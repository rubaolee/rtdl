# Goal1472 v1.5.3 Typed Host Reuse Sweep

## Verdict

ACCEPTED.

## Scope

- Primitive: `COLLECT_K_BOUNDED`
- Surface: typed host input reuse plus prepared host output
- Backends: embree, optix
- Required backends: embree, optix

## Pod Scope

- SSH target: `root@157.157.221.29`
- SSH port: `57142`
- SSH key used from Windows: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_pod`
- Source key copy origin: `Z:\rtdl-dev\id_ed25519_rtdl_codex`
- Pod checkout: `/root/rtdl_goal1467_pod`
- Git commit: `0ebedf95262ed67e2513ac7ebd2379be5555509d`
- GPU: NVIDIA RTX 2000 Ada Generation
- Driver: `570.195.03`

## Results

- Case unique_rows=1024 repeats=4 iterations=20 accepted=True
- `embree`: rows=4096 baseline_materializations=20 typed_materializations=1 delta=19 baseline_total_s=0.081592 typed_total_s=0.026687 ratio=0.327082
- `optix`: rows=4096 baseline_materializations=20 typed_materializations=1 delta=19 baseline_total_s=0.071991 typed_total_s=0.024989 ratio=0.347111
- Case unique_rows=4096 repeats=4 iterations=20 accepted=True
- `embree`: rows=16384 baseline_materializations=20 typed_materializations=1 delta=19 baseline_total_s=0.307135 typed_total_s=0.102431 ratio=0.333506
- `optix`: rows=16384 baseline_materializations=20 typed_materializations=1 delta=19 baseline_total_s=0.307785 typed_total_s=0.105681 ratio=0.343359
- Case unique_rows=16384 repeats=2 iterations=12 accepted=True
- `embree`: rows=32768 baseline_materializations=12 typed_materializations=1 delta=11 baseline_total_s=0.546157 typed_total_s=0.238802 ratio=0.437241
- `optix`: rows=32768 baseline_materializations=12 typed_materializations=1 delta=11 baseline_total_s=0.560822 typed_total_s=0.245063 ratio=0.436971

## Boundary

This sweep records wrapper-level input materialization counts and diagnostic timing across multiple typed-host benchmark sizes. It does not authorize true zero-copy, public speedup wording, whole-app claims, stable primitive promotion, partner tensor handoff, or release action.
