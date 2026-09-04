# Goal5843 final technical report

Date: 2026-09-04

Status:
`PASS__GOAL5843_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING`

## Executive result

Goal5843 completed a fresh, balanced, no-retry comparison of Direct
CUDA/OptiX, a pinned current NVIDIA PyOptiX-compatible API, and ordinary public
check-on RTDL after the Goal5842R1 implementation repair. The accepted v4
transaction contains 108 composites, 216 fresh-process subworker receipts,
7,020 registered execution timing samples, and all preregistered adverse rows.
An independent standard-library recount on the pod and a fresh recount from the
downloaded archive on macOS are byte-identical.

For the primary 16,384-query weighted triangle scalar, steady complete
execution medians were 0.092452 ms for Direct, 0.148260 ms for PyOptiX, and
0.436590 ms for public RTDL. The preregistered median-of-18 within-block ratios
were:

- RTDL/Direct: 4.688692x, bootstrap interval [4.384608x, 4.870805x].
- RTDL/PyOptiX: 2.910318x, bootstrap interval [2.828932x, 3.142973x].

The post-R1 public route is therefore no longer separated from the low-level
baselines by two orders of magnitude, but it has not reached parity. Relative
to the same-GPU Goal5842 V12 descriptive medians, the RTDL/PyOptiX ratio fell
from 155.210x to 2.910x and RTDL steady time fell from 23.653209 ms to
0.436590 ms. This cross-transaction observation is context, not a separately
preregistered causal estimand.

The 4,096-query row-returning relation control remained adverse: RTDL steady
was 12.774231 ms versus 3.853760 ms for PyOptiX and 1.297765 ms for Direct.
The corresponding within-block ratios were 3.332872x and 9.949761x. This is
consistent with the scope boundary: Goal5842R1 optimized the triangle scalar
route, not the relation row-materialization route.

There was no registered performance-success threshold. These adverse ratios
are accepted evidence rather than a reason to delete or rerun rows.

## Scientific question

The experiment asks how expensive the current public, checked RTDL path is
after Goal5842R1, relative to lower-level OptiX programming surfaces, when all
arms share one deterministic semantic input and exact public-output contract
per task.

It does not ask whether the three implementations execute identical hidden
instructions. Direct and PyOptiX are provider-specific programs; RTDL includes
public declaration, generic admission, lowering, runtime ownership, and
receipt enforcement. Setup phases are descriptive because provider work is not
identical and RTDL places its initial query upload in first execute while the
other arms place it in prepare.

## Frozen protocol

The accepted v4 preregistration has internal seal
`c0ad3a566e99f925341d98c987854714cfabc415254ccd7178efcd465e664b66`.
It fixes:

- 18 balanced blocks and all six arm permutations;
- two tasks and three arms, giving 108 composites;
- a separate fresh FIRST process and fresh STEADY process per composite;
- 8 steady warmups and 64 measured steady executions;
- same task input and public-output digests across all arms;
- exact oracle checking outside the registered interval;
- no outlier deletion, no performance threshold, and no subworker retry;
- a primary steady triangle estimand using median within-block ratios;
- a fixed-seed 10,000-draw bootstrap interval;
- retention of the row-returning relation as an adverse control.

Each complete execution includes required resets, parameter updates, OptiX
launches, public output transfer, status checking, and GPU completion. Process
startup is excluded from all provider phase estimands.

## RTDL execution gate

All 36 formal RTDL triangle FIRST/STEADY receipts passed the post-R1 gate. Each
latest receipt proves:

- public execution path `device_resident_checked_u64_scalar_v7`;
- one OptiX launch and no dynamic GAS build;
- no host per-ray U64 or event-row materialization;
- no role-counter materialization or auxiliary CUDA kernel;
- 12 control bytes and one 8-byte scalar downloaded;
- an initial nonzero query upload for FIRST;
- zero query-upload calls and bytes for STEADY;
- reuse of the exact published prepared query object for STEADY.

Relation intentionally has no triangle-only provider-execution extension. Its
Goal5843 boundary instead carries the generic result's self-digested traversal
receipt. Controller and independent recount require the exact route, OptiX
classification, DSO hash, output digest, two successful launches, zero failed
launches, 8,192 raygen invocations, and execution count 1 for FIRST or 72 for
STEADY.

## Accepted performance results

All values below are medians across 18 workers for one task/arm. Setup and first
execution are descriptive secondary values. Steady ratios are calculated from
within-block ratios, not by dividing the displayed aggregate medians.

| Task | Arm | Setup ms | First ms | Steady ms |
| --- | ---: | ---: | ---: | ---: |
| Relation rows | Direct CUDA/OptiX | 592.903675 | 1.408452 | 1.297765 |
| Relation rows | PyOptiX-compatible | 425.417417 | 5.581692 | 3.853760 |
| Relation rows | Public RTDL | 1946.247301 | 26.423480 | 12.774231 |
| Triangle scalar | Direct CUDA/OptiX | 552.126428 | 0.182752 | 0.092452 |
| Triangle scalar | PyOptiX-compatible | 455.316206 | 0.314354 | 0.148260 |
| Triangle scalar | Public RTDL | 1759.391122 | 44.873120 | 0.436590 |

| Task | Metric | RTDL/Direct | Bootstrap interval | RTDL/PyOptiX | Bootstrap interval |
| --- | --- | ---: | ---: | ---: | ---: |
| Relation rows | Setup | 3.314418x | [3.073526x, 3.979651x] | 4.582961x | [3.979837x, 5.506717x] |
| Relation rows | First | 18.949891x | [17.992686x, 20.759673x] | 4.773908x | [4.152629x, 5.211050x] |
| Relation rows | Steady | 9.949761x | [9.809213x, 10.167388x] | 3.332872x | [2.957558x, 3.399837x] |
| Triangle scalar | Setup | 3.227749x | [2.989132x, 3.740437x] | 3.688533x | [3.159748x, 4.130133x] |
| Triangle scalar | First | 232.337862x | [214.548207x, 263.935267x] | 134.604469x | [111.869044x, 151.990489x] |
| Triangle scalar | Steady | 4.688692x | [4.384608x, 4.870805x] | 2.910318x | [2.828932x, 3.142973x] |

The very large triangle FIRST ratios are not steady-state language-overhead
estimates. RTDL's first complete execution includes its initial prepared-query
upload, while Direct and PyOptiX account for that upload during prepare. The
preregistered report therefore treats FIRST and setup only descriptively.

## Remaining overhead

The accepted evidence identifies where work remains but does not provide a
fully instrumented causal decomposition of the 0.436590 ms RTDL steady path.
The public complete-execution interval still includes Python dispatch, generic
result and receipt construction, native status/control handling, and the final
scalar transfer around the native launch. Earlier Goal5842R1 diagnostics put
the native v7 operation near 0.067 ms on this GPU, but those nonformal rows are
not pooled into Goal5843.

Setup also remains expensive. The first-worker phase medians for triangle RTDL
include approximately 1,027.516 ms in native prepare, 543.750 ms in target
materialization, 86.463 ms in generic admission, 68.437 ms in declaration, and
53.653 ms in runtime binding. These phase medians are descriptive and are not
assumed additive because medians are taken independently.

The next performance work should instrument the public steady boundary without
weakening checks, then reduce repeated Python/ctypes receipt and dispatch work.
It must not reintroduce the private checker-off arm, move app semantics into the
engine, or relabel the relation route as scalar-only.

## Repair history

Two timer-free pre-worker repairs corrected Goal5843-only harness assumptions:
recursive read-only lifecycle unwrapping and relation evidence selection. They
recorded no formal timing and changed no frozen Goal5838 core byte.

The v3 formal transaction later completed all pod stages, but its downloaded
archive verifier incorrectly compared modes normalized by secure tar extraction
against original pod modes. v3 is permanently terminal, its complete archive
is retained at SHA-256
`bf24cc9954e9f6970ea58ff6584f79bf1de32b2e5118003a06723cb8ba61f118`,
and none of its 7,020 timing samples was pooled into v4.

v4 keeps safe extraction, verifies original mode custody from tar headers, and
verifies extracted size and SHA-256 independently. The repair passed a focused
mutation test and the real v3 archive's six-artifact custody boundary before a
new preregistration and complete new transaction were run.

## Hardware and toolchain

| Property | Accepted value |
| --- | --- |
| Pod endpoint | `root@194.68.245.56:22160` |
| GPU | NVIDIA RTX A6000, Ampere |
| GPU UUID | `GPU-f50facdf-7752-c71d-2c4a-c4df8c0155cc` |
| Compute capability | 8.6 |
| VRAM | 48,305,799,168 bytes |
| Driver | 580.159.03 |
| CUDA compiler | 12.8, NVCC 12.8.93 |
| OptiX headers/API | 9.0.0 |
| Python | 3.12.3 |
| NumPy / Numba / CuPy | 2.4.4 / 0.65.1 / 14.0.1 |
| PyOptiX distribution | 9.1.0 |
| PyOptiX repository commit | `3144f224c0fd18733925faf3d8fb82c7376b8dcf` |
| Formal source commit | `c2662603c4d24902361fbd70325832ee7d98a0a4` |
| Native DSO SHA-256 | `91ae01bb6944eb03b729ec12313bdbc07f4ca474fa63229fd68eb5681b1d784a` |
| Direct executable SHA-256 | `5f6d4d6a5dd7b5545d5283803c4ee1db51158828e84151a74004fd801eebd28c` |

## Evidence chain

| Evidence | Internal seal or SHA-256 |
| --- | --- |
| Formal leaf-cache preparation | `fcef08dfc14c0e39f72395d9612ced941a7d18e965a90ca5047a46a4b3e8ab38` |
| Independent oracle witness | `fe210416572ba97e0074468ab64bfcd965803955c804aa21970db5e072398960` |
| Execution authority | `41510173122a06c48d0c137f05f9183bc2ac3dad256a0a6bdb435fa59f0e0101` |
| Bound-artifact custody | `6876d7307e7464a27475f4282c98ce05f03cde9a94edfe5a0626eb14ea80c04c` |
| Controller result | `498526cdc9a7e3dbcc76d7cf9af99833bce152cd10b22033709954307d9c5b35` |
| Pod/local recount | `6dd6a575e4278fad9b3add4b6599b49df95dc9c7cafe0db62872a30a5916dac5` |
| Formal archive SHA-256 | `0b8374a70c2fc06f538f45a1911099d4ae5b87bc8ab93f239af2c900fbbf014a` |
| Downloaded archive verification | `4a93956c80d7983601f3704addd4c2f25fd61387997fb404d2ddf97b7e39c18b` |

The archive has 1,480 members, contains six exact bound executable/provider
artifacts, and reproduces the pod recount byte-for-byte on the Mac.

## Exact conclusion

Goal5843 establishes an internally verified fresh post-R1 baseline on one RTX
A6000. Goal5842R1 removed the catastrophic triangle steady-path gap, but the
ordinary public RTDL route remains 2.91x slower than the pinned PyOptiX arm and
4.69x slower than Direct on the primary task. The relation row-returning route
remains a stronger adverse control. These results define the next optimization
target; they do not authorize public or manuscript performance wording,
hardware-independent claims, general language-performance claims, or external
consensus.
