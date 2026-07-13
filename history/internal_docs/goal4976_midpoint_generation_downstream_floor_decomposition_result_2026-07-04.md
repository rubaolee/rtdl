# Goal4976 Result: Midpoint Generation Downstream Floor Decomposition

Date: 2026-07-04

## Verdict Requested

`completed_midpoint_decomposition_pack_boundary_dominated`

## Summary

Goal4976 decomposed `midpoint_points_columnar` on the top4 County x Zipcode representative binary route. The largest downstream phase after Goal4974 was midpoint query-point generation, but the decomposition shows that the math is not the bottleneck.

The bottleneck is host packing into `RtdlRayjoinCdbScaledPoint` records.

## POD Evidence

POD:

- `root@213.173.108.6 -p 10626`

Input:

- left: `Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_county.cdb`
- right: `Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_zipcode.cdb`

Route:

- `--device-columnar`
- `--compiled-group`
- `--bounded-exact-lsi-device-columns --bounded-exact-lsi-capacity 600000`
- `--point-location-device-face-columns`

Artifact:

- `history/internal_docs/goal4976_midpoint_generation_decomposition_artifacts_2026-07-04/midpoint_decomposition_summary.json`

## Decomposition

| Phase | Map0 | Map0 share | Map1 | Map1 share |
|---|---:|---:|---:|---:|
| total midpoint generation | 0.698236s | 100.00% | 0.614120s | 100.00% |
| adjacent owner scan | 0.004157s | 0.60% | 0.001495s | 0.24% |
| scaled midpoint arrays | 0.009055s | 1.30% | 0.005108s | 0.83% |
| world/finite filter | 0.000983s | 0.14% | 0.000745s | 0.12% |
| pack scaled points | 0.683992s | 97.96% | 0.606735s | 98.80% |

## Interpretation

The midpoint arithmetic is already cheap:

- adjacency/owner scan is under 5ms for map0 and under 2ms for map1
- scaled midpoint arithmetic is under 10ms for map0 and under 6ms for map1
- world-coordinate reconstruction / finite filtering is under 1ms

The remaining ~1.29s is almost entirely the host packing boundary:

```text
base.pack_rayjoin_cdb_scaled_points(ids=ids, x=mx, y=my, sx=sx, sy=sy)
```

That helper converts NumPy arrays into Python lists and then into a ctypes array of `RtdlRayjoinCdbScaledPoint`. This is exactly the kind of per-row Python host construction the binary route is supposed to remove.

## What This Proves

1. Optimizing midpoint math itself will not materially move the floor.
2. More NumPy/Numba midpoint arithmetic work is the wrong next target.
3. The next real target is the scaled query-point handoff into point-location/PIP.

## What This Does Not Prove

- It does not implement device-resident midpoint query points.
- It does not remove the host pack/upload boundary.
- It does not authorize zero-copy wording.
- It does not compare against the author text-output route.

## Next Goal Direction

Goal4977 should replace or bypass the per-row ctypes scaled-point packing path.

Two possible generic routes:

1. **Fast host column pack route**:
   - add a vectorized packed scaled-point constructor from contiguous NumPy arrays
   - still host-resident, but avoids Python list/per-row object construction
   - lower risk, likely immediate win

2. **True device/columnar scaled query-point route**:
   - expose a generic directed point-location prepared-points front door from columnar scaled midpoint arrays
   - feed PIP without creating per-point Python/ctypes records
   - higher value, but requires native/Python API work and stricter genericity review

Given the decomposition, the correct first implementation is likely route 1 as a low-risk gate, followed by route 2 if the host pack boundary remains too expensive.

## Local Validation

Commands:

```text
py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
$env:PYTHONPATH='src'; py -m unittest tests.goal4974_point_location_device_face_columns_route_test
```

Result:

```text
Ran 3 tests in 0.010s
OK
```

## Exit Label

`completed_midpoint_decomposition_pack_boundary_dominated`
