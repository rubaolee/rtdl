# Goal3504 Overlay Area Parallel Payload Preparation

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

Goal3504 adds an opt-in parallel CPU preparation route for the generic
simple-polygon overlay-area payload path:

```text
--payload-workers N --parallel-payload-prepare-evidence
```

Each selected shape is independent during Shapely/GEOS repair and prepared
component extraction. The new route uses worker processes to build per-shape
oracle geometry, extract simple components, keep the single triangulation from
Goal3502, and return serialized Shapely geometry plus prepared component
triangles. The main process reconstructs the geometry map for oracle validation
and constructs the same `PreparedSimplePolygonComponentPayload` tables.

This is still a generic prepared-payload route. It does not add app-specific
engine logic and it does not change the device tile planner or executor.

## Pod Evidence

Artifact:
`docs/reports/goal3504_overlay_area_parallel_payload_prepare_pod_2026-06-05.json`

Pod hardware/software:

- GPU: NVIDIA RTX A5000
- CuPy: 14.1.1
- Shapely: 2.1.2
- RTDL commit: `024f3137294b13513300b3ed4935fe8fa2515d3b`

Command shape:

```text
--active-shapes-only --device-active-shape-ordinals --bounds-positive-filter --component-bounds-filter --device-tile-task-planner --device-planner-repeats 5 --resident-cupy-inputs --executor-repeats 5 --single-triangulation-payload-evidence --payload-workers 8 --parallel-payload-prepare-evidence
```

Measured result:

- Relation rows: 4,543
- Bounds-positive candidate rows: 2,274
- Supported relation rows after component filtering: 2,149
- Component-pair rows: 4,524
- Tile tasks: 11,617
- Planned/processed triangle pairs: 4,070,240
- Exact total area: 26.08321766231046
- Observed total area: 26.083217671538264
- Total absolute error: 9.227804298461706e-09
- Max relation absolute error: 1.0414238360567651e-09
- Positive row count match: true

Preparation progression on the same public-CDB route:

| Goal | Geometry build | Payload build | Combined geometry+payload |
| --- | ---: | ---: | ---: |
| Goal3501 component-bounds filter | 0.920s | 6.889s | 7.810s |
| Goal3502 single-triangulation payload | 1.107s | 3.951s | 5.058s |
| Goal3504 parallel payload prepare, 8 workers | 0.000s | 0.000s | 1.479s |

The Goal3504 combined preparation time is about 3.42x faster than Goal3502 and
about 5.28x faster than Goal3501 for the geometry+payload preparation section.
The timing is combined because worker processes perform geometry repair and
component extraction together.

The downstream runtime phases remain essentially unchanged:

- Device planner best repeat: 0.0545s
- CuPy tile-task executor best repeat: 0.0150s

The planner is slightly slower in this run than the Goal3501/3502 best repeat,
but it is still a small phase compared with the setup work, and the exact area
results match the same Shapely/GEOS oracle.

## Boundary

This goal does not make prepared-payload construction device-native and does
not claim true residency or true zero-copy. It is an opt-in CPU parallel
preparation route for the current benchmark runner. It does not authorize
release, public speedup wording, broad RT-core claims, full overlay completion,
or app-specific native-engine behavior.

The next deeper target is still a native or partner prepared-payload
construction path for supported simple-polygon topology, or a reusable prepared
payload residency/cache path for repeated relation streams.
