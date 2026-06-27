# V2/V3/V4 Large-Scale Performance Artifact Bundle

Status: raw evidence bundle for
`../v2_v3_v4_large_scale_performance_comparison_2026-06-19.md`.

## Files

| Path | Purpose |
| --- | --- |
| `lx1_a27a4c92_current_benchmark_scale_profile_clean_2026-06-19.json` | Current-head clean 10-row benchmark-app scale-profile run on `192.168.1.20`. |
| `scale_outputs_lx1_a27a4c92_clean/*.stdout.json` | Current-head per-row JSON payloads for the all-app scale-profile run. |
| `scale_outputs_lx1_a27a4c92_clean/*.stderr.txt` | Current-head per-row stderr captures. |
| `lx1_a27a4c92_v4_m1_linux_gpu_release_gate_clean_2026-06-19.json` | Current-head clean V4 M1 Linux GPU release gate with the 262,144-row benchmark probe. |
| `v4_m1_linux_gpu_release_gate_lx1_a27a4c92_clean/` | Current-head V4 gate sub-artifacts: CuPy, Numba, PyTorch, DLPack, benchmark, test-matrix, claim-scan evidence. |
| `lx1_a27a4c92_v4_0_release_promotion_gate_clean_2026-06-19.json` | Current-head V4.0.0 release-promotion gate. |
| `large_supplements/hausdorff_xhd_1m_threshold.stdout.json` | 1,048,576-point-per-side Hausdorff/X-HD supplement. |
| `large_supplements/triangle_counting_rt_graph_2a1_65536.stdout.json` | 131,072-ray / 327,680-primitive triangle-counting supplement. |
| `lx1_v4_m1_fixed_radius_cupy_262k_probe_2026-06-19.json` | V4 M1 fixed-radius 262,144-row route probe. |
| `lx1_current_benchmark_scale_profile_2026-06-19.json` | Earlier local all-app run retained for comparison; superseded by the current-head clean run above. |
| `scale_outputs/` | Earlier per-row payloads retained for comparison. |

## Host

- Host: `192.168.1.20` / `lx1`
- GPU: `NVIDIA GeForce GTX 1070`
- Driver: `580.126.09`
- Memory: 8192 MiB
- Current-head source commit: `a27a4c92f2b8040cb2f655350567059d756b46b1`
- Earlier retained source commit: `6d2193af16f8269f3e901124593dacc43335255b`

## Pod Status

- RTX pod target: `root@157.157.221.29 -p 22234`
- Latest retry on 2026-06-19: `Connection refused`
- Result: no pod benchmark artifact is present in this bundle.
- Pod-ready rerun instructions live in
  `../v2_v3_v4_large_scale_performance_comparison_2026-06-19.md`.

## Boundaries

This bundle does not authorize broad public speedup wording, RT-core speedup
wording, whole-app acceleration wording, paper-reproduction wording, automatic
partner selection, package-install claims, public true-zero-copy, or async
completion claims.
