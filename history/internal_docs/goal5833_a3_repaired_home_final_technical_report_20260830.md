# Goal5833 A3 repaired Home final technical report

Date: 2026-08-30  
Status: `COMPLETE_AT_BOUNDED_STATIC_BUILTIN_SPHERE_SCOPE`  
External review: not requested and not authorized  
Performance timings: zero

## Outcome

Goal5833 is complete, but only at a deliberately narrow and now explicit
scope. RTDL has a public built-in-sphere path that takes a four-role Callback
IR program through `verify -> compile -> materialize -> prepare -> execute ->
close`, builds one static OptiX sphere GAS, executes a First Contact program,
checks device status before application output, and agrees with an independent
exact-binary32 CPU oracle on the admitted qualification rows.

This is the third bounded instantiation of RTDL's callback-protocol mechanism:
custom primitives, built-in triangles, and built-in spheres. It is not a
universal family compiler, not a prospective new-application exam, and not a
claim that RTDL supports 75% of OptiX functionality. Curves remain absent.

This report and the machine-readable final result supersede the original
Goal5833 result/report and all intermediate self-reviews. Those records remain
immutable because several of their positive statements were false.

## Exact public capability

The public namespace is `rtdsl.v4_sphere`. A user supplies:

- a restricted four-role Callback IR program (`make_ray`, `closest_hit`,
  `miss`, and `finalize`);
- static sphere centers, radii, and unique application IDs; and
- motion-segment queries.

The compiler supplies the built-in-sphere intersection module and the
candidate enumerator. The application does not provide an intersection
program, PTX, an SBT record, or a private native loader. The selected First
Contact is ordered by exactly `(ordered_float32(t), application_id)`.
Primitive index remains execution provenance and cannot decide a legal tie.
The application IDs must be unique, and the public First Contact output is the
fixed `u32/f32/u32` tuple `(hit, t-bits, application-id)`.

The executed native descriptor reports `OPTIX_BUILD_INPUT_TYPE_SPHERES`,
`OPTIX_PRIMITIVE_TYPE_SPHERE`, a built-in IS module, no user intersection
program, one GAS, one SBT record, five primitives, heterogeneous radii, and
zero motion keys. This is a static, non-motion path.

## The admitted numerical domain

The original Goal5833 report implied complete closed-segment sphere-contact
semantics. That claim was wrong. The controlling path supports only the
following domain:

- every input is projected to binary32 before semantic evaluation;
- each segment start is strictly outside every sphere;
- the exact discriminant separation ratio is at least `2^-12`;
- the front-entry root is more than `2^-12` away from both normalized trace
  endpoints `t=0` and `t=1`; and
- trace depth is one, with no instancing or motion blur.

Callable depth is zero.

Exact tangency, near-degenerate contacts, exact endpoint contacts, and roots
inside the endpoint guard fail closed before native execution. The `2^-12`
constants are conservative engineering-domain restrictions. They are not an
OptiX error theorem and do not authorize a cross-GPU numerical guarantee.

This restriction was introduced after real hardware contradicted the earlier
assumption: on the Home OptiX 9 built-in-sphere path, an exact front contact at
`tmax` was reported as MISS even though the independent closed-segment oracle
classifies it as HIT. The correct repair was to exclude the ambiguous domain,
not to relabel the hardware MISS as mathematical correctness.

## Home functional result

The controlling source is the 377-member archive
`goal5833_a3_final_source_snapshot_v7_20260830.tar.gz`, SHA-256
`861a5d39e3e4661433f8eb7d558f0bc6f30f168f1dc6743e97a84062abbbb01d`.
It contains all source, nine Goal5833 test modules, five adjacent Callback test
modules, and the three Goal5749 dependencies omitted by the prior capsule.

The fresh Home execution used:

- Linux `lx1`;
- NVIDIA GeForce GTX 1070, compute capability 6.1;
- driver 580.173.02;
- OptiX 9.0.0; and
- CUDA 12.0.

Pascal has no RT cores. This is behavioral true-OptiX evidence, not RT-core
silicon evidence.

The fresh native is
`e7ae6d04068b989876cb5eec45966a034cdda2676ac9b9581687acd11f29170b`.
The five main rows were:

| Qualification row | Observed `(hit, f32(t)-bits, application-id)` |
|---|---:|
| Equal-time coincident spheres; lower application ID wins | `(1, 1056964608, 2)` |
| Transverse miss | `(0, 1065353216, 4294967295)` |
| Nearer time precedes a smaller later ID | `(1, 1050673152, 99)` |
| Well-conditioned grazing front entry | `(1, 1050673152, 11)` |
| Intersection beyond the segment end | `(0, 1065353216, 4294967295)` |

All five rows match the independent CPU oracle under exact-bit policies. A
second execution on the same prepared owner ran three reversed rows and also
matched. The lifecycle execution counts were `0 -> 1 -> 2`.

The main execution binds:

- Callback IR `60314121...ae5d`;
- physical schema `1b35f180...9f6c`;
- target `40fd2447...be7b`;
- canonical plan `0232be37...517e`;
- Callback ABI `8f63b85d...9652`;
- authority `79462784...ef7b`;
- executable `14b29948...3878`; and
- composed PTX `1665f6d3...45cc`.

## Negative boundaries and failure-path evidence

Three distinct numerical rows were rejected before launch. In every case the
prepared execution count remained `2 -> 2`:

1. Exact tangent: the independent closed-sphere oracle gives HIT at `t=.5`,
   application ID 11; the public path returns
   `exact_tangent_unsupported_by_optix9_front_face_contract`.
2. Just beyond `tmax`: the exact front root is approximately
   `1.0000000596046483`, and the closed-segment oracle gives MISS; the public
   path returns `front_entry_near_closed_trace_interval_boundary`.
3. Exact `tmax`: the closed-segment oracle gives HIT at `t=1`, application ID
   2; the same endpoint-boundary reason rejects it.

The hostile Callback IR changes only `make_ray`'s `tmax` from `ONE_F32` to
`ZERO_F32`. It materializes into a distinct executable and reaches one complete
OptiX launch. Device status reports error 9. The host downloads status once,
downloads application output zero times, and records zero output transfers
after failure. Thus status-before-output is executed failure-path evidence,
not merely source order.

An intentional post-launch expected-output mismatch also unwinds through the
context manager and closes its prepared native owner. This closes the teardown
segfault exposed by an earlier leaked-owner attempt.

## Tests and independent recount

The exact source passed:

- 56 controlling sphere tests;
- 14 explicitly noncontrolling `FamilySchema` prototype tests; and
- 46 adjacent Callback IR/ABI/artifact/PTX regressions.

The 377-member source capsule is complete for this declared Home run, but it
is not a hermetic environment: it intentionally relies on the installed
Python environment, NVIDIA driver, CUDA/OptiX SDK, compiler, headers, and
system libraries. “Source-complete” here must not be read as “offline
hermetic reproduction.”

The independent stdlib-only verifier was copied with the result, native,
oracle, and generated artifacts to a different Home directory and executed
with Python isolated mode. Its recount is byte-identical to the first Home
recount at SHA-256 `f721d210...4b59e`.

The same preserved bundle also passes on Windows. The parsed JSON is identical;
the raw output differs only because Windows writes CRLF and Linux writes LF.
This report therefore claims Linux byte identity and cross-OS JSON identity,
not cross-OS raw-byte identity.

The artifact inventory now includes the original Callback DSL source, trusted
wrapper source/PTX, four generated leaf sources, four compiled leaf PTX files,
composed PTX, compiler options, and NVRTC log for both accepted and hostile
executables. The verifier rehashes the canonical projections and every member,
reconstructs the executable records, and checks receipt/native/oracle
identities.

A second compiler run from the same frozen source and exact native reproduced
all accepted and hostile generated artifact bytes and eleven core identities.
This is compiler-output reproducibility. It is not an independent proof that
the RTDL parser/compiler implements the intended source-to-IR or IR-to-PTX
semantics; a coordinated author can construct a different internally
consistent inventory. The final claim is intentionally limited to preserved
byte inventory plus same-compiler reproduction.

## Failure lineage

The failed attempts are scientific evidence and remain preserved:

- the original result mislabeled a secant as an exact tangent and used an
  unsound binary64 oracle against binary32 execution;
- A2 found that accepted `tmin/tmax` leaves were silently discarded, along
  with physical/native/evidence binding gaps;
- A3 attempts 1 and 2 stopped before GPU execution;
- attempt 3 exposed both the real tangent MISS and a process-exit teardown
  segfault caused by an unclosed prepared owner;
- attempt 4 constructed its cleanup regression from an already-consumed
  executable;
- attempt 5 lost NaN payload bits in JSON evidence;
- `final_home_pass_v6` had valid five-row observations but still accepted
  ambiguous endpoint roots, omitted three capsule dependencies, and shipped a
  verifier that could not move with the preserved native; and
- the first endpoint-repaired successor passed GPU execution but its new
  verifier correctly rejected conflated public-source and normalized-program
  source identities.

No failed result was erased, renamed as success, or reused as the controlling
v8 execution.

## CGO claim boundary

The safe result is:

> On one static, nondegenerate, endpoint-separated built-in-sphere domain,
> RTDL instantiates its whole-callback-protocol mechanism through a public
> lifecycle and executes a First Contact program with exact qualified outputs,
> identity-bound generated artifacts, and fail-closed device status.

The corresponding taxonomy statement is only that RTDL now has kind presence
in three of four coarse OptiX leaf-primitive classes. At the lower-level
OptiX build-input enum denominator it is three of six kinds. Both are
kind-presence implementation counts; neither measures feature coverage within
the kinds.

Goal5833 supplies mechanistic portability evidence for the protocol-contract
idea. It does not supply prospective generalization, third-party usability,
performance, Paper App, curve, RT-CCD, modern RT-silicon, or arbitrary
Callback-IR-to-GPU evidence.

## Controlling evidence

- Machine result:
  `history/internal_docs/goal5833_a3_repaired_home_final_result_20260830.json`
- Raw result and evidence:
  `history/internal_docs/goal5833_a3_repaired_home_evidence_20260830/final_home_pass_v8`
- Closed-world 120-member evidence manifest:
  `history/internal_docs/goal5833_a3_repaired_home_evidence_20260830/final_home_pass_v8_manifest_v2.txt`
  at SHA-256
  `0d439cd33d65a4787d097715cd87141222816766feaff2615b6c9ba05f095e15`.

No CFR was created and no external review was requested.
