# Goal2911: Scale-Stable Canonical Performance Rows

Date: 2026-05-31
Status: implemented with pod evidence

## Purpose

Goal2910 showed that repeat-9 helped, but two packet rows were still too small to serve as serious v2.5 performance gates:

- Hausdorff at 4K points per side: low single-millisecond timing, `1.171x` RTDL/CuPy in one packet
- RTNN uniform at 32K points: sub-0.1ms timing, `0.940x` CuPy/RTDL in one packet

Those rows are useful smoke tests, but they are not good benchmark gates for the project principle that benchmark apps should exercise meaningful RT/partner work. Goal2911 moves the canonical defaults to more stable sizes.

## Pod Probe

Artifact directory:

`docs/reports/goal2911_scale_probe_pod/`

Clean source metadata:

- source commit: `1e3c98ffa76e602959f943a83e79fb5b442d9cd1`
- source dirty: none
- GPU: `NVIDIA RTX A5000, 570.211.01`

Measured rows:

| App | Scale | CuPy median sec | RTDL median sec | Ratio | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| Hausdorff/X-HD | 8,192 x 8,192 | `0.008320` | `0.008316` | `0.9995x` RTDL/CuPy | pass |
| RTNN uniform | 65,536 points | `0.000140` | `0.000136` | `1.030x` CuPy/RTDL | pass |
| RTNN clustered | 65,536 points | `0.047041` | `0.018761` | `2.507x` CuPy/RTDL | pass |
| RTNN shell | 65,536 points | `0.002723` | `0.000356` | `7.645x` CuPy/RTDL | pass |

## Change

The canonical defaults now use:

- Hausdorff: `8192` points per side, repeat `9`
- RTNN: `65536` points, repeat `9`

No native engine code changed. No app-specific engine logic was added.

## Interpretation

The project should not let tiny smoke-test rows masquerade as serious benchmark failures. Scaling the canonical rows makes the measured work closer to the benchmark-app intent and removes the microsecond jitter that dominated the smaller packet rows.

The design lesson is still conservative: this does not authorize a public speedup claim. It only defines more meaningful internal packet defaults.

## Boundary

This is not release consensus and not a v2.5 release packet.

It does not authorize public speedup claims, broad RT-core claims, whole-app speedup claims, true-zero-copy claims, automatic Triton selection, package-install claims, or paper-reproduction claims.
