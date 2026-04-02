# Goal 28C Pre-Implementation Report

Date: 2026-04-02
Round: 2026-04-02-goal-28c-linux-county-zipcode-exact-source-execution

## Starting Point

Goal 28B already established:

- live ArcGIS FeatureServer source layers for `USCounty` and `Zipcode`
- reproducible staging code
- full `USCounty` staging on `192.168.1.20`
- partial `Zipcode` staging through offset `7000`

## Proposed Implementation

1. add a converter from staged ArcGIS polygon pages (`json` / `json.gz`) into RTDL `CdbDataset`
2. expose a public helper for converting CDB chains into logical polygons
3. add tests for the converter on synthetic ArcGIS-like payloads
4. add a Linux execution script that:
   - loads converted county and zipcode CDB files
   - derives `lsi` segment inputs
   - derives `pip` inputs from zipcode chain-start probe points and county chain-derived polygons
   - runs CPU and Embree
   - writes a JSON/Markdown result summary
5. run that script on `192.168.1.20`
6. write the host-backed report

## Main Risk

The conversion is exact-source only at the raw-data level. The current polygon path still uses chain-derived polygon reconstruction rather than a full topological face rebuild, so the report must state that explicitly.
