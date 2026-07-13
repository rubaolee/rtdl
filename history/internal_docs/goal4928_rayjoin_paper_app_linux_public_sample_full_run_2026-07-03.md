# Goal4928: RayJoin Paper-Reproduction App Linux Public-Sample Full Run

Date: 2026-07-03

## Purpose

Run the newly organized `Paper-reproduction-apps/rayjoin-paper` app seriously on the
local Linux machine, using real public RayJoin input data rather than toy fixtures.

This run covers:

- Section 5.2 LSI count: `section52_lsi.py`
- Section 5.3 PIP count: `section53_pip.py`
- Section 5.7 polygon overlay: `section57_overlay.py`
- Section 5.7 polygon overlay with Numba app-layer helpers:
  `section57_overlay_numba.py`

## Linux Environment

- Host: `192.168.1.20`
- Work directory on Linux: `/tmp/rtdl_rayjoin_app_full`
- Public data directory: `/tmp/rayjoin_public_sample`
- GPU: `NVIDIA GeForce GTX 1070`
- Driver: `580.126.09`
- CUDA compiler: `cuda_12.0.r12.0/compiler.32267302_0`
- Python packages:
  - `numpy 2.4.4`
  - `numba 0.65.1`

## Data Used

The run used the public RayJoin County x Soil sample listed in
`src/rtdsl/datasets.py`:

- `br_county_clean_25_odyssey_final.txt`
  - Source URL:
    `https://raw.githubusercontent.com/pwrliang/RayJoin/main/test/dataset/br_county_clean_25_odyssey_final.txt`
  - Linux path: `/tmp/rayjoin_public_sample/br_county_clean_25_odyssey_final.txt`
  - Size: `12,826,522` bytes
- `br_soil_ascii_odyssey_final.txt`
  - Source URL:
    `https://raw.githubusercontent.com/pwrliang/RayJoin/main/test/dataset/br_soil_ascii_odyssey_final.txt`
  - Linux path: `/tmp/rayjoin_public_sample/br_soil_ascii_odyssey_final.txt`
  - Size: `9,543,616` bytes
- `br_countyXbr_soil_answer.txt`
  - Source URL:
    `https://raw.githubusercontent.com/pwrliang/RayJoin/main/test/dataset/br_countyXbr_soil_answer.txt`
  - Linux path: `/tmp/rayjoin_public_sample/br_countyXbr_soil_answer.txt`
  - Size: `16,631,243` bytes
  - SHA256:
    `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`

This is the public County x Soil validation sample, not the hidden old Section
5.7 eight-pair paper input set.

## Build Provenance

The current Windows workspace sources were copied to Linux:

```text
/tmp/rtdl_rayjoin_app_full/src
/tmp/rtdl_rayjoin_app_full/Paper-reproduction-apps
/tmp/rtdl_rayjoin_app_full/Makefile
```

The OptiX native library was rebuilt from those copied sources on Linux:

```bash
cd /tmp/rtdl_rayjoin_app_full
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev CUDA_PREFIX=/usr/lib/cuda
```

Result:

```text
/tmp/rtdl_rayjoin_app_full/build/librtdl_optix.so
size: 2,858,104 bytes
```

Runtime environment:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIB=/tmp/rtdl_rayjoin_app_full/build/librtdl_optix.so
export RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR=/tmp/rayjoin_public_sample/cache
```

## Section 5.2 LSI

Command:

```bash
python3 Paper-reproduction-apps/rayjoin-paper/section52_lsi.py \
  --poly1 /tmp/rayjoin_public_sample/br_county_clean_25_odyssey_final.txt \
  --poly2 /tmp/rayjoin_public_sample/br_soil_ascii_odyssey_final.txt \
  --label br_county_soil \
  --output /tmp/rayjoin_public_sample/out/section52_lsi.json
```

Result:

| Metric | Value |
|---|---:|
| LSI count | `20,860` |
| Script observed total | `3.146539459s` |
| Shell wall time | `3.74s` |
| `load_poly1` | `0.626475858s` |
| `load_poly2` | `0.564904780s` |
| `prepare` | `0.952950834s` |
| `count` | `1.002207987s` |

Boundary:

- Uses public `prepare_planar_map_lsi_2d_optix`.
- Does not use `rtdsl.rayjoin_overlay`.
- No old hidden eight-pair Section 5.2 claim is made for this public sample.

Artifact copied locally:

```text
history/internal_docs/goal4928_linux_public_sample_outputs/section52_lsi.json
```

## Section 5.3 PIP

Command:

```bash
python3 Paper-reproduction-apps/rayjoin-paper/section53_pip.py \
  --poly1 /tmp/rayjoin_public_sample/br_county_clean_25_odyssey_final.txt \
  --poly2 /tmp/rayjoin_public_sample/br_soil_ascii_odyssey_final.txt \
  --label br_county_soil \
  --output /tmp/rayjoin_public_sample/out/section53_pip.json \
  --chunk-size 500000
```

Result:

| Metric | Value |
|---|---:|
| Direction | `poly2 vertices in poly1` |
| Base segments | `326,193` |
| Query points | `258,961` |
| Positive faces | `255,272` |
| Direction observed total | `1.722552205s` |
| Shell wall time | `3.27s` |
| Native traversal total | `0.001597862s` |

Boundary:

- Uses public `prepare_planar_map_point_location_2d_optix`.
- Does not use `rtdsl.rayjoin_overlay`.
- This is a count-only public primitive run. No author byte-output comparison is
  available for this standalone public sample command.

Artifact copied locally:

```text
history/internal_docs/goal4928_linux_public_sample_outputs/section53_pip.json
```

## Section 5.7 Overlay: Python App Layer

Command:

```bash
python3 Paper-reproduction-apps/rayjoin-paper/section57_overlay.py \
  --left /tmp/rayjoin_public_sample/br_county_clean_25_odyssey_final.txt \
  --right /tmp/rayjoin_public_sample/br_soil_ascii_odyssey_final.txt \
  --pair-name br_county_soil \
  --dataset-label available_bounded_pair \
  --output /tmp/rayjoin_public_sample/out/section57_overlay.txt \
  --author-output /tmp/rayjoin_public_sample/br_countyXbr_soil_answer.txt \
  --summary /tmp/rayjoin_public_sample/out/section57_overlay.json \
  --cache-dir /tmp/rayjoin_public_sample/cache
```

Correctness:

| File | Bytes | SHA256 |
|---|---:|---|
| Author answer | `16,631,243` | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |
| RTDL generated | `16,631,243` | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |

`byte_equal_to_author: true`

First run timings:

| Metric | Value |
|---|---:|
| Script elapsed | `6.210671995s` |
| Shell wall time | `6.74s` |
| LSI rows | `20,860` |
| Output lines | `737,830` |
| `load_pack_left` | `0.640839513s` |
| `load_pack_right` | `0.405148605s` |
| `lsi_public_rows` | `0.896276418s` |
| `intersection_reprojection` | `0.595816215s` |
| `sort_map0` | `0.441367178s` |
| `sort_map1` | `0.392919373s` |
| `prepare_point_location_map0_in_map1` | `0.706386776s` |
| `prepare_point_location_map1_in_map0` | `0.074429657s` |
| `vertex_pip_map0_in_map1` | `0.021302045s` |
| `vertex_pip_map1_in_map0` | `0.009849993s` |
| `output_chain_write` | `1.841559762s` |

Warm packed-cache Python rerun:

| Metric | Value |
|---|---:|
| Script elapsed | `5.459685053s` |
| Shell wall time | `5.98s` |
| `output_chain_write` | `2.274983740s` |

Artifacts copied locally:

```text
history/internal_docs/goal4928_linux_public_sample_outputs/section57_overlay.json
history/internal_docs/goal4928_linux_public_sample_outputs/section57_overlay_warm_python.json
```

## Section 5.7 Overlay: Numba App-Layer Helper

Command:

```bash
python3 Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py \
  --left /tmp/rayjoin_public_sample/br_county_clean_25_odyssey_final.txt \
  --right /tmp/rayjoin_public_sample/br_soil_ascii_odyssey_final.txt \
  --pair-name br_county_soil \
  --dataset-label available_bounded_pair \
  --output /tmp/rayjoin_public_sample/out/section57_overlay_numba.txt \
  --author-output /tmp/rayjoin_public_sample/br_countyXbr_soil_answer.txt \
  --summary /tmp/rayjoin_public_sample/out/section57_overlay_numba.json \
  --cache-dir /tmp/rayjoin_public_sample/cache
```

Correctness:

| File | Bytes | SHA256 |
|---|---:|---|
| Author answer | `16,631,243` | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |
| Numba generated | `16,631,243` | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |

`byte_equal_to_author: true`

First Numba run timings:

| Metric | Value |
|---|---:|
| Script elapsed | `6.006142804s` |
| Shell wall time | `6.77s` |
| `output_chain_write` | `2.455819990s` |
| `skip_plan` | `0.296720659s` |

Warm packed-cache Numba rerun:

| Metric | Value |
|---|---:|
| Script elapsed | `5.453846782s` |
| Shell wall time | `6.20s` |
| `output_chain_write` | `2.115155451s` |
| `skip_plan` | `0.018457569s` |

Artifacts copied locally:

```text
history/internal_docs/goal4928_linux_public_sample_outputs/section57_overlay_numba.json
history/internal_docs/goal4928_linux_public_sample_outputs/section57_overlay_warm_numba.json
```

## Numba Effect

On this Linux GTX 1070 public sample run, Numba did not produce a material
whole-app speedup.

The fairer warm-cache comparison is:

| Route | Script elapsed | Shell wall | Byte-equal |
|---|---:|---:|---|
| Python app layer | `5.459685053s` | `5.98s` | yes |
| Numba app-layer helper | `5.453846782s` | `6.20s` | yes |

Interpretation:

- The Numba route is correct.
- It gives a small local writer-phase improvement on the warm rerun:
  `2.274983740s -> 2.115155451s` (`~1.08x` for that phase).
- It does not create a meaningful end-to-end speedup here:
  `5.459685053s -> 5.453846782s` is effectively parity.
- The dominant remaining costs are still Python/app-layer overlay work:
  LSI row materialization, reprojection, sorting, point-location preparation, and
  output-chain text generation.

## Overall Result

The RayJoin paper-reproduction app now runs end-to-end on local Linux using the
real public County x Soil sample:

- Section 5.2 runs and reports LSI count `20,860`.
- Section 5.3 runs and reports PIP positive face count `255,272`.
- Section 5.7 Python route produces byte-identical output to the official
  answer.
- Section 5.7 Numba route also produces byte-identical output to the official
  answer.
- The public primitive boundary is preserved:
  - Section 5.2 uses `prepare_planar_map_lsi_2d_optix`.
  - Section 5.3/5.7 use `prepare_planar_map_point_location_2d_optix`.
  - The app does not import `rtdsl.rayjoin_overlay`.

No broad claim is authorized by this run:

- No full hidden eight-pair Section 5.7 claim.
- No broad RayJoin performance claim.
- No claim that Numba materially accelerates the whole app.
- No claim that this is an exact old hidden paper input set beyond the public
  County x Soil validation sample.

Exit label:

```text
completed_rayjoin_paper_app_linux_public_sample_full_run__section57_byte_equal__numba_whole_app_parity
```
