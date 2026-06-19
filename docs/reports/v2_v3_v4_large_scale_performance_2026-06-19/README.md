# V2/V3/V4 Large-Scale Performance Artifact Bundle

Status: raw evidence bundle for
`../v2_v3_v4_large_scale_performance_comparison_2026-06-19.md`.

## Files

| Path | Purpose |
| --- | --- |
| `lx1_current_benchmark_scale_profile_2026-06-19.json` | Fresh 10-row current benchmark-app scale-profile run on `192.168.1.20`. |
| `scale_outputs/*.stdout.json` | Per-row JSON payloads for the current all-app scale-profile run. |
| `scale_outputs/*.stderr.txt` | Per-row stderr captures. |
| `large_supplements/hausdorff_xhd_1m_threshold.stdout.json` | 1,048,576-point-per-side Hausdorff/X-HD supplement. |
| `large_supplements/triangle_counting_rt_graph_2a1_65536.stdout.json` | 131,072-ray / 327,680-primitive triangle-counting supplement. |
| `lx1_v4_m1_fixed_radius_cupy_262k_probe_2026-06-19.json` | V4 M1 fixed-radius 262,144-row route probe. |

## Host

- Host: `192.168.1.20` / `lx1`
- GPU: `NVIDIA GeForce GTX 1070`
- Driver: `580.126.09`
- Memory: 8192 MiB
- Source commit: `6d2193af16f8269f3e901124593dacc43335255b`

## Boundaries

This bundle does not authorize broad public speedup wording, RT-core speedup
wording, whole-app acceleration wording, paper-reproduction wording, automatic
partner selection, package-install claims, public true-zero-copy, or async
completion claims.
