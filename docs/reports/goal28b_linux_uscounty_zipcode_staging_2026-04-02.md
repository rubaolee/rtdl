# Goal 28B First Slice: Linux USCounty/Zipcode Raw-Source Staging

Date: 2026-04-02

## Scope

This report records the first serious Linux-host exact-source staging slice for the RayJoin `County ⊲⊳ Zipcode` family on `192.168.1.20`.

This slice closes:

- live ArcGIS FeatureServer verification for the `USCounty` and `Zipcode` source layers
- reproducible raw-source staging code in the RTDL repo
- a real Linux-host staging run with measured payload sizes and paging behavior

This slice does **not** yet close:

- conversion from ArcGIS JSON into RayJoin-compatible CDB inputs
- exact-input `lsi` or `pip` execution on the Linux host
- full Zipcode-family download completion

## Host

- host: `192.168.1.20`
- OS: Ubuntu 24.04.4 LTS
- CPU: Intel Core i7-7700HQ
- threads: `8`
- memory: about `15 GiB`

## Verified Source Layers

The live ArcGIS REST metadata and count queries confirmed:

| Asset | Service URL | Geometry | Max Record Count | Feature Count |
| --- | --- | --- | --- | --- |
| `uscounty_feature_layer` | `https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_Counties/FeatureServer/0` | `esriGeometryPolygon` | `2000` | `3144` |
| `zipcode_feature_layer` | `https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_ZIP_Code_Areas_anaylsis/FeatureServer/0` | `esriGeometryPolygon` | `2000` | `32294` |

## New Repo Tooling

The staging slice added:

- script: `/Users/rl2025/rtdl_python_only/scripts/goal28b_stage_uscounty_zipcode.py`
- service-layer registry and query helpers in:
  - `/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py`
- exports in:
  - `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- tests in:
  - `/Users/rl2025/rtdl_python_only/tests/goal28b_staging_test.py`

The script stages paginated FeatureServer pages plus metadata manifests under a chosen output directory.

## Host Probe Results

Before the full staging run, the host was used to measure the live payload behavior.

### County, `1000` features, `f=geojson`

- payload bytes: `115506107`
- fetch time: `13.408 s`
- JSON decode time: `1.592 s`

This was too heavy for a practical first Linux staging run.

### County, `100` features

`f=json`

- payload bytes: `9911720`
- fetch time: `3.881 s`

`f=geojson`

- payload bytes: `9916093`
- fetch time: `4.811 s`

These probes showed that:

- `f=json` is slightly smaller and faster than `f=geojson` on this host path
- a practical first serious staging run should use:
  - `f=json`
  - paginated requests
  - a smaller page size than the layer maximum

## Linux Staging Run

The Linux-host run used:

```sh
PYTHONPATH=src:. python3 scripts/goal28b_stage_uscounty_zipcode.py \
  --output-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact \
  --host-label 192.168.1.20 \
  --page-size 250 \
  --sleep-sec 0.02 \
  --response-format json \
  --gzip
```

Observed checkpoint:

- `USCounty` completed fully
- `Zipcode` progressed cleanly through offset `7000`
- the run was then stopped intentionally to record the first serious staging slice without spending the whole round on a long raw download

## Staged Outputs on Linux

Directory:

- `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact`

Observed checkpoint contents:

| Asset | Highest Observed Page Offset | Approximate Downloaded Features | Directory Size |
| --- | --- | --- | --- |
| `uscounty_feature_layer` | `3000` | full set (`3144`) | `92M` |
| `zipcode_feature_layer` | `7000` | at least `7250` requested / paged | `48M` |

Observed page files:

- county last page:
  - `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer/page_003000.json.gz`
- zipcode checkpoint page:
  - `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer/page_007000.json.gz`

## What This Means

This Linux host is suitable for serious raw-source staging and later exact-input conversion work, but the Zipcode source is still large enough that the full pull is a non-trivial step even on the independent workstation.

The important positive result is:

- the host can sustain live paginated ArcGIS source downloads
- the `County ⊲⊳ Zipcode` family is no longer just a paper-reference target
- RTDL now has a reproducible acquisition path for the first serious exact-source family

## Boundary

This report does **not** claim:

- that RayJoin exact-input CDB data has been reconstructed already
- that the full `County ⊲⊳ Zipcode` pair has been executed on the Linux host
- that the full Zipcode raw-source pull is finished

The correct closure statement for this slice is:

- **raw-source acquisition/staging path established**
- **USCounty staged fully**
- **Zipcode staging proven and partially completed**
- **CDB conversion and Linux exact-input execution remain the next slice**
