# Goal3761 RayJoin Native-PIP Cross-Size Current Packet

Date: 2026-06-07

## Purpose

Goal3760 corrected the benchmark matrix to acknowledge that the current
RayJoin PIP scalar-count leg can use the generic RTDL/OptiX resident
relation-status corrected scalar-count executor instead of the older dense
CuPy PIP route. Goal3761 refreshes that evidence across the supported
cross-size public-CDB slices from a clean current-main checkout.

## Clean Pod Setup

- Pod GPU: NVIDIA RTX A5000.
- Clean checkout: `/root/rtdl_goal3761_main`.
- Source commit: `69a4cc0a`.
- OptiX SDK: `/root/vendor/optix-sdk`.
- OptiX library: `/root/rtdl_goal3761_main/build/librtdl_optix.so`.
- Runtime env: `PYTHONPATH=src:.`, `RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS=1e-9`.
- Public CDB source files were copied into `data/rayjoin_public_cdb/`; this is
  why the full checkout status contains `?? data/`. The scoped source status
  for the route remained clean.

Command:

```bash
python scripts/goal3688_rayjoin_native_pip_safe_mixed_composite.py \
  --counts 512,1024,2048,4096 \
  --repeat 10 \
  --warmup 3 \
  --output docs/reports/goal3761_rayjoin_native_pip_cross_size_current_a5000/summary.json
```

## Results

Artifact:

- `docs/reports/goal3761_rayjoin_native_pip_cross_size_current_a5000/summary.json`

Summary:

- all counts match: `true`
- row count: `4`
- geomean native-PIP safe-mixed speedup versus dense all-CuPy: `288.759x`
- minimum native-PIP safe-mixed speedup versus dense all-CuPy: `118.931x`

| Chains | Dense all-CuPy sum sec | Native-PIP mixed sum sec | Composite speedup |
| ---: | ---: | ---: | ---: |
| 512 | 0.070897 | 0.000596 | 118.931x |
| 1,024 | 0.164704 | 0.000788 | 209.021x |
| 2,048 | 0.357336 | 0.000995 | 358.977x |
| 4,096 | 1.433339 | 0.001840 | 779.090x |

Per-workload speedups:

| Chains | PIP | LSI | Overlay active-count |
| ---: | ---: | ---: | ---: |
| 512 | 1.425x | 322.879x | 227.625x |
| 1,024 | 1.238x | 1091.380x | 236.206x |
| 2,048 | 1.547x | 3194.304x | 161.656x |
| 4,096 | 2.726x | 12455.363x | 116.358x |

## 8192 Boundary

An exploratory 8192-chain run was attempted before the accepted clean packet.
It is not part of the accepted artifact because the dense all-CuPy LSI baseline
attempted to allocate about 32.9 GB of flag storage and OOMed on the A5000.
This is useful future-design evidence: larger RayJoin comparisons need a
non-dense baseline policy instead of materializing all candidate-pair flags.

## Interpretation

The current native-PIP RayJoin route is now cross-size supported on the
512-4096 public-CDB slices:

- PIP uses the generic RTDL/OptiX resident scalar-count executor.
- LSI uses exact prepared RTDL/OptiX count.
- Overlay active-count uses the RTDL/OptiX prepared active-count route.
- CuPy is the dense CUDA-core baseline/opponent, not a required leg in this
  current native-PIP packet.

This remains a same-contract internal benchmark packet. It is not RayJoin paper
reproduction and not a public `RTDL beats RayJoin` claim.

## Boundary

Goal3761 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, RayJoin paper-reproduction wording,
RTDL-beats-RayJoin wording, true-zero-copy wording, automatic partner
selection, or app-specific native engine logic.
