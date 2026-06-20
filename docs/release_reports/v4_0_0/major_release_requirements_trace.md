# RTDL V4.0.0 Release Requirements Trace

Status: release-process trace for `v4.0.0`.

| Requirement | V4.0.0 answer |
| --- | --- |
| Current version named | `VERSION` and editable metadata identify `v4.0.0` / `4.0.0`. |
| User doorway polished | README, docs index, tutorials, examples, and release reports point to V4.0.0 first. |
| Tutorial path | `tutorials/v4_0/` teaches setup, CuPy, Numba, PyTorch, and boundaries. |
| Runnable examples | `examples/v4_0/getting_started/` includes CuPy, Numba, and PyTorch hello programs. |
| Evidence packet | M8 packet, blocker manifest, Linux GPU release gate, current-head clean V4 gate, release-promotion gate, and performance comparison are linked. |
| Claim boundaries | Public wording boundaries block package, SDK, true-zero-copy, async, speedup, and full-framework claims. |
| History boundary | V3.0.2 remains linked as the previous release package, not the current doorway. |

V4.0.0 deliberately releases a narrow operator lane instead of a broad SDK. That
is the product decision that keeps the release useful without inventing claims
the evidence does not support.

Post-promotion freshness is closed by the clean Linux GPU rerun on
`a27a4c92f2b8040cb2f655350567059d756b46b1`:

- `docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/lx1_a27a4c92_v4_m1_linux_gpu_release_gate_clean_2026-06-19.json`
- `docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/lx1_a27a4c92_v4_0_release_promotion_gate_clean_2026-06-19.json`
- `docs/reports/v4_0_release_promotion_gate_post_closeout_2026-06-19.json`
