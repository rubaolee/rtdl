# Goal 33 Linux Post-Fix Verification

Date: 2026-04-02

## Scope

Goal 33 verified that the Goal 31 correctness fix and Goal 32 sort-sweep optimization for local `lsi` also hold on the Linux Embree host `192.168.1.20`, not only on this Mac.

This was a verification/report round. It did not change RTDL code.

## Host

- host: `192.168.1.20`
- OS: Ubuntu 24.04.4 LTS
- CPU: Intel Core i7-7700HQ
- threads: `8`
- memory: about `15 GiB`

## Preparation

On the Linux host I:

- preserved the pre-existing dirty checkout with `git stash push -u -m 'pre-goal33-linux-verification'`
- pulled the current main branch to include Goal 31 and Goal 32
- rebuilt the native backend with `make build`

Important boundary:

- the stash was created only to avoid losing remote local work before pulling the new commits
- Goal 33 does not claim that the remote host checkout was kept permanently clean after pull; it claims that the verification was run against the current published RTDL state

## Linux Regression Tests

Command run on `192.168.1.20`:

```sh
PYTHONPATH=src:. python3 -m unittest \
  tests.goal31_lsi_gap_closure_test \
  tests.goal32_lsi_sort_sweep_test
```

Observed result:

```text
Ran 4 tests in 2.266s

OK (skipped=1)
```

Interpretation:

- Goal 31 minimal exact-source reproducer is parity-clean on Linux
- Goal 32 localized synthetic sort-sweep regression is parity-clean on Linux
- the frozen `k=5` snapshot test was skipped because the local build snapshot files were not present in that checkout

## Exact-Source Larger-Slice Re-Execution

I then reran the old Goal 28D larger-slice driver on the Linux host using the staged full `USCounty` and `Zipcode` ArcGIS pages in:

- `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer`
- `/home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer`

The same driver was used:

- [goal28d_complete_and_run_county_zipcode.py](/Users/rl2025/rtdl_python_only/scripts/goal28d_complete_and_run_county_zipcode.py)

### `1 x 5` Slice

This slice had previously failed `lsi` parity in Goal 28D.

Observed post-fix result:

- county face id: `829`
- zipcode face ids: `16360, 16577, 16559, 16563, 16524`
- estimated total segments: `772`
- `lsi` CPU rows: `7`
- `lsi` Embree rows: `7`
- `lsi` pair parity: `true`
- `lsi` CPU sec: `0.039520817`
- `lsi` Embree sec: `0.004615849`
- `pip` CPU rows: `5`
- `pip` Embree rows: `5`
- `pip` row parity: `true`

### `1 x 6` Slice

This slice had also previously failed `lsi` parity in Goal 28D.

Observed post-fix result:

- county face id: `829`
- zipcode face ids: `16360, 16577, 16559, 16563, 16524, 16280`
- estimated total segments: `921`
- `lsi` CPU rows: `11`
- `lsi` Embree rows: `11`
- `lsi` pair parity: `true`
- `lsi` CPU sec: `0.061642837`
- `lsi` Embree sec: `0.004795399`
- `pip` CPU rows: `6`
- `pip` Embree rows: `6`
- `pip` row parity: `true`

### `1 x 8` Slice

This was the largest previously failing exploratory slice from Goal 28D.

Observed post-fix result:

- county face id: `826`
- zipcode face ids: `16395, 16392, 16323, 16202, 16417, 16387, 16428, 16544`
- estimated total segments: `1530`
- `lsi` CPU rows: `16`
- `lsi` Embree rows: `16`
- `lsi` pair parity: `true`
- `lsi` CPU sec: `0.170075287`
- `lsi` Embree sec: `0.006709648`
- `pip` CPU rows: `8`
- `pip` Embree rows: `8`
- `pip` row parity: `true`

## What Goal 33 Proves

Goal 33 proves that the Goal 31 / Goal 32 `lsi` fix is not Mac-only.

More specifically:

- the old exact-source `lsi` mismatch reproducer is fixed on Linux too
- the old Goal 28D larger slices that had failed parity on Linux are now parity-clean
- the parity restoration survives the Goal 32 sort-sweep optimization on Linux

## Boundary

Goal 33 does **not** claim:

- paper-scale exact-input reproduction is complete
- every larger exact-source county/zipcode slice is now known to be parity-clean
- the current local `lsi` path is BVH-backed

The honest closure statement is:

- Goal 31 / Goal 32 fixed the active local `lsi` correctness issue on both Mac and Linux
- the previously failing Linux exact-source `1 x 5`, `1 x 6`, and `1 x 8` slices are now parity-clean
- local `lsi` remains an explicit `native_loop` path, currently implemented with the Goal 32 sort-sweep candidate pass
