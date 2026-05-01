# Goal864 Segment/Polygon Gate Review Packet

- source goal: `Goal807 segment/polygon OptiX native-mode gate`
- dataset: `authored_segment_polygon_minimal`
- include_postgis: `False`
- gate status: `non_strict_recorded_gaps`
- recommended status: `needs_real_optix_artifact`
- required records ok: `False`
- required parity ok: `False`

## Records

| Label | Status | OptiX mode | Seconds | Parity vs CPU | Error |
|---|---|---|---:|---:|---|
| cpu_python_reference | ok | not_applicable | 0.000118 | True |  |
| optix_host_indexed | unavailable_or_failed |  | 0.000472 | False | FileNotFoundError |
| optix_native | unavailable_or_failed |  | 0.000232 | False | FileNotFoundError |

## Strict Failures

- optix_host_indexed did not run
- optix_native did not run

## Boundary

This packet interprets a Goal807 gate artifact only. It does not promote segment/polygon to an active RTX claim path and does not authorize a public speedup claim.
