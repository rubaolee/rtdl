# Handoff: Review Goals3021-3022 OptiX Hausdorff Toolchain And Performance Probe

Please perform an independent read-only review of the latest RTDL main branch work for:

- `docs/reports/goal3021_l4_optix_cuda126_hausdorff_rt_smoke_2026-06-02.md`
- `docs/reports/goal3021_l4_optix_cuda126_hausdorff_rt_smoke_2026-06-02.json`
- `tests/goal3021_l4_optix_cuda126_hausdorff_rt_smoke_test.py`
- `docs/reports/goal3022_hausdorff_optix_cupy_perf_probe_2026-06-02.md`
- `docs/reports/goal3022_hausdorff_optix_cupy_perf_probe_2026-06-02.json`
- `tests/goal3022_hausdorff_optix_cupy_perf_probe_test.py`
- `src/rtdsl/v2_6_roadmap.py`
- `docs/research/future_version_to_do_list.md`

Questions to answer:

1. Does Goal3021 correctly document that CUDA 12.6 side-by-side toolkit rebuilds unblock the L4 OptiX exact Hausdorff smoke after the Goal3020 CUDA 12.8 PTX/driver blocker?
2. Does Goal3021 avoid overclaiming package-install readiness, speedup, release readiness, zero-copy, or broad RT-core performance?
3. Does Goal3022 correctly interpret the evidence: exact OptiX RT Hausdorff now runs and preserves scalar distance parity, but the current dense 2D exact HD performance path is the explicit CuPy grouped-grid partner implementation?
4. Are the Goal3022 design conclusions sound and app-agnostic: next RT Hausdorff work needs generic sparse candidate frontier/radius-plan/device-resident continuation primitives, not Hausdorff-specific native-engine customizations?
5. Are the roadmap and future-work notes consistent with the v2.6 boundaries: user-selected partners, Triton paused, Numba first-class lane, no release authorization?

Please write the review to:

`docs/reviews/goal3023_gemini_review_goal3021_3022_optix_hausdorff_toolchain_perf_2026-06-02.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Do not edit source code. If you run tests, prefer:

```powershell
$env:PYTHONPATH="src;."; py -3 -m unittest tests.goal3022_hausdorff_optix_cupy_perf_probe_test tests.goal3021_l4_optix_cuda126_hausdorff_rt_smoke_test tests.goal3020_l4_optix_readiness_and_ptx_toolchain_blocker_test tests.goal2989_v2_5_partner_choice_cleanup_and_v2_6_kickoff_test
```
