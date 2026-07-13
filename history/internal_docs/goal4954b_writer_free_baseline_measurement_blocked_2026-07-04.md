# Goal4954-B Writer-Free Binary Baseline Measurement Blocked

Date: 2026-07-04

Status: blocked_by_pod_missing_optix_sdk

Parent:

- `history/internal_docs/goal4954a_binary_overlay_contract_and_measurement_plan_2026-07-04.md`
- Antigravity verdict: `approve_goal4954a_contract_measurement_plan_open_goal4954b`

## Goal

Goal4954-B was authorized as measurement-only work:

- run the public RayJoin Section 5.7 sample;
- exclude the paper text writer from the binary metric;
- measure the writer-free binary operator phases;
- compare the writer-free hot path against the AuthorOfficial overlay-compute
  reference;
- do not implement columnar reprojection/sort or any runtime/core change.

## Work Completed

### 1. Clean Remote Source Setup

The current committed repository state was transferred to POD:

```text
remote: root@213.173.108.15:14399
remote clone: /root/rtdl_goal4954
HEAD: 8cc0597b
```

The local Goal4954-B measurement script was copied into:

```text
/root/rtdl_goal4954/history/internal_docs/goal4954b_writer_free_binary_overlay_measure.py
```

The script was syntax-checked on the POD with:

```bash
python3 -m py_compile history/internal_docs/goal4954b_writer_free_binary_overlay_measure.py
```

### 2. Public Sample Download

The public County x Soil sample was downloaded and hash-verified on the POD:

```bash
PYTHONPATH=src:. python3 Paper-reproduction-apps/rayjoin-paper/scripts/fetch_public_sample.py \
  --data-dir Paper-reproduction-apps/rayjoin-paper/_data/public_sample
```

Verified files:

| Role | File | SHA-256 |
|---|---|---|
| poly1_county | `br_county_clean_25_odyssey_final.txt` | `cee9f41da48c6f072b0692843cc23804517e8928f46c6c84675fc9a3b1e5a0e7` |
| poly2_soil | `br_soil_ascii_odyssey_final.txt` | `525a6dda0e42c1ed63f30cd5ffe8e9283697f3c53076837a122ba098ad530d9f` |
| section57_answer | `br_countyXbr_soil_answer.txt` | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |

### 3. Measurement Script Prepared

The script:

- imports the public RayJoin Section 5.7 app path;
- reuses public LSI and point-location primitives;
- does not import `rtdsl.rayjoin_overlay`;
- does not write paper text in the binary metric;
- builds app-owned generic binary rows;
- runs `descriptor_pair_count` over `(label_a, label_b)` columns;
- records phase times and the ratio to an AuthorOfficial overlay-compute
  reference when provided.

This script is measurement-only. It does not change RTDL core/runtime.

## Blocking Failure

The measurement command:

```bash
PYTHONPATH=src:. python3 history/internal_docs/goal4954b_writer_free_binary_overlay_measure.py \
  --left Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt \
  --right Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt \
  --pair-name br_county_soil_public \
  --author-overlay-compute-sec 0.0421 \
  --summary _goal4954b/writer_free_binary_summary.json
```

failed before measurement at the first OptiX LSI call:

```text
FileNotFoundError: librtdl_optix not found. Build it with 'make build-optix'
or set RTDL_OPTIX_LIB=/path/to/lib.
```

Attempting to build the library:

```bash
make build-optix
```

failed with:

```text
RTDL OptiX SDK header not found at /opt/optix/include/optix.h
Set OPTIX_PREFIX to the OptiX SDK root, for example:
  make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev
```

## POD Environment Facts

The POD has a suitable NVIDIA GPU and CUDA toolkit:

```text
GPU: NVIDIA RTX 4000 Ada Generation, compute capability 8.9
CUDA headers: /usr/local/cuda/include/cuda.h
nvcc: /usr/local/cuda/bin/nvcc
libcuda: /usr/lib/x86_64-linux-gnu/libcuda.so
```

But it does not have:

```text
OptiX SDK headers: optix.h / optix_device.h / optix_stubs.h
RTDL native library: build/librtdl_optix.so
```

NVIDIA's OptiX SDK download page requires NVIDIA Developer Program login. This
worker cannot legally or reliably fetch the SDK automatically without provided
credentials or a pre-installed SDK path.

## Interpretation

This is an environment blocker, not a RayJoin algorithm blocker and not a
generic RTDL design blocker.

The following are already ready:

- public sample data;
- measurement script;
- command line;
- correctness-preserving boundary;
- generic-system/RayJoin-app invariant.

The missing prerequisite is:

```text
An installed OptiX SDK and a built RTDL OptiX native library.
```

## Required To Unblock

Any one of these is sufficient:

1. Provide an OptiX SDK path on the POD, for example:

   ```bash
   export OPTIX_PREFIX=/root/vendor/optix-dev
   make build-optix OPTIX_PREFIX=$OPTIX_PREFIX
   ```

2. Provide a POD image that already contains:

   ```text
   $OPTIX_PREFIX/include/optix.h
   build/librtdl_optix.so
   ```

3. Provide a compatible prebuilt `librtdl_optix.so` built from the same RTDL
   commit and compatible with the POD driver/CUDA environment, then run with:

   ```bash
   export RTDL_OPTIX_LIB=/path/to/librtdl_optix.so
   ```

## Next Command After Unblock

After `make build-optix` succeeds, run:

```bash
cd /root/rtdl_goal4954
mkdir -p _goal4954b
PYTHONPATH=src:. RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
python3 history/internal_docs/goal4954b_writer_free_binary_overlay_measure.py \
  --left Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt \
  --right Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt \
  --pair-name br_county_soil_public \
  --author-overlay-compute-sec 0.0421 \
  --summary _goal4954b/writer_free_binary_summary.json
```

## Exit

Current exit:

`blocked_by_pod_missing_optix_sdk`

This does not close Goal4954-B. It records that the goal is ready to run, but
blocked by missing POD OptiX SDK/native-library prerequisites.
