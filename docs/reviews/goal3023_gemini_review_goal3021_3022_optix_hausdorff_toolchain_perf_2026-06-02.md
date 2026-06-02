# Gemini Review: Goal3021-3022 OptiX Hausdorff Toolchain and Performance Probe

**Date:** 2026-06-02
**Reviewer:** Gemini CLI Agent
**Verdict:** accept

## Reviewed Documents

- `docs/reports/goal3021_l4_optix_cuda126_hausdorff_rt_smoke_2026-06-02.md`
- `docs/reports/goal3021_l4_optix_cuda126_hausdorff_rt_smoke_2026-06-02.json`
- `tests/goal3021_l4_optix_cuda126_hausdorff_rt_smoke_test.py`
- `docs/reports/goal3022_hausdorff_optix_cupy_perf_probe_2026-06-02.md`
- `docs/reports/goal3022_hausdorff_optix_cupy_perf_probe_2026-06-02.json`
- `tests/goal3022_hausdorff_optix_cupy_perf_probe_test.py`
- `src/rtdsl/v2_6_roadmap.py`
- `docs/research/future_version_to_do_list.md`

## Answers to Questions

### 1. Does Goal3021 correctly document that CUDA 12.6 side-by-side toolkit rebuilds unblock the L4 OptiX exact Hausdorff smoke after the Goal3020 CUDA 12.8 PTX/driver blocker?

Yes, Goal3021 correctly documents this. The report explicitly details the Goal3020 PTX/toolchain blocker and describes the successful workaround using a side-by-side CUDA 12.6 toolkit rebuild. It provides evidence of `libnvrtc.so.12` linking to CUDA 12.6 and confirms that the RT Hausdorff path now executes with `rt_core_accelerated: true`. The JSON artifact and associated test cases corroborate these findings, and the `v2_6_roadmap.py` status for Goal3021 explicitly notes the `cuda12_6_side_by_side_toolchain_unblocked_rt_hausdorff_smoke`.

### 2. Does Goal3021 avoid overclaiming package-install readiness, speedup, release readiness, zero-copy, or broad RT-core performance?

Yes, Goal3021 rigorously avoids overclaiming. The "Boundary" section of the markdown report clearly states that it is not performance evidence and does not authorize v2.6 release, public speedup wording, RT-core speedup wording, whole-app speedup wording, true-zero-copy wording, package-install claims, or app-specific native-engine behavior. The JSON artifact contains multiple `_claim_authorized: false` flags, and the unit test (`tests/goal3021_..._test.py`) explicitly verifies that these overclaiming statements are absent or set to false.

### 3. Does Goal3022 correctly interpret the evidence: exact OptiX RT Hausdorff now runs and preserves scalar distance parity, but the current dense 2D exact HD performance path is the explicit CuPy grouped-grid partner implementation?

Yes, Goal3022 correctly interprets the evidence. The report confirms that the CUDA 12.6 toolchain repair allows all RT rows to execute with `rt_core_accelerated: true` and that scalar Hausdorff distance parity is preserved. However, it clearly demonstrates through measured data (e.g., RT methods being hundreds of times slower) and explicit statements that the `cupy_grouped_grid_rawkernel` is the current fast reference implementation for dense 2D exact Hausdorff. The JSON artifact and test also confirm `all_rt_rows_exact_and_rt_core: true`, `all_recorded_parity_true: true`, and identify `cupy_grouped_grid_rawkernel` as the `best_current_non_rt_partner_method`.

### 4. Are the Goal3022 design conclusions sound and app-agnostic: next RT Hausdorff work needs generic sparse candidate frontier/radius-plan/device-resident continuation primitives, not Hausdorff-specific native-engine customizations?

Yes, the Goal3022 design conclusions are sound and adhere to app-agnostic principles. The report unequivocally states that future RT Hausdorff work should focus on generic runtime/primitive requirements such as sparse candidate frontiers, radius plans, and device-resident continuations, explicitly advising against Hausdorff-specific native-engine customizations. This is further reinforced by entries in `docs/research/future_version_to_do_list.md`, which consistently emphasize generic primitives and avoiding domain-specific ABI names for future features.

### 5. Are the roadmap and future-work notes consistent with the v2.6 boundaries: user-selected partners, Triton paused, Numba first-class lane, no release authorization?

Yes, both `src/rtdsl/v2_6_roadmap.py` and `docs/research/future_version_to_do_list.md` are fully consistent with the stated v2.6 boundaries. The roadmap explicitly designates Numba as the `primary_partner_track` and emphasizes `users_choose_supported_partners_explicitly`. `triton_status` is `paused_ignored_for_recommended_paths_until_new_same_contract_evidence`. Crucially, both documents consistently set `release_authorized: False` and disclaim any public speedup, RT-core speedup, whole-app speedup, true-zero-copy, automatic partner/Triton selection, Numba speedup, or app-specific native-engine logic claims. The future work notes also align by prioritizing generic primitives and avoiding app-specific solutions, supporting the overall v2.6 strategic direction.

## Conclusion

The work documented in Goal3021 and Goal3022 successfully addresses the CUDA 12.8 PTX/driver blocker for L4 OptiX exact Hausdorff, proving runtime correctness with CUDA 12.6. Furthermore, Goal3022 provides a clear performance assessment, establishing that while the RT path now executes correctly, the CuPy grouped-grid implementation remains the current performance leader for dense 2D exact Hausdorff. The reports maintain strict adherence to project claim boundaries and consistently advocate for generic, app-agnostic primitive development for future work, fully aligning with the v2.6 roadmap and its cautious approach to performance claims and release authorization.

The independent review finds the work to be well-documented, evidence-based, and strategically aligned.

**Verdict: accept**
