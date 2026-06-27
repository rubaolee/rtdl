# Goal 28C: Linux County/Zipcode Exact-Source Conversion and Execution

Date: 2026-04-02

## Goal

Use the already staged Linux-host ArcGIS source pages for `USCounty` and `Zipcode` to build the first executable exact-source `County ⊲⊳ Zipcode` slice on `192.168.1.20`.

## Scope

This goal is intentionally narrower than full exact-input paper reproduction.

It aims to close:

- conversion from staged ArcGIS polygon pages into RTDL-readable CDB chain files
- first Linux-host `lsi` and `pip` runs using those converted exact-source inputs
- a report that clearly distinguishes:
  - exact-source full county
  - exact-source partial zipcode checkpoint
  - current CDB-to-runtime approximation boundary

## Honest Boundary

This goal is allowed to close if:

- `USCounty` staged pages are converted fully into a CDB file
- the staged `Zipcode` checkpoint pages are converted into a CDB file
- RTDL executes:
  - `county_zip_join_reference` on Linux using converted county + zipcode chain-derived segments
  - `point_in_counties_reference` on Linux using converted zipcode chain-derived probe points and converted county chain-derived polygons
- CPU and Embree results are compared for the same converted inputs
- the final report is explicit that:
  - the county side is full exact-source
  - the zipcode side is partial exact-source from the current checkpoint
  - polygon reconstruction remains the current chain-derived approximation, not a topologically exact face rebuild

This goal does **not** require:

- full `Zipcode` source download completion
- full paper-scale `County ⊲⊳ Zipcode` execution unchanged
- final Table 3 publication

## Deliverables

- ArcGIS-page-to-CDB conversion code in the repo
- tests for the conversion path
- a Linux execution script for the first exact-source slice
- a host-backed report

## Co-Working Rule

- Codex implements and integrates
- Claude reviews the plan and the implementation before closure
- Gemini monitors each stage and verifies the declared boundary
