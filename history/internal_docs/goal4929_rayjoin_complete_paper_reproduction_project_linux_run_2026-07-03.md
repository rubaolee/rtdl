# Goal4929: Complete RayJoin Paper-Reproduction Project Linux Run

Date: 2026-07-03

## Purpose

Convert `Paper-reproduction-apps/rayjoin-paper/` from a set of RTDL scripts into
a complete paper-reproduction engineering project:

- include the patched author comparator program (`AuthorOfficial`);
- include reproducible public input acquisition and SHA verification;
- include RTDL Section 5.2, 5.3, and 5.7 runners;
- include a one-command public-sample runner;
- validate the whole project on the local Linux machine.

## Project Structure Added Or Hardened

Public project directory:

`Paper-reproduction-apps/rayjoin-paper/`

Important files:

- `README.md`: explains the complete project, comparator definition, run
  commands, generated directories, and claim boundaries.
- `data/public_sample_manifest.json`: public County x Soil input/answer URLs,
  byte sizes, and SHA-256 hashes.
- `author_patches/author_clean_compat_cuda12.patch`: author-source build
  compatibility patch.
- `author_patches/author_sos_t_reported.patch`: author-derived SoS
  reported-distance patch.
- `author_patches/author_duplicate_half_edge_contract.patch`: documented
  RTDL-defined duplicate-half-edge contract patch.
- `scripts/fetch_public_sample.py`: downloads and verifies public inputs.
- `scripts/apply_author_duplicate_contract_patch.py`: applies the duplicate
  half-edge contract to the author source because the historical patch is stored
  as an apply-patch transcript, not a clean git diff.
- `scripts/setup_author_official.sh`: clones pinned RayJoin source, builds local
  `gflags`/`glog` without `sudo`, applies patches, fixes CUDA arch for the
  current GPU, and builds `query_exec` / `polyover_exec`.
- `scripts/run_author_public_sample.sh`: runs AuthorOfficial on 5.2, 5.3, and
  5.7 public sample.
- `scripts/run_rtdl_public_sample.sh`: runs RTDL 5.2, 5.3, 5.7, and 5.7+Numba.
- `scripts/run_full_public_sample.sh`: one-command full public-sample runner.

## Linux Validation Environment

Machine: `192.168.1.20` (`lx1`)

GPU:

- NVIDIA GeForce GTX 1070
- compute capability 6.1
- driver 580.126.09

Toolchain:

- Python 3.12.3
- CMake 3.28.3
- CUDA 12.0
- OptiX prefix: `/home/lestat/vendor/optix-dev`

Linux working directory:

`/tmp/rtdl_rayjoin_complete_project_20260703`

## Checks Run

Static checks on Linux:

- Python compile check for all RayJoin project Python scripts: passed.
- `bash -n` for all RayJoin project shell scripts: passed.

Full command:

```bash
cd /tmp/rtdl_rayjoin_complete_project_20260703
OPTIX_PREFIX=/home/lestat/vendor/optix-dev \
CUDA_PREFIX=/usr/lib/cuda \
RAYJOIN_CUDA_ARCH=61 \
bash Paper-reproduction-apps/rayjoin-paper/scripts/run_full_public_sample.sh
```

The runner:

1. Downloaded and verified the public County x Soil inputs and answer file.
2. Built local `gflags` and `glog` under `_work/author_official/deps/`.
3. Cloned the author RayJoin source at commit
   `02bf6220d6d20b04af77ee20364eced75cc029c9`.
4. Applied the three documented author-comparator patches.
5. Built AuthorOfficial `query_exec` and `polyover_exec`.
6. Ran AuthorOfficial Section 5.2, 5.3, and 5.7.
7. Ran RTDL Section 5.2, 5.3, 5.7, and 5.7+Numba.

## Public Sample Data

Downloaded files:

| Role | File | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| poly1_county | `br_county_clean_25_odyssey_final.txt` | 12,826,522 | `cee9f41da48c6f072b0692843cc23804517e8928f46c6c84675fc9a3b1e5a0e7` |
| poly2_soil | `br_soil_ascii_odyssey_final.txt` | 9,543,616 | `525a6dda0e42c1ed63f30cd5ffe8e9283697f3c53076837a122ba098ad530d9f` |
| section57_answer | `br_countyXbr_soil_answer.txt` | 16,631,243 | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |

All manifest checks passed.

## Results

AuthorOfficial 5.7:

- output bytes: 16,631,243
- answer bytes: 16,631,243
- output SHA-256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`
- answer SHA-256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`
- byte-equal to public answer: `true`

RTDL:

| Section | Result |
| --- | --- |
| 5.2 LSI | count `20860`, observed total `2.812s` |
| 5.3 PIP | positive faces `255272`, observed total `1.459s` |
| 5.7 overlay | byte-equal to public answer, elapsed `5.399s` |
| 5.7 overlay + Numba | byte-equal to public answer, elapsed `5.456s` |

Final full-run checks:

```json
{
  "rtdl_section57_byte_equal": true,
  "rtdl_section57_numba_byte_equal": true,
  "author_section57_byte_equal": true
}
```

All three Section 5.7 outputs share the same SHA-256:

`464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`

## Numba Result

The Numba route is correct, but it is not a material whole-app acceleration on
this public sample.

In the second full-run:

- Python Section 5.7 elapsed: `5.399s`
- Numba Section 5.7 elapsed: `5.456s`
- Python writer phase: `2.273s`
- Numba writer phase: `2.146s`

Interpretation:

- Numba helps selected numeric app-layer writer planning work.
- The remaining cost is dominated by output-chain formatting and file emission,
  not by a large numeric loop that Numba can erase.
- No broad Numba speedup claim is authorized from this result.

## Fixes Made During Validation

Two packaging defects were found by the Linux run and fixed:

1. Shell executable-bit dependency:
   - Problem: `run_full_public_sample.sh` directly executed child scripts, which
     failed after Windows-to-Linux transfer without executable bits.
   - Fix: call child shell scripts through explicit `bash`.

2. Author setup metadata:
   - Problem: build logs were redirected into `author_setup.json`.
   - Fix: setup logs now go to `author_setup.log`; clean metadata is written to
     `author_setup.json`.

One author build dependency issue was also handled:

- Problem: local Linux lacked system `gflags/glog`, and no passwordless `sudo`
  was available.
- Fix: `setup_author_official.sh` now builds local `gflags` and `glog` under
  `_work/author_official/deps/` and passes their include/library paths to
  RayJoin CMake. The PTX compile rule also receives the local include path.

## Artifacts

Local artifacts copied from Linux:

`history/internal_docs/goal4929_rayjoin_complete_paper_reproduction_project_linux_run_2026-07-03_artifacts/`

Files:

- `full_summary.json`
- `author_setup.json`
- `author_official_summary.json`
- `rtdl_summary.json`
- `rerun.out`
- `rerun.err`

Remote working directory retained for inspection:

`/tmp/rtdl_rayjoin_complete_project_20260703`

## Claim Boundary

This validates the complete public-sample reproduction project packaging and
execution path.

Authorized:

- The project can fetch verified public sample inputs.
- The project can build the patched author comparator locally without `sudo`.
- The project can run AuthorOfficial and RTDL on Section 5.2, 5.3, and bounded
  public-sample Section 5.7.
- AuthorOfficial, RTDL, and RTDL+Numba all produce byte-identical Section 5.7
  output to the public answer on this sample.

Not authorized:

- No claim that all hidden Section 5.7 paper inputs are available.
- No all-eight-pair Section 5.7 claim from this public-sample run.
- No broad RayJoin-system speedup claim.
- No claim that Numba materially accelerates the full public-sample app.
