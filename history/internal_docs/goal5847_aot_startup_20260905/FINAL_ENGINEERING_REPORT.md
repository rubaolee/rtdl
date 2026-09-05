# Goal5847 deployable AOT startup performance report

## Decision

Goal5847 is internally technically complete at exactly
`PASS__GOAL5847_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING`.
For the frozen 4,096-by-4,096 bounded-relation task returning 4,096 canonical
rows, the median of eight paired complete-process RTDL/PyOptix ratios is
`0.229370x` and the worst block is `0.258728x`. The reciprocal primary ratio is
`4.360x`. All 2,048 registered steady samples are retained. Pooled steady
medians are 299.403 us for RTDL and 3,496.252 us for PyOptix, a `0.085635x`
ratio and `11.677x` reciprocal.

This closes the exact deployable-AOT startup and prepared-steady performance
debt defined by the frozen Goal5847 experiment. It does not establish an
intrinsic language speedup, first-ever compilation performance, arbitrary
workload performance, cross-hardware generality, production signing, external
review, or a public/manuscript claim.

## Problem

Goal5846 showed warm-cache setup parity against a source-compiling PyOptix arm,
but also retained an adverse precompiled-PTX sensitivity: after compilation
was removed from PyOptix, the then-current RTDL setup path was materially
slower. The causes were architectural rather than a single Python call:

1. A deploy process still loaded a broad native image with an eager runtime-
   compiler dependency even when the `.rtdlexe` already contained PTX.
2. CUDA/OptiX provider initialization and signed artifact verification were
   serialized despite being independent until their final identity bind.
3. The public family route lacked one direct family-bound deployable artifact
   handoff and relied on internal adaptation.
4. Repeated prepared relation execution rebuilt thousands of identical Python
   row tuples even though native code already returned canonical packed rows.

A language abstraction that requires a runtime compiler to execute a
precompiled artifact, or loses its steady advantage while fixing startup, does
not support the CGO argument. Goal5847 therefore measures the complete deploy
path and steady execution together.

## Repair

The repair remains application-neutral.

- The native builder now has a `rtdlexe_aot_runtime_v1` profile. Its fresh DSO
  is 1,262,360 bytes, exports exactly 23 allowlisted relation/triangle runtime
  and audit symbols, has no eager `libnvrtc` dependency, and exposes no source-
  compiler entry point. Runtime-compiler linkage is lazy and build-pinned, but
  the measured deploy path neither loads nor invokes it.
- Signed deployment installation can start a one-shot provider initialization
  capability while the CPU verifies the artifact and detached authority.
  Binding waits for completion and rechecks deployment, trust root/package,
  artifact, executable, family, native SHA-256, target and producer descriptor
  before issuing a provider-ready capability.
- Provider initialization is PID-bound, one-shot and fail closed. Background
  failures, mismatched family/artifact binding, concurrent bind/close,
  abandonment and post-fork use are rejected or cleaned up by tested ownership
  handoffs.
- The public family export builds and loads a family-bound `.rtdlexe` directly;
  it does not unwrap private family handles.
- A prepared bounded-relation owner preallocates fixed ABI storage and scalar
  control buffers. Every call still executes native OptiX and validates status.
  An immutable decoded tuple is reused only when the newly returned canonical
  packed bytes are byte-identical. Oracle, audit or cache-commit failure cannot
  publish a new cached value.

No RayDB, collision, graph, paper-app predicate or application formula entered
the engine. The two AOT families are reusable bounded relation and checked
triangle reduction behaviors.

## Frozen experiment

The successor preregistration was committed before any V2 formal worker. Both
arms used:

- task `CUSTOM_AABB_CLOSED_RELATION_COUNT_V1`;
- input SHA-256
  `8606dd3c22d424a7ee2d64b61918f6185d39d8090d1a0a64001de65054d25e0e`;
- output SHA-256
  `2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77`;
- 4,096 indexed boxes, 4,096 query boxes and 4,096 canonical rows;
- source commit `f5e337feef6829e063c6aff06f4e8bd6d5466b3b`, tree
  `c276d64342bf17fee77b7ab0cf66ef5060c73341`;
- pinned PyOptix commit
  `3144f224c0fd18733925faf3d8fb82c7376b8dcf`, tree
  `0bf0ec24efb4a43f129aee25dd265aa8149374e3`;
- precompiled PTX SHA-256
  `7f79eb31ff6eedaf25c24e0910bf2989b576b13a883a4a2e5c840f72b6203b2d`;
- RTX 2000 Ada Generation, compute capability 8.9, driver 580.159.04,
  CUDA 12.8 and OptiX 9.0.0;
- eight balanced alternating-order blocks, one fresh process per arm/block,
  16 warmups, 128 retained steady samples per worker and zero discarded
  samples.

The primary endpoint starts in the parent immediately before spawning each
worker and ends after the first exact result. It includes interpreter startup,
arm dependency import, deterministic fixture construction, deployment/pipeline
setup, prepare, first execution and exact result validation. Git and hardware
instrumentation follow the endpoint. The secondary endpoint excludes only the
implementation import. The steady timer encloses complete same-contract
execution; exact validation follows every timed action for both arms.

Both arms consume precompiled device programs. The PyOptix harness does not
compile source, but importing its CuPy-based dependency stack maps NVRTC. RTDL
maps no NVRTC library, imports no Numba/llvmlite/compiler lifecycle module, and
reports zero runtime-compiler attempts before and after execution.

## Results

| Metric | RTDL | Pinned PyOptix | RTDL/PyOptix |
|---|---:|---:|---:|
| Median complete process to first correct result | 1,413.776 ms | 6,163.251 ms | descriptive 0.229x |
| Primary median of paired block ratios | - | - | 0.229370x |
| Worst primary block | 1,432.887 ms | 5,538.199 ms | 0.258728x |
| Median post-import to first correct result | 637.846 ms | 263.349 ms | descriptive 2.422x |
| Secondary median of paired block ratios | - | - | 2.504242x |
| Worst secondary block ratio | - | - | 3.211853x |
| Pooled prepared steady median | 299.403 us | 3,496.252 us | 0.085635x |
| Registered steady samples | 1,024 | 1,024 | zero discarded |
| Canonical rows per call | 4,096 | 4,096 | exact match |

The ratio-of-medians rows are descriptive. The preregistered primary and
secondary estimators are medians of within-block ratios.

| Block | First arm | RTDL process ms | PyOptix process ms | Primary ratio | RTDL post-import ms | PyOptix post-import ms | Secondary ratio |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | RTDL | 1,600.411 | 9,777.223 | 0.163688x | 832.753 | 259.275 | 3.211853x |
| 1 | PyOptix | 1,480.260 | 6,090.035 | 0.243063x | 692.522 | 256.376 | 2.701198x |
| 2 | RTDL | 1,354.064 | 5,792.040 | 0.233780x | 621.466 | 270.107 | 2.300812x |
| 3 | PyOptix | 1,432.887 | 5,538.199 | 0.258728x | 654.225 | 250.301 | 2.613755x |
| 4 | RTDL | 1,370.824 | 6,037.586 | 0.227048x | 606.908 | 272.652 | 2.225941x |
| 5 | PyOptix | 1,490.090 | 6,431.322 | 0.231693x | 698.222 | 267.423 | 2.610930x |
| 6 | RTDL | 1,394.664 | 6,236.466 | 0.223630x | 607.805 | 253.511 | 2.397553x |
| 7 | PyOptix | 1,389.702 | 6,289.074 | 0.220971x | 548.951 | 299.308 | 1.834070x |

Median per-worker phases are independently aggregated and therefore do not sum
to the median total.

| RTDL phase | Median |
|---|---:|
| Implementation import | 136.718 ms |
| Deterministic input materialization | 15.519 ms |
| Signed deployment install | 47.240 ms |
| Start provider initialization | 4.262 ms |
| Artifact and authority load | 72.566 ms |
| Provider bind and initialization join | 269.734 ms |
| Deploy static input | 58.660 ms |
| Deploy dynamic input | 42.793 ms |
| Native prepare | 53.815 ms |
| First complete execution | 2.946 ms |

| PyOptix phase | Median |
|---|---:|
| Implementation import | 5,205.902 ms |
| Deterministic input materialization | 15.208 ms |
| Precompiled PTX load | 6.137 ms |
| CUDA/OptiX context | 167.911 ms |
| Module/program/pipeline/SBT | 18.030 ms |
| Native prepare | 30.195 ms |
| First complete execution | 4.368 ms |

The complete-process advantage is dominated by avoiding the PyOptix/CuPy
dependency import. Once that import is excluded, RTDL remains slower because it
pays signed deployment, detached authority verification, static/dynamic input
construction and the provider initialization join. That adverse `2.504x`
secondary result is retained and passes only the separately frozen `3.0x`
median and `4.0x` worst-block bounds.

The 299.403 us RTDL steady median is `0.817282x` the Goal5845 366.340 us
reference, so startup work did not buy its result by regressing the prepared
path. The pinned PyOptix arm emits 8,192 raw events and canonicalizes 4,096 rows
on the host; RTDL performs generic device semantic compaction. Therefore the
`11.677x` reciprocal is an exact public-contract implementation comparison,
not a pure dispatch-overhead or intrinsic language comparison.

## Correctness and security

- The independent GPU validator matched all 4,096 relation rows and the
  triangle checked-U64 result `65530`.
- Ten full traversal receipts were independently recounted: relation and
  triangle GPU validation plus one post-timing relation diagnostic in each of
  eight RTDL workers. Relation receipts record two successful OptiX launches
  and 8,192 raygen invocations; triangle records one launch and 16,384 raygen
  invocations.
- Five isolated attacks failed closed: artifact append, detached-authority
  append, native-library append, cross-family bind and unknown deployment slot.
- Both installed deployment chains pass standard-library RSA PKCS#1 v1.5
  SHA-256 verification and bind the exact artifact, authority, executable,
  family, native provider, target and task semantics.
- Signing keys were generated only for tests and destroyed after freeze. This
  is not production key-custody evidence.

## Evidence and verification

The complete pod capture is
`FORMAL_V2_EVIDENCE.tar.gz`, SHA-256
`65ee646c36e801fbf957de6eeb0c8b03106a48fa01bb2008d3aed0761fd037e8`.
It contains 80 manifest-bound payload files plus the capture manifest: all 16
worker JSON/stdout/stderr triples, controller, preregistration, GPU validation,
candidate artifacts and trust documents, native DSO/build identity, pinned
PyOptix source/extension/build receipt/PTX, and environment records.

`scripts/goal5847_build_aot_startup_authority.py` imports neither RTDL nor a GPU
package. It checks safe tar membership, every captured byte, frozen Git blobs,
the native export/dependency surface, AOT artifact chains, RSA signatures,
full traversal receipts, duplicate stdout transport, all timing samples,
statistics and gates. Its hostile tests reject path traversal, captured-byte
mutation, a coherently resealed launch-counter mutation, a timing-summary
mutation and an RSA signature bit flip.

- Goal5847 current-path suite: 29/29 passed locally.
- Authority hostile tests: 7/7 passed locally.
- Exact stored-authority recount: byte-identical and passing.
- A broader 198-test local adjacent run: 193 passed, one environment skip and
  four errors. All four errors are old Goal5803 history tests whose required
  Git-excluded archived snapshots are absent on this Mac; they fail at file
  open/stat before behavior assertions. They are disclosed, not repaired or
  relabeled as Goal5847 regressions.
- Before the formal V2 transaction, the exact clean pod/current-path adjacent
  suite passed 192 tests with three environment skips.

## Failed attempt and custody

Formal Attempt 01 is terminal. Its first RTDL worker succeeded, but the
controller read launch counters at the wrong receipt level and stopped before
worker two. Its complete archive is preserved with SHA-256
`d59b368b337d20d928329d1fd919551c49f8e397ba941b45d71bb8e22a80f8ea`.
No Attempt 01 or exploratory timing was pooled into V2. The repaired controller
uses the canonical full receipt verifier and V2 was separately preregistered.

## Final boundary

Goal5847 removes the exact precompiled deploy-path performance blocker without
disabling validation, hiding adverse samples, adding application logic or
regressing steady execution. It is a substantive systems result: one signed,
family-bound RTDL artifact executes with no runtime compiler, reaches its first
correct result faster than the pinned precompiled-PyOptix process contract, and
retains strong prepared performance.

The remaining costs are explicit: about 638 ms post-import RTDL setup, a
94.171 s first-ever materialize/build/sign operation excluded from deployment,
one relation workload, one Ada GPU, uncontrolled storage page cache, test-only
keys and no external review. These boundaries prohibit broad or public claims.
