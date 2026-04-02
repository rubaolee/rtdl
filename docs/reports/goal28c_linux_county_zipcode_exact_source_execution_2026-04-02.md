# Goal 28C: Linux County/Zipcode Exact-Source Conversion and Execution

Date: 2026-04-02

## Scope

This report closes the first executable Linux-host exact-source `County ⊲⊳ Zipcode` slice from the staged ArcGIS pages on `192.168.1.20`.

This round closes:

- full `USCounty` ArcGIS-page to CDB conversion on Linux
- staged-checkpoint `Zipcode` ArcGIS-page to CDB conversion on Linux
- first Linux execution of:
  - `county_zip_join_reference`
  - `point_in_counties_reference`
- CPU vs Embree parity for a feature-limited exact-source execution subset

This round does **not** close:

- full Zipcode source acquisition
- full paper-scale exact-input `County ⊲⊳ Zipcode` execution
- topologically exact polygon-face reconstruction from the staged raw sources

## Design Rule Used In This Round

ArcGIS polygon pages were mapped into RTDL CDB chains using this explicit rule:

- one ArcGIS `ring` becomes one CDB chain
- `left_face_id` is the source feature `OBJECTID`
- `right_face_id` is `0`
- multipart features therefore become multiple chains sharing the same face id

This is exact-source at the raw-data level, but the current polygon execution path is still a chain-derived approximation rather than a full topological face rebuild.

## New Repo Work

This round added:

- ArcGIS-page conversion helpers in:
  - `/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py`
- new public exports in:
  - `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- Linux conversion/execution script:
  - `/Users/rl2025/rtdl_python_only/scripts/goal28c_convert_and_run_county_zipcode.py`
- conversion tests:
  - `/Users/rl2025/rtdl_python_only/tests/goal28c_conversion_test.py`

This round also fixed two Linux portability problems:

- Embree dynamic-library build path in:
  - `/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py`
- missing `<stdexcept>` include in:
  - `/Users/rl2025/rtdl_python_only/src/native/rtdl_embree.cpp`

## Host

- host: `192.168.1.20`
- OS: Ubuntu 24.04.4 LTS
- CPU: Intel Core i7-7700HQ
- threads: `8`
- memory: about `15 GiB`

## Converted Linux Artifacts

Directory:

- `/home/lestat/work/rayjoin_sources/goal28c_exact_source_run`

Observed files:

| File | Size | Meaning |
| --- | --- | --- |
| `uscounty_full.cdb` | `418M` | full exact-source county conversion |
| `zipcode_partial.cdb` | `277M` | valid staged-checkpoint zipcode conversion |
| `uscounty_exec.cdb` | `72K` | feature-limited county execution subset |
| `zipcode_exec.cdb` | `192K` | feature-limited zipcode execution subset |
| `goal28c_summary.json` | `1.9K` | machine-readable result summary |
| `goal28c_summary.md` | `1.1K` | human-readable result summary |

## Converted Input Counts

Full county conversion:

- source pages used: `13`
- feature count: `3144`
- chain count: `12273`

Zipcode checkpoint conversion:

- valid staged pages used: `28`
- feature count: `7000`
- chain count: `12834`

The Zipcode count is `7000` rather than `7250` because the interrupted staging run left a truncated tail page; Goal 28C explicitly ignored the invalid tail and used only valid staged pages.

## Execution Subset

The first executable parity-checkable exact-source subset was:

- county execution feature limit: `1`
- zipcode execution feature limit: `1`
- county execution chain count: `1`
- zipcode execution chain count: `6`

This tiny subset was necessary because the full exact-source boundary geometry is too large for the current pure-Python `lsi_cpu` reference path.

For scale:

- full county segments: `12474300`
- one zipcode feature still produced `5600` segments

So the first Linux exact-source execution slice had to be chosen at the feature level rather than at the full converted-dataset level.

## Execution Command

The Linux host run used:

```sh
PYTHONPATH=src:. python3 scripts/goal28c_convert_and_run_county_zipcode.py \
  --county-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer \
  --zipcode-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer \
  --output-dir /home/lestat/work/rayjoin_sources/goal28c_exact_source_run \
  --host-label 192.168.1.20 \
  --county-exec-max-features 1 \
  --zipcode-exec-max-features 1
```

CPU in this report means:

- `rt.run_cpu(...)`, the current pure-Python RTDL reference path

Embree in this report means:

- `rt.run_embree(...)`, the native RTDL Embree backend on the Linux host

## Results

### LSI

- cpu rows: `0`
- embree rows: `0`
- cpu sec: `3.626239`
- embree sec: `1.407477`
- pair parity: `True`

Interpretation:

- the first county feature and first zipcode feature chosen for the execution subset are spatially disjoint
- observed bounding boxes:
  - county: `(-86.921237, 32.307574, -86.411172, 32.7082130000001)`
  - zipcode: `(-160.431152, 58.678617, -160.373152, 58.749838)`
- so the zero-row result is expected rather than a runtime defect

### PIP

- cpu rows: `6`
- embree rows: `6`
- cpu sec: `0.003355`
- embree sec: `0.002007`
- row parity: `True`

## What This Means

Goal 28C proves that:

- RTDL can convert real staged `USCounty` and `Zipcode` ArcGIS source pages into RTDL-readable CDB files
- Linux-host RTDL Embree execution works on converted exact-source inputs
- CPU and Embree agree on the first exact-source feature-limited slice for both `lsi` and `pip`
- the Linux host is now a real execution platform for future larger exact-source slices, not just a staging machine

## Boundary

This report does **not** claim:

- full paper-scale exact-input execution for `County ⊲⊳ Zipcode`
- full Zipcode acquisition completeness
- topologically exact polygon reconstruction

The correct closure statement is:

- **full county exact-source conversion complete**
- **staged-checkpoint zipcode exact-source conversion complete**
- **first Linux exact-source execution slice complete**
- **larger exact-source execution still requires a stronger execution strategy than the current pure-Python `lsi_cpu` path**
