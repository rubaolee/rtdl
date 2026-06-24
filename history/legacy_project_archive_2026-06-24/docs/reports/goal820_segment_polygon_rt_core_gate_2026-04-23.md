# Goal 820: Segment/Polygon RT-Core Gate

Date: 2026-04-23

Status: complete

## Problem

The segment/polygon apps expose OptiX and now have explicit native-mode
switches, but their public performance classification remains
`host_indexed_fallback` until strict native RTX validation passes. This is a
high-risk area for accidental overclaiming because `--optix-mode native` sounds
like a claim path even though it is still a gated candidate.

Affected apps:

- `examples/rtdl_road_hazard_screening.py`
- `examples/rtdl_segment_polygon_hitcount.py`
- `examples/rtdl_segment_polygon_anyhit_rows.py`

## Change

Added `--require-rt-core` to all three apps. The flag rejects the current OptiX
paths, including `--optix-mode native`, until the strict Goal807-style RTX gate
passes.

Normal compatibility and native-mode experimentation remain available without
`--require-rt-core`.

Payloads now include `rt_core_accelerated: false` while the apps remain
unpromoted.

## Current Status

| App | Native mode status | Claim status |
| --- | --- | --- |
| `road_hazard_screening` | explicit native hit-count mode can be requested | no RT-core claim |
| `segment_polygon_hitcount` | explicit native hit-count mode can be requested | no RT-core claim |
| `segment_polygon_anyhit_rows` | compact flags/counts can request native hit-count mode; pair rows cannot | no RT-core claim |

## Verification

Run:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal820_segment_polygon_rt_core_gate_test tests.goal818_rtx_claim_gate_summary_test tests.goal705_optix_app_benchmark_readiness_test tests.goal803_rt_core_app_maturity_contract_test
python3 -m py_compile examples/rtdl_road_hazard_screening.py examples/rtdl_segment_polygon_hitcount.py examples/rtdl_segment_polygon_anyhit_rows.py tests/goal820_segment_polygon_rt_core_gate_test.py
git diff --check
```

Expected result: all tests pass and no whitespace errors.

## Release Boundary

This goal prevents accidental claims. It does not prove native segment/polygon
RT-core performance and does not promote these apps to `rt_core_ready`.
