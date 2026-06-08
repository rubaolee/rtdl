# Goal3967: Direct CUDA Loader Hardening Lane Closeout

Date: 2026-06-08

## Purpose

Goal3967 closes the direct CUDA module-loader compatibility-hardening lane that
began after RTX pods exposed unsupported PTX driver-module loads. The lane did
not change RTDL semantics or benchmark routes. It replaced direct CUDA driver
module payloads that were loaded from PTX strings with CUBIN payloads, then
validated that the ten benchmark-app registry still passed on real RTX
hardware.

## Closeout Summary

| Step | Scope | Direct PTX debt after step | Clean all-app pod packet | Review status |
| --- | --- | ---: | --- | --- |
| Goal3951 | inventory after earlier CUBIN repairs | 19 | n/a | reviewed with Goal3956/3957 |
| Goal3952 | grouped reductions and segment-pair helpers | 16 | Goal3953 | reviewed with Goal3956/3957 |
| Goal3954 | partner triangle/ray device-column pack helpers | 12 | Goal3955 | reviewed with Goal3956/3957 |
| Goal3958 | point-group-nearest split/reduce helpers | 9 | Goal3959 | reviewed with Goal3960/3961 |
| Goal3962 | collect-k helpers, including cooperative smoke | 0 | Goal3963 | reviewed with Goal3964/3965 |
| Goal3966 | whole-native direct module-load audit | 0 direct PTX loads; 28/28 direct loads use CUBIN | n/a | this closeout records the scan |

## Evidence

- Goal3951 records the tracked direct `cuModuleLoadData(..., ptx.c_str())`
  inventory and its reduction from `19` to `0`.
- Goal3952, Goal3954, Goal3958, and Goal3962 migrate every tracked direct CUDA
  helper loader to `compile_to_cubin(...)` plus
  `cuModuleLoadData(..., cubin.data())`.
- Goal3953, Goal3955, Goal3959, and Goal3963 are clean all-app current-scale RTX
  pod refreshes after each migration slice. Goal3963 is the final clean packet:
  clean commit `b745a7e5`, 10/10 rows passed, and all claim-boundary flags stayed
  false.
- Goal3966 broadens the check from the tracked OptiX files to the full
  `src/native` tree: 28 direct `cuModuleLoadData` sites exist and all 28 load
  `cubin.data()` payloads; zero direct `ptx.c_str()` or `ptx.data()` CUDA driver
  payloads remain.
- Independent review pairs are present:
  - Goal3956 Claude + Goal3957 Gemini for Goals3951-3955.
  - Goal3960 Claude + Goal3961 Gemini for Goals3958-3959.
  - Goal3964 Claude + Goal3965 Gemini for Goals3962-3963.

## What Remains Out Of Scope

OptiX pipeline PTX is intentionally still present where PTX is the OptiX program
module input to pipeline construction. That is not the same mechanism as a
direct CUDA driver module loaded through `cuModuleLoadData(...)`, and this
closeout does not try to remove or relabel it.

The next useful audit, if we continue in this lane, is a classification of every
remaining `compile_to_ptx(...)` call site into intentional OptiX-pipeline use or
another explicitly documented category. That would be an audit/classification
goal, not a blind migration.

## Boundary

This is an internal compatibility closeout. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, AMD performance
wording, paper reproduction, package-install wording, or app-specific
native-engine logic.
