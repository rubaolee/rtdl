# Goal3488 - Overlay-Area Prepared Payload Feasibility Probe

## Status

Implemented and pod-validated on the public-CDB active relation stream.

Goal3488 adds a public-CDB feasibility probe for the Goal3483-3486 prepared
payload path.

## Question

The current prepared payload supports no-hole simple polygon components. Before
scaling the CuPy tiled prototype to the full public-CDB relation stream, we need
to know how much of that stream can be represented by this payload today.

This probe measures:

- active RTDL relation row count;
- how many source shapes normalize to prepared no-hole simple components;
- how many active relation rows are supported by the current payload;
- how much exact Shapely/GEOS area those supported rows cover;
- why unsupported rows are unsupported.

## Script

- `scripts/goal3488_overlay_area_prepared_payload_feasibility_probe.py`

The script uses RTDL/OptiX only to produce active relation ordinals. It uses
Shapely/GEOS as an external CPU oracle/classifier, not as an RTDL runtime
dependency.

## Boundary

This is a feasibility classifier, not an overlay-area runtime implementation.
It does not authorize release packaging, public speedup wording, RT-core
speedup wording, true-zero-copy wording, paper reproduction claims, hidden
dispatch, automatic partner selection, full overlay completion claims, or
app-specific native engine behavior.

## Pod Evidence

Artifact:

- `docs/reports/goal3488_overlay_area_prepared_payload_feasibility_pod_2026-06-05.json`

Pod result:

- active relation rows: `4,543`;
- supported prepared-payload rows: `4,539`;
- unsupported rows: `4`;
- all unsupported rows are zero-area rows;
- supported positive-area rows: `1,090 / 1,090`;
- supported exact area: `26.08321766231043 / 26.08321766231043`;
- supported area fraction: `1.0`;
- supported positive-row fraction: `1.0`;
- max supported triangle pairs in one row: `318,096`.

Interpretation: the current no-hole prepared simple component payload is
sufficient for the scalar exact-area target on the positive public-CDB rows, but
the row with `318,096` triangle pairs makes bounded tiling mandatory before
scaling the CuPy prototype beyond fixtures.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3488_overlay_area_prepared_payload_feasibility_probe_test`

Pod validation ran the script on the public CDB relation stream and saved:

- `docs/reports/goal3488_overlay_area_prepared_payload_feasibility_pod_2026-06-05.json`
