# Goals658-679 Cross-Engine Prepared Visibility/Count Optimization

Date: 2026-04-20

Status: accepted catch-up history record.

This revision round records current-main work after the public `v0.9.5` tag.
It is not a new public release tag and is not a retroactive `v0.9.5` tag
claim.

## Covered Work

| Goal range | Result |
| --- | --- |
| Goals658-667 | Selected and optimized a Mac visibility/collision app case for Apple RT, added profiling, prepacked rays, scalar count output, source restoration, public docs, and Apple RT closure evidence. |
| Goal668 | Recorded current-main Apple RT visibility-count pre-release audit. |
| Goal669 | Wrote cross-engine performance optimization lessons from Apple RT. |
| Goal670 | Produced and reviewed OptiX, HIPRT, and Vulkan performance optimization plans. |
| Goals671-673 | Implemented OptiX prepared 2D any-hit count, prepacked ray count, cleanup, Linux validation, and consensus. |
| Goal674 | Implemented HIPRT prepared 2D any-hit, Linux validation, performance sanity, and 3-AI consensus. |
| Goal675 | Implemented Vulkan prepared 2D any-hit with packed-ray support, Linux validation, performance sanity, and 2-AI consensus. |
| Goals676-677 | Wrote cross-engine optimization closure, refreshed public docs, and received Codex + Claude + Gemini acceptance. |
| Goal678 | Ran local total test, public-doc audit, and flow audit. |
| Goal679 | Ran fresh Linux OptiX/Vulkan/HIPRT backend release gate and received Codex + Claude + Gemini acceptance. |

## Public Boundary

- Current public release remains `v0.9.5`.
- This current-main round proves a prepared/prepacked optimization direction
  for repeated 2D visibility / any-hit / blocked-ray-count workloads.
- Apple RT, OptiX, HIPRT, and Vulkan all have bounded current-main evidence in
  this class.
- These are not broad speedup claims for every RTDL workload.
- These are not DB or graph speedup claims.
- These are not one-shot-call speedup claims.
- Apple RT scalar count does not imply full emitted-row Apple RT speedup.
- GTX 1070 Linux evidence is not RT-core evidence.
- HIPRT/Orochi CUDA evidence is not AMD GPU validation.

## Key Evidence Files

- `docs/reports/goal667_apple_rt_visibility_count_closure_2026-04-20.md`
- `docs/reports/goal669_cross_engine_performance_optimization_lessons_2026-04-20.md`
- `docs/reports/goal670_engine_performance_optimization_consensus_2026-04-20.md`
- `docs/reports/goal671_optix_prepared_anyhit_and_hiprt_boundary_2026-04-20.md`
- `docs/reports/goal672_optix_prepacked_ray_anyhit_count_2026-04-20.md`
- `docs/reports/goal673_optix_prepacked_ray_cleanup_2026-04-20.md`
- `docs/reports/goal674_hiprt_prepared_2d_anyhit_optimization_2026-04-20.md`
- `docs/reports/goal675_vulkan_prepared_2d_anyhit_packed_optimization_2026-04-20.md`
- `docs/reports/goal676_677_cross_engine_optimization_closure_and_doc_refresh_2026-04-20.md`
- `docs/reports/goal676_677_consensus_2026-04-20.md`
- `docs/reports/goal678_local_total_test_doc_flow_audit_2026-04-20.md`
- `docs/reports/goal679_linux_gpu_backend_release_gate_2026-04-20.md`
- `docs/reports/goal678_679_consensus_2026-04-20.md`

## Final Gates

Goal678 local gate:

```text
Ran 1266 tests in 108.891s
OK (skipped=187)
```

Additional Goal678 checks:

```text
public command truth audit: valid, 250 commands across 14 docs
public entry smoke: valid
focused public-doc tests: 10 tests OK
git diff --check: clean
```

Goal679 Linux gate:

```text
fresh builds: OptiX (9, 0, 0) PASS; Vulkan (0, 1, 0) PASS; HIPRT (2, 2, 15109972) PASS
focused native suite: Ran 30 tests in 10.864s, OK (skipped=2)
```

Goal679 Linux performance sanity at `4096` rays / `1024` triangles:

| Backend | Direct median | Prepared/prepacked median | Count |
| --- | ---: | ---: | ---: |
| OptiX | `0.0035153299977537245 s` | `0.00005833699833601713 s` | `4096` |
| HIPRT | `0.5688568009936716 s` | `0.0057718300085980445 s` | `4096` |
| Vulkan | `0.009350006002932787 s` | `0.004641148989321664 s` | `4096` |

## Consensus

- Goal676/677 was accepted by Codex, Claude, and Gemini.
- Goal678/679 was accepted by Codex, Claude, and Gemini.

This round is accepted as current-main release-gate evidence for the
prepared/prepacked visibility/count optimization line.
