# Goal866: Segment Polygon Anyhit Review Packet

Date: 2026-04-23

## Purpose

Make the current RT promotion boundary for
`segment_polygon_anyhit_rows` machine-readable and explicit.

The app contains two very different surfaces:

- compact `segment_flags` / `segment_counts`
- full pair-row `rows`

Those two surfaces do not share the same RT promotion story.

## Problem

The current repo truth is already honest but scattered:

- compact modes can reuse the native segment-polygon hit-count primitive
- `rows` mode does not have a native OptiX pair-row emitter
- `--optix-mode native` is allowed only for compact modes
- `--require-rt-core` still fails for the whole app

Without a dedicated review packet, the app still reads as one undifferentiated
thing. For RT roadmap work, that is too vague.

## Change

Added:

- `/Users/rl2025/rtdl_python_only/scripts/goal866_segment_polygon_anyhit_review_packet.py`
- `/Users/rl2025/rtdl_python_only/tests/goal866_segment_polygon_anyhit_review_packet_test.py`

The packet makes the split explicit:

- compact modes inherit readiness only through the Goal864 segment-polygon
  native gate state
- `rows` mode remains blocked by a missing native pair-row emitter

## Current Result

Using the current local Goal864 segment-polygon packet:

- `segment_flags`: `needs_segment_polygon_real_optix_artifact`
- `segment_counts`: `needs_segment_polygon_real_optix_artifact`
- `rows`: `needs_native_pair_row_emitter`

That is the correct local state.

It means:

- compact modes still cannot be promoted ahead of the native hit-count core
- pair-row output is blocked for a different and stricter reason:
  there is no native row emitter yet

## Boundary

This goal does not promote `segment_polygon_anyhit_rows` into an active RTX
claim set.

It only documents the existing split:

- compact modes may eventually become bounded RT-ready
- pair-row mode is not promotable until a real native row emitter exists

## Verification

Focused checks:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal866_segment_polygon_anyhit_review_packet.py
PYTHONPATH=src:. python3 -m unittest \
  tests.goal866_segment_polygon_anyhit_review_packet_test \
  tests.goal864_segment_polygon_gate_review_packet_test \
  tests.goal808_segment_polygon_app_native_mode_propagation_test \
  tests.goal807_segment_polygon_optix_mode_gate_test
python3 -m py_compile \
  scripts/goal866_segment_polygon_anyhit_review_packet.py \
  tests/goal866_segment_polygon_anyhit_review_packet_test.py
git diff --check
```

Result:

- `16` tests `OK`
- `py_compile` OK
- `git diff --check` OK
