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
Numba 0.65.1, NumPy 2.4.4, and CUDA compatible with the visible GPU. Replace
the uppercase placeholders with discovered absolute paths and the full
40-character Git commit.

Goal5838 does not preregister one mandatory OptiX SDK or driver branch. Select
the newest exact SDK whose zero-launch `optixInit()` ABI probe succeeds against
the pod's host driver. An ABI mismatch is a repairable environment result: try
another compatible SDK without changing the frozen generic core or selected
semantics. The SDK version, header hashes, driver, GPU, and compiled native
descriptor remain bound into the final evidence, so results from different
profiles are never conflated.

Use a normal full-history clone when possible. The preregistration verifier
reads the frozen baseline commit
`0f5c9d4297f73e412732e5a8ab133423fe4cfd21`; an unqualified depth-one clone
does not contain that object and therefore fails closed before GPU work. If a
shallow clone is required, fetch the baseline object without changing `HEAD`:

```bash
git fetch --depth=1 origin 0f5c9d4297f73e412732e5a8ab133423fe4cfd21
git rev-parse HEAD
git rev-parse 0f5c9d4297f73e412732e5a8ab133423fe4cfd21
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

If the pod has no OptiX headers, acquire one NVIDIA public-header candidate by
exact commit rather than trusting a mutable tag name. Current candidate
identities are:

| SDK | `optix-dev` commit |
| --- | --- |
| 9.1.0 | `f1f6dd803f3159992d248178f6e09421c6eb8b6d` |
| 9.0.0 | `fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd` |
| 8.1.0 | `50021ea0af6d41609a97777ceebbdf1e1d34efe7` |
| 8.0.0 | `f60c1e44f18426f426a2ed948f28515b3cf67b8a` |
| 7.7.0 | `7b5c4e8608b8b4b601729f6240fc3fd53cb36d23` |

For example, replace `OPTIX_COMMIT` and `OPTIX_PREFIX` below:

```bash
git clone --quiet https://github.com/NVIDIA/optix-dev.git OPTIX_PREFIX
git -C OPTIX_PREFIX checkout --detach OPTIX_COMMIT
test "$(git -C OPTIX_PREFIX rev-parse HEAD)" = OPTIX_COMMIT
```

Before building, run the dedicated read-only pod preflight. It verifies the
exact clean commit, preregistered baseline object, frozen-core and selection
authorities, focused tests, Python dependencies, selected GPU 0, CUDA/NVRTC,
the exact selected OptiX headers, host tools, fresh external artifact paths,
and a compiled-and-executed `optixInit()` ABI probe. It performs no provider
build and no OptiX launch. Replace `FULL_COMMIT`, `CUDA_PREFIX`, `OPTIX_PREFIX`,
and `OPTIX_SDK`.

```bash
PYTHONPATH=src:. python scripts/goal5838_pod_preflight.py \
  --cuda-prefix CUDA_PREFIX \
  --optix-prefix OPTIX_PREFIX \
  --expected-optix-sdk OPTIX_SDK \
  --expected-commit FULL_COMMIT \
  --artifact-dir /tmp/goal5838-evidence \
  --output /tmp/goal5838-preflight.json
```

Only the status
`PASS__GOAL5838_POD_READY_FOR_FROZEN_GPU_EXAM__NO_GPU_EXECUTION_CLAIM`
authorizes proceeding to the printed build, run, and verifier commands. A
non-ready result identifies repairable pod engineering; it is not a
scientific-failure result and must be repaired before execution.

The existing product-only native build excludes the sphere lifecycle ABI under
`RTDL_V4_PRODUCT_ONLY`. Therefore this exam builds the existing full generic
provider from `src/native/rtdl_optix.cpp`; it does not modify native C++ source
or add selected-app logic to the engine.

```bash
CUDA_VISIBLE_DEVICES=0 PYTHONPATH=src:. \
python scripts/goal5838_build_selected_sphere_optix_provider.py \
  --cuda-prefix CUDA_PREFIX \
  --optix-prefix OPTIX_PREFIX \
  --expected-optix-sdk OPTIX_SDK \
  --compute-capability COMPUTE_CAPABILITY \
  --expected-commit FULL_COMMIT \
  --output /tmp/librtdl_optix_goal5838.so \
  --manifest /tmp/goal5838_native_build.json \
  --log /tmp/goal5838_native_build.log
```

```bash
CUDA_VISIBLE_DEVICES=0 PYTHONPATH=src:. \
python scripts/goal5838_run_selected_sphere_gpu_exam.py \
  --native /tmp/librtdl_optix_goal5838.so \
  --native-build-manifest /tmp/goal5838_native_build.json \
  --optix-include OPTIX_PREFIX/include \
  --cuda-include CUDA_PREFIX/include \
  --optix-sdk OPTIX_SDK \
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
