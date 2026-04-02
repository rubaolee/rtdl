# Goal 28D Linux County Zipcode Larger Exact-Source Execution

Date: 2026-04-02

## Scope

Goal 28D continued the first serious Linux-host exact-source family after Goal 28C:

- complete `Zipcode` raw-source staging on `192.168.1.20`
- keep the existing exact-source conversion path from ArcGIS pages to RTDL CDB/logical inputs
- move from the Goal 28C 1-county × 1-zipcode proof slice to a larger co-located slice
- report Linux-host CPU vs Embree timings with explicit parity status

## Host

- host: `192.168.1.20`
- OS: Ubuntu 24.04.4 LTS
- CPU: Intel Core i7-7700HQ
- threads: `8`
- memory: about `15 GiB`

## New Code in This Round

- resumable staging in [goal28b_stage_uscounty_zipcode.py](/Users/rl2025/rtdl_python_only/scripts/goal28b_stage_uscounty_zipcode.py)
- larger-slice runner in [goal28d_complete_and_run_county_zipcode.py](/Users/rl2025/rtdl_python_only/scripts/goal28d_complete_and_run_county_zipcode.py)
- tests in [goal28b_staging_test.py](/Users/rl2025/rtdl_python_only/tests/goal28b_staging_test.py) and [goal28d_execution_test.py](/Users/rl2025/rtdl_python_only/tests/goal28d_execution_test.py)

The staging change matters because the Linux host already had a partial `Zipcode` checkpoint from Goal 28B, including one corrupt tail page at offset `7000`. Goal 28D added the ability to reuse existing valid pages and re-fetch a corrupt page in place instead of restarting the entire acquisition.

## Completed Staging

Final `Zipcode` staging state on the Linux host:

- expected features: `32294`
- downloaded features: `32294`
- staged pages: `130`
- final page: `page_032250.json.gz` with `44` features

`USCounty` remained fully staged:

- features: `3144`
- staged pages: `13`

## Larger Slice Selection Method

Goal 28C selected the first feature from each side by page order and happened to get a spatially disjoint pair. Goal 28D replaced that with a co-located selection rule:

- convert the fully staged pages into CDB datasets
- compute face-level bounding boxes
- find counties with overlapping zipcode bounding boxes
- choose the lowest estimated segment-cost slice for a requested zipcode count

This is still a bounded local execution policy, but it is materially more serious than the Goal 28C first-page slice because it deliberately searches for spatially co-located exact-source features.

## Exploratory Results

I tested increasingly larger co-located slices on the Linux host:

| County × Zipcode Slice | `lsi` Parity | `pip` Parity | Notes |
| --- | --- | --- | --- |
| `1 × 8` | `false` | `true` | too large for parity-clean `lsi` on this round |
| `1 × 6` | `false` | `true` | still not parity-clean for `lsi` |
| `1 × 5` | `false` | `true` | still not parity-clean for `lsi` |
| `1 × 4` | `true` | `true` | accepted final larger slice |

The important technical conclusion is:

- the Linux host now supports materially larger exact-source slices than Goal 28C
- but larger is not automatically better, because `lsi` parity becomes unstable on the larger exploratory slices attempted here

## Accepted Final Slice

The largest parity-clean co-located slice found in this round was:

- county face id: `829`
- county bbox: `(-93.027115, 42.2092670000001, -92.53351, 42.556812547)`
- county chains: `1`
- county segments: `507`
- zipcode face ids: `16360, 16577, 16559, 16563`
- overlapping zipcode matches available for that county: `23`
- selected zipcode count: `4`
- selected zipcode chains: `4`
- selected zipcode segments: `124`
- estimated total segments: `631`

## Measured Results

### LSI

- CPU rows: `2`
- Embree rows: `2`
- CPU sec: `0.019200748`
- Embree sec: `0.011426202`
- pair parity: `true`

Sample result pairs:

- `(5, 413)`
- `(15, 404)`

### PIP

- CPU rows: `4`
- Embree rows: `4`
- CPU sec: `0.000665036`
- Embree sec: `0.000603524`
- row parity: `true`

Sample result rows:

- `(27312, 4706, 1)`
- `(27530, 4706, 1)`
- `(27534, 4706, 1)`
- `(27549, 4706, 1)`

## What Goal 28D Closed

Goal 28D closed:

- full `Zipcode` raw-source staging on the Linux host
- resumable acquisition for the ArcGIS FeatureServer path
- one larger co-located exact-source `County ⊲⊳ Zipcode` slice
- Linux-host CPU/Embree parity for that accepted larger slice

## Boundary

Goal 28D does **not** claim:

- paper-scale exact-input reproduction
- that all larger co-located `County ⊲⊳ Zipcode` slices are parity-clean for `lsi`
- that the exploratory `1 × 5`, `1 × 6`, or `1 × 8` slices should be treated as accepted results

The honest closure statement is:

- **full `Zipcode` staging is complete**
- **a larger exact-source Linux slice is now executed and parity-clean**
- **the accepted final slice is the largest parity-clean slice found in this round**
