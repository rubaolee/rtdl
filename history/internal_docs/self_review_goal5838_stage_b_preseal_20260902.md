# Internal hostile review: Goal5838 Stage B before generic-core seal

Date: 2026-09-02

Verdict: `ACCEPT_STAGE_B_FOR_BYTE_FREEZE__P0_0_P1_0_P2_4_P3_3`

Review mode: strict internal self-review only. External review is unavailable
under the owner's 2026-09-01--02 travel constraint. This document is not
independent review and does not establish multi-AI consensus.

## Reviewed scope

- `src/rtdsl/v4_family_schema.py`
- `src/rtdsl/v4_generic_family_lifecycle.py`
- `src/rtdsl/v4_family.py`
- `src/rtdsl/v4_family_route_adapters.py`
- `tests/fixtures/goal5838_external_provider.py`
- `tests/goal5838_generic_family_lifecycle_test.py`
- `tests/goal5838_family_route_migration_test.py`
- `scripts/goal5838_freeze_generic_core.py`
- `scripts/goal5838_select_challenge.py`
- the preregistration and pretarget selection protocol

The review inspected admission/dataflow checks, complete artifact handoff,
provider descriptor and executable identity binding, lifecycle state and
affinity, error/output publication, migration classification, package-external
provider use, candidate enumeration, and selection cryptography. It also ran a
forbidden-vocabulary scan over the three proposed core files.

## Resolved attacks

1. **Concrete dispatch disguised as a compiler.** The three core files contain
   no application, concrete geometry, OptiX, Embree, CUDA, triangle, sphere,
   curve, or relation dispatch. Geometry knowledge is isolated in provider and
   route-adapter code. The public family facade exports only schema, artifact,
   requirement, provider, and lifecycle objects.
2. **Hash-only wrapper glue.** Providers receive the complete canonical
   callback program, verification summary, ABI, and behavior-schema bytes.
   Bundle identity is cross-bound to the canonical plan. A provider cannot pass
   conformance by receiving only hashes.
3. **Self-attested provider drift.** Provider descriptors are reconstructed and
   compared before and after projection/materialization; executable identities
   are reconstructed before and after prepare/execute. Plan, target,
   toolchain, artifact bundle, provider artifact, and generated artifact
   identities are checked fail-closed.
4. **Lifecycle races and partial output.** Prepare is single-use and guarded by
   a nonblocking lock; recursive prepare/execute is rejected rather than
   deadlocking. Process/thread affinity, non-reentrancy, close invalidation,
   malformed receipts, provider errors, and immutable output publication are
   tested.
5. **Retrospective route promotion.** The two stable constructors remain exactly
   two stable constructors. The owner-grouped route remains one closed
   successor. Migration changes no classification and contributes no
   prospective success.
6. **Project-internal-only plugin claim.** The conformance fixture is outside
   `src/rtdsl`, imports only `rtdsl.v4_family`, and completes the full public
   lifecycle. It is still a project-authored CPU fixture, not an external human
   provider or GPU result.
7. **Convenient post-hoc challenge.** A complete finite table and mapping are
   committed before the target pulse. Two exact pre-existing triangle callback
   topologies are conservatively excluded; near matches are not called unseen.
   Selection uses a single exact future NIST pulse, with no alternate pulse.

## Open P2 limitations

1. **Providers remain trusted.** The core verifies declared requirements,
   immutable identities, artifact transport, lifecycle receipts, and output
   shape. It does not prove that arbitrary provider machine code semantically
   implements Callback IR. Goal5840 must add an independent target-side
   extractor/refinement argument.
2. **Migrated OptiX providers are bridges, not fresh generic code generation.**
   They exact-match the plan and complete artifact bundle before delegating to
   previously trusted concrete materializers. This demonstrates one generic
   control/lifecycle boundary, not arbitrary provider synthesis.
3. **External-provider conformance is CPU-only and project-authored.** It proves
   package-external API reachability, not third-party usability, independent
   implementation, portability, or GPU execution.
4. **The challenge universe is intentionally bounded.** It covers four already
   exercised primitive kinds and three declared callback/result topologies. It
   is not a complete OptiX topology universe, all Callback IR, IAS, motion
   transforms, recursion, callables, or arbitrary application semantics.

## Open P3 limitations

1. The live Beacon 2.0 service uses a DER certificate identifier and four-byte
   non-integer signing lengths, which differ from one reading of draft NISTIR
   8213. The exact live variant and certificate were fixed and successfully
   calibrated at `2026-09-02T18:10:00Z`, before the target. Selection uses the
   signed and prior-precommitted local random field, not the unresolved derived
   output formula. No post-target variant switch is allowed.
2. Goal583x regression is `264/265`; the sole error is the already registered
   Goal5832 current-tree custody mismatch caused by later legitimate root export
   changes. Rewriting that historical manifest would destroy evidence and is
   forbidden. Focused Stage-B tests are `67/67`.
3. External critical review count is zero. It remains a later gate before final
   paper claims; this internal review may not be counted as independent review.

## Seal decision

There is no P0 or P1 defect requiring a generic-core change before freezing.
The remaining items are explicit claim ceilings or separately planned work,
not hidden success assumptions. The owner instructed the project to finish
Goal5838 and the CGO submission while preserving genuine negative evidence.
Stage B may therefore freeze the exact three-file generic core and the complete
challenge table.

The freeze itself is not a prospective success. The count remains zero until
the independently selected row passes schema and Callback-IR admission,
provider binding, public `compile -> materialize -> prepare -> execute -> close`,
an independent CPU oracle, hostile cases, and a true-GPU receipt with zero
frozen-core byte changes.
