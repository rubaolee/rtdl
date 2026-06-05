# Goal3502 Overlay Area Single-Triangulation Payload Construction

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

Goal3502 removes duplicated CPU triangulation from the generic prepared
simple-polygon component payload path. The previous overlay-area runner
triangulated each Shapely-normalized component once to validate topology, then
called `prepare_simple_polygon_component_payload(...)`, which triangulated the
same component again while building the prepared payload. The new generic
constructor:

```text
prepare_simple_polygon_component_payload_from_triangles(...)
```

accepts already-triangulated simple components, source shape ids, vertex
counts, and component bounds. It builds the same prepared component records and
triangle tables without calling ear clipping a second time.

This is a generic prepared-payload improvement. It is not RayJoin-specific and
does not change the native engine boundary.

## Pod Evidence

Artifact:
`docs/reports/goal3502_overlay_area_single_triangulation_payload_construction_pod_2026-06-05.json`

Pod hardware/software:

- GPU: NVIDIA RTX A5000
- CuPy: 14.1.1
- Shapely: 2.1.2
- RTDL commit: `314f3eece958c9632babe96b59141d904508b91d`

Command shape:

```text
--active-shapes-only --device-active-shape-ordinals --bounds-positive-filter --component-bounds-filter --device-tile-task-planner --device-planner-repeats 5 --resident-cupy-inputs --executor-repeats 5 --single-triangulation-payload-evidence
```

Measured result:

- Relation rows: 4,543
- Bounds-positive candidate rows: 2,274
- Supported relation rows after component filtering: 2,149
- Component-pair rows: 4,524
- Tile tasks: 11,617
- Planned/processed triangle pairs: 4,070,240
- Exact total area: 26.08321766231046
- Observed total area: 26.08321767153826
- Total absolute error: 9.227800745748027e-09
- Max relation absolute error: 1.0414238360567651e-09
- Positive row count match: true

Compared with Goal3501 on the same pod route:

- Payload construction: 6.887s -> 3.951s
- Payload construction speedup: about 1.74x
- Absolute payload-construction saving: about 2.94s
- Executor best repeat: 0.01461s -> 0.01460s
- Device planner best repeat: 0.04407s -> 0.04422s

The improvement is exactly where expected: the CPU-owned payload construction
phase. The device planner and executor remain essentially unchanged, which is
important because Goal3502 does not alter their semantics.

## Boundary

Goal3502 still relies on Shapely/GEOS for topology normalization and oracle
validation in this benchmark runner. It does not construct polygon payloads in
native code, does not claim full overlay geometry output, does not claim true
zero-copy, and does not authorize public speedup or release wording.

The remaining dominant one-shot cost is still CPU-owned geometry repair plus
payload construction. The next deeper target is either reusable prepared-payload
residency/caching for repeated streams or a native/partner prepared-payload
construction route for supported simple-polygon topology.
