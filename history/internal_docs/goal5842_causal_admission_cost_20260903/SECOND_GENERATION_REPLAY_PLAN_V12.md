# Goal5842 V12 exact second-generation replay plan

Date: 2026-09-03

## Purpose

This protocol obtains the second and final GPU-architecture generation required
by Goal5842. It is a replay of the exact V12 experiment, not an optimization,
new workload, or result-dependent redesign. The Ada transaction remains fixed
and is never rerun or replaced.

## Immutable inputs

- Source commit:
  `04305fc820290cc183a599376f13d2fb48175233`
- Preregistration path:
  `history/internal_docs/goal5842_causal_admission_cost_20260903/PREREGISTRATION_V12.json`
- Preregistration whole-file SHA-256:
  `f90d49a1663338c729f86dd08cf3ce2b51a3845326fe349ec5b80759fd06e509`
- Preregistration internal seal:
  `9bcb9876bca6234756c9c49b0caf12956fd87a13748a62074278194446e67570`
- First-generation authority seal:
  `588462752860276987d12ab8d6bd0e71c8d371004268ad9e47d1d0b2bbf94006`
- Ada recount internal seal:
  `70305326b122e15806f9a67353b259620fcbb85932f6bbc04f002b4c899bbab3`

No source-manifest byte, task, input, output contract, schedule, block count,
warm-up count, repetition count, phase boundary, statistic, bootstrap seed,
failure rule, or claim boundary may change.

## Acceptable GPU

The second GPU must satisfy all of the following:

1. NVIDIA GPU and usable OptiX implementation are visible to the process.
2. `architecture_generation()` in the frozen execution-authority script maps
   its compute capability to `TURING`, `AMPERE`, `HOPPER`, or `BLACKWELL`, not
   `ADA`.
3. Its GPU UUID differs from
   `GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9`.
4. No foreign compute process is active at execution-authority binding.
5. A clean detached checkout of exact commit `04305fc8...` is used.

There is no owner-supplied driver, CUDA, Python, PyOptiX, or OptiX SDK floor.
The agent must probe the pod and negotiate a compatible user-space stack before
worker zero. Missing packages or build tools are engineering tasks, not
scientific failure. Only an immutable host limitation such as no usable NVIDIA
device or host OptiX implementation may reject a pod.

## Pre-worker-zero preparation

Use create-only paths. Replace the angle-bracket variables below with probed
absolute paths; do not reuse any path from a failed attempt.

```bash
git clone https://github.com/rubaolee/rtdl <SOURCE_ROOT>
git -C <SOURCE_ROOT> checkout --detach 04305fc820290cc183a599376f13d2fb48175233
git -C <SOURCE_ROOT> status --porcelain
git -C <SOURCE_ROOT> rev-parse HEAD
```

The status output must be empty and `HEAD` must equal the exact source commit.
Create a fresh Python 3.12-compatible environment containing the dependencies
needed by the frozen harness. Probe GPU identity, CUDA include/library roots,
OptiX headers, host compiler, NVRTC, PyOptiX, CuPy, NumPy, and Numba before any
formal execution.

Build a fresh native provider for the actual compute capability:

```bash
PYTHONPATH=<SOURCE_ROOT>/src:<SOURCE_ROOT> <PYTHON> \
  <SOURCE_ROOT>/scripts/goal5838_build_selected_sphere_optix_provider.py \
  --cuda-prefix <CUDA_PREFIX> \
  --optix-prefix <OPTIX_PREFIX> \
  --expected-optix-sdk <OPTIX_SDK_VERSION> \
  --expected-commit 04305fc820290cc183a599376f13d2fb48175233 \
  --output <NATIVE_ROOT>/librtdl_optix_goal5838.so \
  --manifest <NATIVE_ROOT>/goal5838_native_build.json \
  --log <NATIVE_ROOT>/goal5838_native_build.log
```

Build a fresh Direct baseline from the same source commit:

```bash
bash <SOURCE_ROOT>/experiments/goal5798_premeasurement/build_direct_measurement.sh \
  <OPTIX_PREFIX>/include <CUDA_PREFIX>/include <DIRECT_BINARY>
```

Before worker zero, run the exact focused no-timing tests and verify the V12
preregistration file and all source-manifest pins. Any repair must happen in a
new, explicitly documented pre-worker transaction. A repair that changes a
registered scientific input requires a new preregistration and cannot count as
this V12 replay.

## Formal one-generation command

Choose a never-before-used `<TRANSACTION_ROOT>`. The command below is the only
formal transaction driver:

```bash
CUDA_VISIBLE_DEVICES=0 \
PYTHONPATH=<SOURCE_ROOT>/src:<SOURCE_ROOT> \
<PYTHON> <SOURCE_ROOT>/scripts/goal5842_run_one_generation.py \
  --preregistration \
    <SOURCE_ROOT>/history/internal_docs/goal5842_causal_admission_cost_20260903/PREREGISTRATION_V12.json \
  --native <NATIVE_ROOT>/librtdl_optix_goal5838.so \
  --native-build-manifest <NATIVE_ROOT>/goal5838_native_build.json \
  --direct-binary <DIRECT_BINARY> \
  --device-source <SOURCE_ROOT>/experiments/goal5796_matched/matched_device.cu \
  --optix-include <OPTIX_PREFIX>/include \
  --cuda-include <CUDA_PREFIX>/include \
  --optix-sdk <OPTIX_SDK_VERSION> \
  --pyoptix-distribution pyoptix \
  --output-root <TRANSACTION_ROOT> \
  --owner-authorized
```

After worker zero, any nonzero stage is terminal for that transaction. Do not
retry a failed row, remove an adverse row, replace a worker, or resume into the
same root. Preserve the complete failed root before considering a documented
successor transaction.

## Download and independent verification

Preserve the complete transaction, native DSO and manifest, Direct binary,
driver stdout/stderr, and environment/build notes in one archive. Record its
bytes and SHA-256 before transfer and verify both after transfer.

On the Mac, use the exact source commit to rerun
`scripts/goal5842_independent_recount.py` over the downloaded raw receipt roots.
The locally generated recount must be byte-identical to the recount in the pod
transaction. Add a second-generation authority/verification record analogous
to `V12_ADA_FIRST_GENERATION_AUTHORITY.json`; it must preserve all adverse
ratios and the one-generation public-claim ceiling.

## Cross-generation gate

Only after both generation authorities pass, invoke:

```bash
PYTHONPATH=src:. <PYTHON> scripts/goal5842_build_cross_generation_authority.py \
  --recount <ADA_EXTRACTED_TRANSACTION>/independent_recount.json \
  --recount <SECOND_EXTRACTED_TRANSACTION>/independent_recount.json \
  --output <CREATE_ONLY_CROSS_GENERATION_AUTHORITY.json>
```

The builder must reject different source commits, different preregistration
seals, fewer than two architecture generations, or repeated GPU UUIDs. It must
retain per-hardware absolute results and keep
`cross_machine_raw_time_ratios_computed=false` and
`public_performance_claim_authorized=false`.

## Completion gate

Goal5842 may move to internal technical completion only when all of these are
true:

- both complete transaction archives are hash-bound and locally verified;
- both original recounts reproduce byte for byte;
- two distinct architecture generations and two distinct UUIDs are proven;
- exact source commit and preregistration seal match;
- no failed or predecessor row is pooled;
- the cross-generation authority builder passes;
- a post-result internal hostile review preserves adverse findings;
- external review remains explicitly pending while unavailable.

Public or manuscript performance wording requires a later external review and
the applicable consensus gate. Goal5842 technical completion alone does not
authorize such wording.
