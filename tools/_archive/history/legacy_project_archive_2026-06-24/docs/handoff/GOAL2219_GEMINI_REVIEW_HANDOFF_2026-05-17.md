# Goal2219 Gemini Review Handoff

Please perform an independent read-only review of Goal2219 and write your review to:

`docs/reviews/goal2220_gemini_review_goal2219_optix_pip_default_prefilter_pod_2026-05-17.md`

## Context

Goal2218 made the OptiX PIP device prefilter the default for positive-only PIP, with a conservative opt-out through `RTDL_OPTIX_PIP_DISABLE_DEVICE_PREFILTER=1`.

Goal2219 imports pod evidence from `root@69.30.85.202 -p 22064` showing the default path on the same RayJoin-exported PIP query stream used by Goals 2209 and 2213:

- evidence report: `docs/reports/goal2219_optix_pip_device_prefilter_default_pod_2026-05-17.md`
- evidence summary: `docs/reports/goal2219_optix_pip_device_prefilter_default_pod_2026-05-17.json`
- artifact dir: `docs/reports/goal2219_optix_pip_device_prefilter_default_pod/`
- source change report: `docs/reports/goal2218_optix_pip_device_prefilter_default_2026-05-17.md`
- tests: `tests/goal2218_optix_pip_device_prefilter_default_test.py`, `tests/goal2219_optix_pip_device_prefilter_default_pod_test.py`

## What To Check

1. Confirm the default path, with no `RTDL_OPTIX_PIP_DEVICE_PREFILTER` env var, preserves CPU/Embree/OptiX parity on `8686` rows.
2. Confirm the evidence supports only the narrow engineering claim: RTDL OptiX PIP improved from Goal2209 `4.107544 s` and Goal2213 `0.618395 s` to Goal2219 `0.121710 s`.
3. Confirm the candidate reduction claim is supported: `2797698` conservative candidates down to `8793`, while emitted rows remain `8686`.
4. Confirm the report does not overclaim: no RTDL beats RayJoin claim, no broad RT-core claim, no paper reproduction claim, no v2.0 release authorization.
5. Flag any wording that could mislead a public performance narrative, especially around "default" versus "release-ready".

## Expected Review Shape

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please state that Gemini is an independent external AI reviewer distinct from Codex. This is a review only; do not edit source code.
