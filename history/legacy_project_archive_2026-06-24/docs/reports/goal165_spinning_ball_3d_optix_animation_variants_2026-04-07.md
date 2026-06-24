# Goal 165 Report: Spinning-Ball 3D OptiX Animation Variants

## Decision

Three named spin-speed animation variants for the 3D spinning-ball demo have
been validated on Linux with OptiX, with per-frame parity against
`cpu_python_reference` confirmed clean across all frames and all variants.

## What Was Run

Variants:

| Variant        | spin_speed | Description                               |
|----------------|-----------|-------------------------------------------|
| `current_spin` | 1.1       | Default demo speed — ball rotates ~1.1 turns over full phase |
| `slower_spin`  | 0.35      | Perceptibly slower; surface detail more visible |
| `no_spin`      | 0.0       | Static surface; only lights animate       |

Runner script:

- `examples/rtdl_goal165_optix_animation_variants.py`

## Linux Environment

- Host: `lestat@192.168.1.20`
- Working directory: `/home/lestat/work/rtdl_python_only`
- OptiX backend: built via `make build-optix`

## Two-Tier Run Design

### Tier 1: Parity (64×64, 4 frames, OptiX vs cpu_python_reference)

Parameters:

- resolution: 64 × 64
- latitude bands: 12
- longitude bands: 24
- frame count: 4 per variant
- backend: `optix`
- compare backend: `cpu_python_reference`
- triangle count: 528

Results:

| Variant        | Parity per frame        | All ok | query_share | total_query_s |
|----------------|------------------------|--------|-------------|---------------|
| `current_spin` | `[true, true, true, true]` | true | 0.3192 | 0.0878 |
| `slower_spin`  | `[true, true, true, true]` | true | 0.2920 | 0.0765 |
| `no_spin`      | `[true, true, true, true]` | true | 0.3038 | 0.0811 |

**Parity tier overall status: PASS**

### Tier 2: Full-Resolution Animation (192×192, 8 frames, OptiX only)

Parameters:

- resolution: 192 × 192
- latitude bands: 32
- longitude bands: 64
- frame count: 8 per variant
- backend: `optix`
- no comparison (parity already confirmed in tier 1)
- triangle count: 3968

Results:

| Variant        | query_share | total_query_s | total_shading_s |
|----------------|-------------|---------------|-----------------|
| `current_spin` | 0.705       | 7.823         | 3.270           |
| `slower_spin`  | 0.706       | 7.823         | 3.255           |
| `no_spin`      | 0.703       | 7.736         | 3.264           |

PPM frame sequences written to:

```
build/goal165_optix_variants/fullres_192x192/current_spin/
build/goal165_optix_variants/fullres_192x192/slower_spin/
build/goal165_optix_variants/fullres_192x192/no_spin/
```

Each sequence contains `frame_000.ppm` through `frame_007.ppm`.

## Key Observations

### Parity is clean across all three variants

All 12 per-frame parity checks (3 variants × 4 frames each) returned `true`.
This confirms that the spin-phase parameter does not affect row-level parity —
RTDL computes the same ray/triangle hit counts regardless of the scene's
rotation animation state.

### Query share at full resolution is dominant

At 192×192 with 3968 triangles, the RTDL OptiX query work accounts for
approximately 70–71% of total frame time. The remaining ~29% is Python-side
shading. This confirms the intended split: RTDL is the heavy runtime
component and Python handles surrounding application logic.

### Spin speed does not affect hit-count correctness

The three variants differ only in the `spin_phase` parameter passed to the
Python-side shading functions. The RTDL ray/triangle input set (rays from
the pinhole camera and the sphere triangle mesh) is identical across variants.
This is expected: spin_phase is purely a shading argument.

## Honest Boundary

This goal validates animation parameter variants on the existing 3D backend
line. It does not:

- change the RTDL runtime or backend code
- claim new workload types or language features
- claim video encoding (PPM frame sequences are the artifact)
- claim that the 192×192 OptiX timing is a calibrated performance number
  (it includes Python-side CPU overhead not separated from OptiX dispatch)

## Conclusion

Goal 165 closes the OptiX animation variant validation slice:

- three named spin-speed variants (`current_spin`, `slower_spin`, `no_spin`)
- Linux OptiX backend
- clean per-frame parity on all 12 frames in the parity tier
- 192×192 full-resolution PPM sequences as visual artifacts
- RTDL query share at ~70% of full-resolution frame time
