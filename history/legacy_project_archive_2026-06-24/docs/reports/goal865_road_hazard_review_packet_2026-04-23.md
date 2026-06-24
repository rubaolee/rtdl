# Goal865: Road Hazard Review Packet

Date: 2026-04-23

## Purpose

Make the `road_hazard_screening` RT promotion dependency explicit.

This app is built on the segment/polygon hit-count primitive, so its RT-core
promotion should never outrun the promotion state of that core primitive.

## Problem

The current repo truth is spread across several places:

- `road_hazard_screening` is still `host_indexed_fallback`
- the app exposes `--optix-mode native`
- the app still hard-fails `--require-rt-core`
- the app-support matrix says road hazard depends on the segment/polygon core

All of that is honest, but it is still too implicit. There was no small packet
that says:

- what the current road-hazard recommendation is
- which upstream dependency blocks it
- what exact next step is required

## Change

Added:

- `/Users/rl2025/rtdl_python_only/scripts/goal865_road_hazard_review_packet.py`
- `/Users/rl2025/rtdl_python_only/tests/goal865_road_hazard_review_packet_test.py`

The packet reads the existing Goal864 segment/polygon review packet and maps
that into a bounded road-hazard recommendation:

- `needs_segment_polygon_real_optix_artifact`
- `blocked_by_segment_polygon_gate_failure`
- `ready_for_review`

## Current Result

With the current local Goal864 packet:

- segment/polygon status: `needs_real_optix_artifact`
- road-hazard status: `needs_segment_polygon_real_optix_artifact`

That is the correct local result.

It means:

- road hazard is not independently promotable yet
- the missing evidence is still the real OptiX/RTX segment-polygon gate result
- there is no honest road-hazard RT claim before that upstream proof exists

## Boundary

This goal does not promote `road_hazard_screening` into an active RTX claim
path.

It only documents and automates the dependency rule that already exists in the
app-support matrix and the current RT-core roadmap.

## Verification

Focused checks:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal865_road_hazard_review_packet.py
PYTHONPATH=src:. python3 -m unittest \
  tests.goal865_road_hazard_review_packet_test \
  tests.goal864_segment_polygon_gate_review_packet_test \
  tests.goal807_segment_polygon_optix_mode_gate_test
python3 -m py_compile \
  scripts/goal865_road_hazard_review_packet.py \
  tests/goal865_road_hazard_review_packet_test.py
git diff --check
```

Result:

- `12` tests `OK`
- `py_compile` OK
- `git diff --check` OK
