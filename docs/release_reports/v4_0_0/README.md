# RTDL V4.0.0 Release Package

Status: released source-tree major packet for tag `v4.0.0`.

Version marker: `v4.0.0`

Release date: 2026-06-19

## Release Statement

RTDL V4.0.0 is the current source-tree release. Its headline is the Python GPU
RT-core operator lane: Python frameworks own CUDA arrays, RTDL borrows named
device columns, the OptiX-backed route executes, and the caller receives
fixed-size CUDA output columns.

The first released route is:

`fixed_radius_count_threshold_2d`

It accepts one-dimensional CUDA columns named `ids`, `x`, and `y` for query and
search points, then writes caller-owned `query_ids`, `neighbor_counts`, and
`threshold_flags` output columns. Evidence-backed inputs are CuPy CUDA arrays,
Numba `DeviceNDArray` columns, and detached contiguous PyTorch CUDA tensors for
this exact route.

## Included Release Docs

- [Release Statement](release_statement.md)
- [Support Matrix](support_matrix.md)
- [Public Wording Boundaries](public_wording_boundaries.md)
- [Publication Note](publication.md)
- [Final Closeout](final_closeout.md)
- [Major Release Requirements Trace](major_release_requirements_trace.md)

## Evidence

- [V4.0 M8 release-candidate packet](../../engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md)
- [V4.0 release-candidate blocker manifest](../../engineering/rtdl_v4_0_release_candidate_blockers_2026-06-19.json)
- [V4.0 source-tree runtime story](../../engineering/rtdl_v4_0_source_tree_runtime_story_2026-06-19.md)
- [V4.0 M1 Linux GPU release gate](../../reports/v4_0_m1_linux_gpu_release_gate_2026-06-19.json)
- [V4.0 M1 Linux GPU release gate artifacts](../../reports/v4_0_m1_linux_gpu_release_gate_2026-06-19/README.md)
- [V2/V3/V4 large-scale performance comparison](../../reports/v2_v3_v4_large_scale_performance_comparison_2026-06-19.md)
- [Claude V4.0 M8 external review](../../reviews/claude_v4_0_m8_external_review_2026-06-19.md)

## Release Gates

| Gate | Required state |
| --- | --- |
| Version marker | `VERSION` is `v4.0.0`; editable metadata version is `4.0.0`. |
| Front page and docs index | Current learner-facing docs identify V4.0.0 as the active source-tree release. |
| Route freeze | `fixed_radius_count_threshold_2d` remains the only V4.0 released operator route. |
| Runtime | Source-tree runtime and editable-install hygiene are validated; package/PyPI/wheel claims stay blocked. |
| Device-array evidence | CuPy, Numba, DLPack capsule, and PyTorch route probes pass for the exact M1 route. |
| Stream evidence | Caller stream propagation and fixed-radius prepare/query event ordering are validated; async completion stays blocked. |
| Benchmark evidence | 262,144-row M1 benchmark gate passes with boundary flags; no public speedup claim is authorized. |
| Claim scan | Current front-door claim scan passes with V4.0.0 authorized and blocked claims still false. |
| Validation | `v4_current`, `v4_release_candidate`, source-tree doctor, JSON checks, and diff checks pass locally; Linux GPU gate passed on `192.168.1.20`. |

## Minimal Smoke Commands

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --include-v4-active --json
make build-optix
PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_cupy_hello.py
PYTHONPATH=src:. python scripts/run_test_matrix.py --group v4_current
```

## Release Boundary

V4.0.0 is a source-tree major release for one Python GPU operator route. It is
not a PyPI package, wheel, stable SDK, generated binding release, public
multi-language C ABI release, async runtime, public true-zero-copy release,
public speedup release, RT-core speedup proof, full PyTorch/Numba/DLPack/JAX
surface, or non-Python host embedding release.
