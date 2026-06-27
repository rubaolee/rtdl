# Goal 28B First Slice Implementation Report

Date: 2026-04-02
Round: 2026-04-02-goal-28b-linux-uscounty-zipcode-staging

## Implemented

- added live FeatureServer registry and query helpers in:
  - `/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py`
- exported those helpers in:
  - `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- added the Linux staging script:
  - `/Users/rl2025/rtdl_python_only/scripts/goal28b_stage_uscounty_zipcode.py`
- added tests:
  - `/Users/rl2025/rtdl_python_only/tests/goal28b_staging_test.py`
- wrote the host-backed report:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal28b_linux_uscounty_zipcode_staging_2026-04-02.md`

## Host-Run Evidence

Host:

- `192.168.1.20`
- Ubuntu 24.04.4 LTS
- Intel i7-7700HQ
- `8` threads
- about `15 GiB` RAM

Verified layer counts:

- `USCounty`: `3144`
- `Zipcode`: `32294`

Measured payload behavior on host:

- `County`, `1000` features, `f=geojson`:
  - `115506107` bytes
  - `13.408 s` fetch
  - `1.592 s` decode
- `County`, `100` features:
  - `f=json`: `9911720` bytes, `3.881 s`
  - `f=geojson`: `9916093` bytes, `4.811 s`

Actual Linux run used:

```sh
PYTHONPATH=src:. python3 scripts/goal28b_stage_uscounty_zipcode.py \
  --output-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact \
  --host-label 192.168.1.20 \
  --page-size 250 \
  --sleep-sec 0.02 \
  --response-format json \
  --gzip
```

Observed checkpoint before intentionally stopping the long Zipcode pull:

- `USCounty` fully staged through offset `3000`
- `Zipcode` staged through offset `7000`
- directory sizes:
  - county: `92M`
  - zipcode checkpoint: `48M`

## Verification

Local verification:

- `PYTHONPATH=src:. python3 -m unittest tests.goal28b_staging_test`
- `python3 -m py_compile scripts/goal28b_stage_uscounty_zipcode.py src/rtdsl/datasets.py src/rtdsl/__init__.py`

## Claimed Result

This round closes:

- reproducible raw-source staging for the first serious exact-source RayJoin family on Linux

This round does not close:

- CDB conversion
- full Zipcode pull completion
- exact-input `lsi` or `pip` execution on Linux
