# Handoff: Goal3691 RayJoin Same-Source Probe Review

Please perform a read-only independent review of Goal3691 and write your review to:

`docs/reviews/goal3692_gemini_review_goal3691_rayjoin_same_source_probe_2026-06-07.md`

## Context

Goal3691 is the first current packet comparing RTDL against the original RayJoin checkout on the same bundled Brazil sample files, instead of only comparing against dense all-CuPy same-contract baselines.

Important: this is a diagnostic probe, not a RayJoin paper reproduction and not a public performance claim.

## Files To Inspect

- `docs/reports/goal3691_rayjoin_original_same_source_probe_2026-06-07.md`
- `docs/reports/goal3691_rayjoin_original_same_source_probe_a5000/summary.json`
- `scripts/goal3691_rayjoin_original_same_source_probe.py`
- `tests/goal3691_rayjoin_original_same_source_probe_test.py`
- `docs/research/future_version_to_do_list.md`

You may inspect the supporting Goal3688/3690 reports if useful:

- `docs/reports/goal3688_rayjoin_native_pip_safe_mixed_composite_2026-06-07.md`
- `docs/reports/goal3690_rayjoin_native_pip_safe_mixed_multicount_2026-06-07.md`

## Key Facts To Verify

- RTDL source commit in the artifact: `c8f9adf0`, with `goal3691_scoped_source_dirty=false`.
- RayJoin source commit in the artifact: `02bf622`, but the checkout is not pristine: `M src/util/markers.h` and `?? release/`. The source diff is an include-path repair from `<nvToolsExt.h>` to `<nvtx3/nvToolsExt.h>`.
- Same files used:
  - county: `/root/RayJoin/test/dataset/br_county_clean_25_odyssey_final.txt`
  - soil: `/root/RayJoin/test/dataset/br_soil_ascii_odyssey_final.txt`
- PIP:
  - RayJoin query time: `0.000879685 s`
  - RTDL query time: `0.000471005 s`
  - RTDL/RayJoin query speedup: `1.8677x`
  - RayJoin PIP timing output does not print a count, so PIP count parity is not established.
- LSI:
  - RayJoin query time: `0.000897010 s`
  - RTDL query time: `0.011885975 s`
  - RTDL/RayJoin query speedup: `0.0755x`
  - RayJoin checked intersections: `20860`
  - RTDL row count: `20859`
  - delta: `-1`

## Questions To Answer

1. Is the report honest that PIP is promising but not fully count-validated against RayJoin?
2. Is the report honest that LSI is a correctness/performance blocker, not a win?
3. Does the script preserve app-agnostic RTDL engine boundaries and avoid adding RayJoin-specific native logic?
4. Does the artifact support only the limited internal conclusion and avoid release/public/RayJoin-paper/RTDL-beats-RayJoin/broad-RT-core/zero-copy claims?
5. Are the recommended next steps correct: localize the missing LSI intersection and compare RTDL's predicate to RayJoin's scaled/high-precision predicate?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
