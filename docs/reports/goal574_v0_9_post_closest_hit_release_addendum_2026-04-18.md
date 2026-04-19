# Goal 574: v0.9 Post-Closest-Hit Release Addendum

Date: 2026-04-18

## Verdict

ACCEPT. v0.9 remains release-ready after solving the RTXRMQ closest-hit gap for
CPU reference, `run_cpu`, and Embree.

## Superseded Earlier Boundary

Goal 571 originally included `/Users/rl2025/Downloads/2306.03282v1.pdf` as a
bounded threshold-hitcount traversal analogue because RTDL lacked a public
closest-hit primitive.

Goal 573 resolves that missing feature for the CPU and Embree closure path:

- new primitive: `rt.ray_triangle_closest_hit(exact=False)`
- CPU reference support: `rt.run_cpu_python_reference(...)`
- native CPU/oracle runtime support: `rt.run_cpu(...)`
- native Embree 3D support: `rt.run_embree(...)`

The remaining boundary is backend coverage: OptiX, Vulkan, and HIPRT do not yet
claim native closest-hit support.

## Final Evidence

- Goal 573 report:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal573_rtxrmq_closest_hit_feature_2026-04-18.md`
- Linux JSON:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal573_rtxrmq_closest_hit_linux_2026-04-18.json`
- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal573_external_review_2026-04-18.md`
- Gemini Flash review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal573_gemini_flash_review_2026-04-18.md`

Final tests after the feature:

```text
macOS: python3 -m unittest discover -s tests
Ran 239 tests in 61.701s
OK

Linux: python3 -m unittest discover -s tests
Ran 239 tests in 144.697s
OK
```

Linux exact RTXRMQ-style performance:

| Backend | Median seconds | Exact RMQ parity |
|---|---:|---|
| CPU Python reference | `11.408521` | yes |
| Embree | `0.027440` | yes |

Embree is about `416x` faster than the Python reference on this bounded case.

## Release Impact

No release blocker remains from the RTXRMQ paper workload. The v0.9 release
claim must say that exact closest-hit RMQ is closed for CPU reference,
`run_cpu`, and Embree, while OptiX/Vulkan/HIPRT closest-hit support is future
work.
