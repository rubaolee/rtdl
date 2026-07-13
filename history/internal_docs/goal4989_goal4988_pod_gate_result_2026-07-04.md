# Goal4989 / Goal4988 POD Gate Result

## Verdict

`completed_goal4988_pod_runtime_gate__lsi_pair_device_columns_direct_to_numba_verified`

## POD

```text
ssh root@157.157.221.29 -p 25248
key: ~/.ssh/id_ed25519_rtdl_codex_current_pod
hostname: aee120b7ac8f
GPU: NVIDIA RTX 4000 Ada Generation
driver: 570.211.01
```

## Environment Repair

The POD initially had CUDA and the NVIDIA driver but not OptiX headers:

```text
CUDA: /usr/local/cuda-12.8/bin/nvcc
missing: /root/vendor/optix-dev/include/optix.h
```

Using the latest `NVIDIA/optix-dev` headers failed at runtime with:

```text
OptiX error: Unsupported ABI version
```

Root cause: the latest headers were OptiX 9.1:

```text
#define OPTIX_VERSION 90100
```

The fix was to use the official NVIDIA `optix-sdk` tag compatible with this
driver family:

```text
git clone --depth 1 --branch v8.1.0 https://github.com/NVIDIA/optix-sdk /root/vendor/optix-sdk-8.1
#define OPTIX_VERSION 80100
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk-8.1 CUDA_PREFIX=/usr/local/cuda
```

The native library then built successfully:

```text
/root/rtdl_goal4988/build/librtdl_optix.so
```

## Runtime Command

The real Section 5.7 public-sample writer-free binary route was run with the
direct LSI device-column handoff enabled:

```text
PYTHONPATH=src:. \
RTDL_OPTIX_LIB=/root/rtdl_goal4988/build/librtdl_optix.so \
RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR=/root/rtdl_goal4988/Paper-reproduction-apps/rayjoin-paper/_runs/public_sample/cache \
.venv/bin/python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt \
  --right Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt \
  --pair-name br_county_soil \
  --device-columnar \
  --bounded-exact-lsi-device-columns \
  --bounded-exact-lsi-capacity 1000000 \
  --point-location-device-face-columns \
  --fast-scaled-point-pack \
  --compiled-group \
  --validate-device-order \
  --summary Paper-reproduction-apps/rayjoin-paper/_runs/public_sample/rtdl/goal4988_direct_handoff_binary.json
```

## Artifact

Copied back to the repo:

```text
history/internal_docs/goal4989_pod_artifacts_2026-07-04/goal4988_direct_handoff_binary_public_sample.json
```

## Required Gate Checks

All required checks passed:

```json
{
  "bounded_direct": true,
  "bounded_no_numpy_copy": true,
  "pair_device_resident": true,
  "pair_no_h2d_copy": true,
  "rb_device_resident": true,
  "rb_no_host_materialization": true,
  "sort_validated": true,
  "row_count": true,
  "xsect_counts": true
}
```

Important result fields:

```text
bounded_exact_lsi_numba_direct_handoff_used: true
bounded_exact_lsi_downstream_numpy_copy_used: false
lsi_pair_input_device_resident: true
lsi_pair_host_to_device_copy_used: false
lsi_pair_row_buffer_contract.device_resident_candidate: true
lsi_pair_row_buffer_contract.materializes_host_rows_for_bridge: false
lsi_pair_row_buffer_contract.host_rows_materialized_before_partner_handoff: false
sort_order_validated_against_cpu_reference: true
lsi_row_count: 20860
xsect_sorted_counts: side0=20860, side1=20860
```

## Timing Snapshot

This is a public County x Soil sample run, not top4 County x Zipcode:

```text
writer_free_hot_sec: 1.7649040445685387
lsi_phase_sec: 0.9842492435127497
downstream_floor_sec: 0.780654801055789
```

The LSI pair-id copy phase is absent from the writer-free key list because the
route now directly hands native device columns to Numba CUDA:

```text
writer_free_hot_keys:
  lsi_bounded_exact_pair_id_device_columns_sec
  ""
  intersection_reprojection_device_columnar_sec
  ...
```

## Claim Boundary

This proves:

```text
LSI pair-id device columns can feed Numba CUDA reprojection through the generic
row-buffer / CUDA-array-interface path without a device -> NumPy -> device pair
round trip.
```

This does not prove:

```text
full Section 5.7 device-resident overlay;
true-zero-copy end-to-end route;
author-performance parity;
public v2.14.3 release readiness;
Layer 4 fusion;
top4 performance ratio.
```

Remaining visible host boundaries include:

```text
point-location face-id device columns are still copied to NumPy;
carrier/group construction remains CPU/Numba;
downstream consumer remains CPU/Numba;
the binary route remains separate from byte-for-byte paper text output.
```
