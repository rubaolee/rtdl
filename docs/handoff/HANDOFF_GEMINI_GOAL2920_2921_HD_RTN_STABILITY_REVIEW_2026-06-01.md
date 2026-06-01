# Handoff: Gemini Review Goal2920-2921 RTNN/Hausdorff Stability

Please write an independent Gemini review to:

`docs/reviews/goal2922_gemini_review_goal2920_2921_rtnn_hausdorff_stability_2026-06-01.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

Important: do not try to run shell commands. Use file reads/search only. The
validation output is already provided below.

## Scope

Review these files:

- `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py`
- `docs/reports/goal2920_rtnn_hausdorff_large_scale_stability_and_hd_default_2026-06-01.md`
- `docs/reports/goal2920_hausdorff_rtnn_large_probe_pod/rtnn_262144_repeat9.json`
- `docs/reports/goal2920_hausdorff_rtnn_large_probe_pod/hd_confirm/hd8192_target4096_repeat9.json`
- `docs/reports/goal2920_hausdorff_rtnn_large_probe_pod/hd_confirm/hd16384_target4096_repeat9.json`
- `docs/reports/goal2921_current_packet_after_hausdorff_target4096_2026-06-01.md`
- `docs/reports/goal2921_current_packet_after_hd4096_pod/goal2855_summary.json`
- `docs/reports/goal2921_current_packet_after_hd4096_pod/goal2921_triage.json`
- `docs/reports/goal2921_current_packet_after_hd4096_pod/goal2801_hausdorff_xhd.json`
- `tests/goal2920_rtnn_hausdorff_large_scale_stability_test.py`
- `tests/goal2921_current_packet_after_hausdorff_target4096_test.py`
- `src/rtdsl/v2_5_internal_readiness.py`

## Facts To Verify

Goal2920:

- RTNN 262,144-point repeat-9 probe passes.
- RTNN CuPy/RTDL ratios are uniform `3.740x`, clustered `1.971x`, shell `4.342x`.
- The old Hausdorff 16k target-2048 repeat-9 row regressed at `1.722x` RTDL/CuPy.
- The target sweep identifies `4096` as best among the tried reduced targets.
- Target `4096` repeat-9 confirmation passes:
  - 8192 x 8192: RTDL/CuPy `0.949x`
  - 16384 x 16384: RTDL/CuPy `0.942x`
- The code changes only the canonical Hausdorff harness default to target `4096`
  and bumps the entrypoint version; it does not change native engine logic.

Goal2921:

- full seven-app packet passes at commit
  `fe628f4faec8e7d43521f11afd395b29462fba8b`;
- `all_pass: true`;
- artifact count `7`;
- dirty artifacts `{}`;
- claim-boundary violations `{}`;
- Hausdorff canonical row uses target `4096`, exact match, RT cores, RTDL/CuPy
  ratio `0.915x`;
- triage performance targets `[]`;
- readiness index points at
  `docs/reports/goal2921_current_packet_after_hd4096_pod/goal2855_summary.json`;
- toolchain metadata remains present.

## Validation Already Run

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2801_hausdorff_xhd_v25_canonical_entrypoint_test tests.goal2916_packet_toolchain_provenance_test tests.goal2917_current_packet_toolchain_provenance_test tests.goal2920_rtnn_hausdorff_large_scale_stability_test tests.goal2921_current_packet_after_hausdorff_target4096_test tests.goal2806_v2_5_internal_readiness_packet_test

Ran 28 tests in 1.277s
OK
```

## Review Questions

1. Does Goal2920 correctly diagnose the RTNN and Hausdorff scale-stability risks?
2. Is changing the Hausdorff reduced target default to `4096` justified by the
   evidence?
3. Does Goal2921 prove the current seven-app packet is still clean after the
   default change?
4. Does the work preserve the app-agnostic native-engine boundary?
5. Does it avoid public/release/performance overclaiming?
6. What residual risks remain before any v2.5 release packet?

Expected likely verdict: `accept-with-boundary`, because second-architecture,
compiler fairness, RayJoin row/overlay, Tier C rows, and fresh 3-AI release
review remain outside this scope.
