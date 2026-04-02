# Goal 28D Implementation Report (Codex)

Date: 2026-04-02

## Implemented Changes

- added resumable raw-source staging support to `goal28b_stage_uscounty_zipcode.py`
- resumable staging now reuses valid existing pages and re-fetches a corrupt tail page instead of failing the whole round
- added regression coverage for:
  - reused existing pages
  - corrupt-tail fallback re-fetch
- added `goal28d_complete_and_run_county_zipcode.py`
  - converts full staged `USCounty` and full staged `Zipcode`
  - computes face-level bounding boxes
  - selects a co-located county/zipcode slice by bbox overlap and estimated segment cost
  - runs `lsi` and `pip` through both `run_cpu(...)` and `run_embree(...)`
- added `goal28d_execution_test.py` for slice selection and face filtering helpers

## Linux Host Results

Host:

- `192.168.1.20`
- Ubuntu 24.04.4 LTS
- `8` CPU threads
- about `15 GiB` RAM

Completed raw-source staging:

- `USCounty`: `3144` features, `13` staged pages
- `Zipcode`: `32294` features, `130` staged pages

Exploratory larger-slice search:

- `target_zip_matches=8`:
  - `lsi` parity failed
- `target_zip_matches=6`:
  - `lsi` parity failed
- `target_zip_matches=5`:
  - `lsi` parity failed
- `target_zip_matches=4`:
  - `lsi` parity passed
  - `pip` parity passed

Chosen parity-clean larger slice (`goal28d_try_4`):

- county face id: `829`
- county chains: `1`
- county segments: `507`
- zipcode selected faces: `16360, 16577, 16559, 16563`
- zipcode chains: `4`
- zipcode selected segments: `124`
- estimated total segments: `631`

Measured timings on the chosen slice:

- `lsi`
  - CPU rows: `2`
  - Embree rows: `2`
  - CPU sec: `0.019200748`
  - Embree sec: `0.011426202`
  - parity: `true`
- `pip`
  - CPU rows: `4`
  - Embree rows: `4`
  - CPU sec: `0.000665036`
  - Embree sec: `0.000603524`
  - parity: `true`

## Honest Boundary

- Goal 28D completed full `Zipcode` staging on the Linux host.
- Goal 28D closed one larger exact-source execution slice beyond Goal 28C.
- Goal 28D did not establish that arbitrary larger co-located slices are parity-clean for `lsi`; the exploratory `k=5+` runs were not parity-clean.
- The accepted final slice is therefore the largest parity-clean co-located slice found in this round, not the numerically largest slice attempted.
