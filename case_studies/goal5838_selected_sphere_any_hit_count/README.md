# Goal5838 selected sphere any-hit count

## Scientific role

This post-selection case study is the independently selected prospective exam
for the frozen Goal5838 generic family core. The challenge was selected from
the precommitted ten-row table after the three-file core seal. Its exact ID is
`builtin_sphere::any_hit_count_continue_u64_per_query`.

The selected protocol traces one motion segment per query against one static
OptiX built-in-sphere GAS. Every intersected primitive invokes the verified
`any_hit` callback exactly once, increments a U64 payload, calls
`optixIgnoreIntersection`, and continues traversal. The miss role returns the
final payload after all ignored intersections and the finalize role commits one
U64 count per query.

## Layer boundary

| Layer | Goal5838 responsibility |
| --- | --- |
| Frozen generic core | Schema admission, canonical plan, provider binding, and generic public lifecycle |
| Selected protocol extension | Restricted four-role Callback IR, exact proof, ABI, Numba leaf generation, and trusted OptiX wrapper |
| Generic OptiX provider | Built-in-sphere GAS, built-in intersection module, one-SBT-record pipeline, prepared execution, and physical receipts |
| Case study | Deterministic centers, radii, queries, and names only |
| Independent oracle | RTDL-free exact-rational classification of conditioned binary32 segment/sphere intersections |

The frozen core contains no sphere dispatch and no application vocabulary.
The selected callback has no primitive metadata channel. Consecutive primitive
IDs are generated only inside the provider as private compatibility input to
the pre-existing native sphere ABI; the wrapper never reads them and they are
not output.

## True RT requirements

A passing receipt must independently establish all of the following:

- `OPTIX_BUILD_INPUT_TYPE_SPHERES` and `OPTIX_PRIMITIVE_TYPE_SPHERE`;
- an OptiX built-in intersection module, with no user intersection program;
- one static GAS and one SBT record;
- `OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL`;
- one real `optixTrace` launch per execution;
- `optixIgnoreIntersection` continuation in the any-hit program;
- make-ray, any-hit, miss, and finalize device-role counters;
- exact U64 outputs matching the independent CPU oracle; and
- byte-identical frozen core before and after execution.

## Clean-pod procedure

Run from a clean checkout of the exact committed exam source. Use Python 3.12,
Numba 0.65.1, NumPy 2.4.4, CUDA compatible with the visible GPU, and OptiX SDK
9.0.0. Replace the uppercase placeholders with discovered absolute paths and
the full 40-character Git commit.

The existing product-only native build excludes the sphere lifecycle ABI under
`RTDL_V4_PRODUCT_ONLY`. Therefore this exam builds the existing full generic
provider from `src/native/rtdl_optix.cpp`; it does not modify native C++ source
or add selected-app logic to the engine.

```bash
PYTHONPATH=src:. python scripts/goal5838_build_selected_sphere_optix_provider.py \
  --cuda-prefix CUDA_PREFIX \
  --optix-prefix OPTIX_9_PREFIX \
  --expected-optix-sdk 9.0.0 \
  --compute-capability COMPUTE_CAPABILITY \
  --expected-commit FULL_COMMIT \
  --output /tmp/librtdl_optix_goal5838.so \
  --manifest /tmp/goal5838_native_build.json \
  --log /tmp/goal5838_native_build.log
```

```bash
PYTHONPATH=src:. python scripts/goal5838_run_selected_sphere_gpu_exam.py \
  --native /tmp/librtdl_optix_goal5838.so \
  --native-build-manifest /tmp/goal5838_native_build.json \
  --optix-include OPTIX_9_PREFIX/include \
  --cuda-include CUDA_PREFIX/include \
  --optix-sdk 9.0.0 \
  --compute-capability COMPUTE_CAPABILITY \
  --expected-commit FULL_COMMIT \
  --output /tmp/goal5838_gpu_exam.json
```

```bash
python scripts/goal5838_verify_selected_sphere_gpu_exam.py \
  --artifact /tmp/goal5838_gpu_exam.json \
  --native /tmp/librtdl_optix_goal5838.so \
  --output /tmp/goal5838_gpu_exam_verification.json
```

All generated evidence paths are outside the Git tree and are created
exclusively. The build manifest seals source, compiler, SDK headers, GPU,
command, log, exported symbols, and DSO identity. The final verifier imports no
RTDL module and rederives the fixture, expected counts, family identities,
native fingerprints, physical descriptor, and traversal receipt.

## Claim boundary

Before a verified true-GPU artifact exists, this is implementation and local
readiness evidence only. A pass establishes one bounded prospective result for
one independently selected topology. It is not performance evidence, a Paper
App, arbitrary Callback-IR GPU execution, universal provider portability,
application correctness, external review, or consensus.
