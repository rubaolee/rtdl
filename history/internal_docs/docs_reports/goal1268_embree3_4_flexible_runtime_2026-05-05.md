# Goal1268 Embree 3/4 Flexible Runtime

Date: 2026-05-05

## Summary

RTDL should not require a fixed Embree major version on Linux pods. Ubuntu package repositories commonly provide Embree 3 as `libembree-dev`, while our prior native backend hard-required Embree 4 headers and `-lembree4`. That made otherwise valid CPU ray-tracing validation fail before any app work could run.

This change makes the Embree backend accept either:

- `include/embree4/rtcore.h` linked with `-lembree4`
- `include/embree3/rtcore.h` linked with `-lembree3`

Embree 4 remains preferred when both header trees exist.

## Implementation

- Runtime discovery now detects `include/embree4` or `include/embree3` under `RTDL_EMBREE_PREFIX`.
- The native prelude selects the available header with `__has_include`.
- A small compatibility shim normalizes `rtcIntersect1`, `rtcOccluded1`, `RTCIntersectArguments`, and `RTCOccludedArguments` across Embree 3 and Embree 4.
- The polygon intersect callback avoids `rtcInvokeIntersectFilterFromGeometry` when compiling against Embree 3 and directly calls RTDL's polygon filter function instead.
- Source-inspection tests now assert the graph path uses the RTDL Embree intersection shim, preserving the existing requirement that graph traversal is ray-intersection based and not point-query based.

## Pod Evidence

Pod: `root@69.30.85.180 -p 22072`

Embree 3 smoke:

```text
RTDL_EMBREE_PREFIX=/usr
rt.embree_version() -> (3, 12, 2)
examples/rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies 10 --output-mode summary
result: passed
```

Embree 4 smoke:

```text
RTDL_EMBREE_PREFIX=/opt
LD_LIBRARY_PATH=/opt/lib
rt.embree_version() -> (4, 4, 0)
examples/rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies 10 --output-mode summary
result: passed
```

## Boundary

This is a portability and validation unblocker, not a performance claim. It lets local Linux and cloud pods run Embree-backed RTDL apps with whichever supported Embree major version is installed. Performance reports must still record the exact Embree major/minor used.

