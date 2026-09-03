# Goal5842 V12 Ampere preparation notes

Date: 2026-09-03

## Scope

These notes describe preparation performed before worker zero for the exact
V12 second-generation replay. They are environment and custody evidence, not a
new scientific input and not a performance result.

## Pod and toolchain

- Endpoint used by the project SSH wrapper: `root@38.147.83.21:44968`.
- GPU: NVIDIA RTX A6000, UUID
  `GPU-6457d4af-a4bb-bff5-a9d2-02f251ceca27`.
- Architecture generation: Ampere; compute capability: 8.6; VRAM:
  51,527,024,640 bytes.
- Driver: 550.127.08.
- CUDA: 12.8 (`nvcc` V12.8.93) at `/usr/local/cuda-12.8`.
- OptiX SDK/API: 7.7.0 at `/workspace/goal5842_ampere/optix-7.7.0`.
- Python: 3.12.3 in `/workspace/goal5842_ampere/venv`.
- NumPy 2.4.4, Numba 0.65.1, llvmlite 0.47.0, CuPy 14.0.1,
  cuda-python 12.8.0, and pyoptix distribution 9.1.0.
- PyOptiX source commit:
  `3144f224c0fd18733925faf3d8fb82c7376b8dcf`.
- Exact RTDL source commit:
  `04305fc820290cc183a599376f13d2fb48175233`; the detached checkout was
  clean before and after the formal transaction.

The execution authority inside the transaction is controlling for all exact
paths, package identities, source/header hashes, native hashes, and hardware
fields.

## Pre-worker repairs

Two ordinary compatibility repairs occurred before worker zero:

1. The first noninteractive OptiX installer invocation failed because its
   requested prefix directory did not yet exist. The directory was created and
   the same NVIDIA OptiX 7.7.0 installer was rerun successfully. The installer
   SHA-256 is
   `c558c51235afe859847681e96f1950600dcd10ba96791bc1e059e19730602a9c`.
2. The first pinned PyOptiX build accidentally selected its bundled OptiX 9.1
   headers and failed import with an unsupported ABI version. A clean rebuild
   of the same pinned PyOptiX commit explicitly bound the OptiX 7.7 headers and
   CUDA 12.8. Its accepted wheel SHA-256 is
   `fe2f424ba4ebd07055ef2750b2ead10304c738857eaa2668ee777f8c615ae74e`;
   `optix.version()` returned `(7, 7, 0)` and `optix.init()` passed.

Neither event reached worker zero, produced a registered observation, changed
a V12 source-manifest byte, or changed any preregistered workload, schedule,
phase boundary, statistic, or failure rule.

## Fresh artifacts and preflight

- Native provider:
  `/workspace/goal5842_ampere/native-v1/librtdl_optix_goal5838.so`, SHA-256
  `04f319f805eaf8e420227d20b5d30cbe8a220b928112fe8915e16de0ea912a3f`.
- Native build manifest SHA-256:
  `8aba844997b6b889348a20adf6110a8dd45cf7c86869be964ca96856778d0a22`.
- Fresh Direct binary:
  `/workspace/goal5842_ampere/direct-v1/goal5842-direct`, SHA-256
  `6588529aa1a7fb42fd5a1a0a509145b7f57abf4184f37281c34cbe9d3bcab021`.
- The four exact focused suites passed 74/74 before worker zero:
  `goal5842_causal_admission_cost_test`,
  `goal5842_prepared_cache_commit_test`,
  `goal5798_immutable_input_reuse_test`, and
  `goal5838_selected_sphere_any_hit_count_test`.
- Focused-test stderr SHA-256:
  `aeb79d4e0335570a336160a752c7a2018a1e7c1c77d7a40a0d7ebeb52dfdbae5`;
  stdout was empty.
- The V12 preregistration whole-file SHA-256 was
  `f90d49a1663338c729f86dd08cf3ce2b51a3845326fe349ec5b80759fd06e509`.

No foreign GPU compute process was present when the formal execution authority
was bound.

## Formal transaction

The create-only transaction root was
`goal5842-v12-ampere-a6000-transaction01`. All seven stages returned zero,
every stage stderr was empty, and the transaction ended with
`PASS__ONE_GPU_GENERATION_TRANSACTION_COMPLETE`. It contains 216 causal
receipts, 216 baseline subworker receipts, 108 baseline composites, and one
independent recount.

The transaction is an exact V12 replay on a second GPU generation. It does not
authorize cross-machine raw-time ratios, public performance claims, external
review, consensus, or removal of public admission checks.
