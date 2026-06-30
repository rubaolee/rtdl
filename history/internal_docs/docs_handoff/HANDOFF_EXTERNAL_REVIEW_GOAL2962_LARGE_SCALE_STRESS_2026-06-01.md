# Handoff: External Review For Goal2962 Large-Scale v2.5 Stress Probe

Please perform an independent read-only review of Goal2962. Write your review
to the output path named in the prompt you received. Do not edit source files,
tests, reports, or artifacts other than that single review file.

## Scope

Goal2962 adds large-scale pod stress evidence for three high-risk v2.5 paths:

- RTNN ranked summaries at 262,144 query/search points.
- Exact Hausdorff/X-HD at 16,384 by 16,384 points.
- RT-DBSCAN grouped-stream continuation at 262,144 points.

Primary files:

- `docs/reports/goal2962_large_scale_v2_5_stress_probe_2026-06-01.md`
- `tests/goal2962_large_scale_v2_5_stress_probe_test.py`
- `docs/reports/goal2962_large_scale_stress_pod/goal2962_rtnn_262k.json`
- `docs/reports/goal2962_large_scale_stress_pod/goal2962_hausdorff_16k.json`
- `docs/reports/goal2962_large_scale_stress_pod/goal2962_rt_dbscan_262k.json`
- `src/rtdsl/v2_5_internal_readiness.py`

## Questions To Answer

1. Do the three artifacts really report `status: pass`, clean source, and the
   expected source commit `8deb21be`?
2. Does RTNN correctly use four 65,536-query graph chunks at 262K and match the
   same-contract CuPy grid opponent?
3. Does the Hausdorff 16K artifact prove an exact RTDL/OptiX RT-core path with
   zero distance error against the optimized CuPy rawkernel opponent?
4. Does the RT-DBSCAN 262K artifact prove grouped-stream continuation remains
   RT-core accelerated, compact, signature-matching, and faster than the
   prepared CuPy grid opponent?
5. Does the report avoid overclaiming? In particular, it must not authorize
   release, public speedup, broad RT-core speedup, whole-app speedup, true
   zero-copy, package install, Triton auto-selection, paper reproduction, or
   app-specific native-engine customization.
6. Is Goal2962 appropriate as stress evidence layered on top of the current
   Goal2959 zero-target packet, or does it need different framing?

## Expected Verdict Format

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

For this review, `accept-with-boundary` is expected if the stress evidence is
sound but release/public claims remain blocked.

Please include file-level findings where possible and distinguish source-backed
facts from your own recommendations.
