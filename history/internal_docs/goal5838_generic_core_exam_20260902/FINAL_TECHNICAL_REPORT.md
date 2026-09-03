# Goal5838 final technical report

Date: 2026-09-03

Status: `PASS__GOAL5838_COMPLETE_AT_PREREGISTERED_BOUNDED_SCOPE`

## Executive result

Goal5838 asked whether one schema-driven RTDL V4 core could be implemented,
sealed before learning a challenge, and then execute an independently selected
new callback topology without changing a byte of that core. The answer is yes
for one bounded prospective topology:
`builtin_sphere::any_hit_count_continue_u64_per_query`.

The final clean-commit run produced two true OptiX executions. All 12 output
rows matched the independent exact-rational CPU oracle, and all three frozen
core files remained byte-identical. An RTDL-free verifier rederived the
artifact, source identities, native-library identity, physical traversal
receipts, and oracle result. The final authority seal is
`c0578a22e006e2bee2dec39e6de98201ce547eca95dc20b6b7f4c1a891479a8e`.

This result is not evidence for arbitrary Callback IR, universal provider
portability, performance, a Paper App, application correctness, external
review, or consensus.

## Scientific question and controls

The preregistered question was:

> Can RTDL replace concrete-family dispatch with one schema-driven admission,
> compilation-plan, provider-binding, and public lifecycle core, freeze that
> core, and then execute an independently selected new callback topology
> without changing any frozen-core byte?

The controls were established in this order:

| Event | Commit or authority | Information boundary |
| --- | --- | --- |
| Baseline frozen | `0f5c9d4297f73e412732e5a8ab133423fe4cfd21` | Zero prospective successes |
| Preregistration | `d0e218a` | Question, success rule, and failure rule fixed |
| Generic core implemented | `3b2f540` | Selected topology still unknown |
| Challenge protocol and pretarget calibration | `7abab6e`, `19b3fda` | Future NIST pulse fixed before revelation |
| Core and ten-row table sealed | `1ad0628` | Three core files immutable; no row selected |
| Independent selection recorded | `3c66f19` | NIST pulse selected stable row 3 |
| Selected extension implemented | `affbc8b` | Only provider/protocol/app/test layers changed |
| Final execution source | `7da68056550818d8e2f6cdb4d7aa3e9029cc4524` | Clean detached Pod checkout |

The frozen core is exactly:

- `src/rtdsl/v4_family_schema.py`;
- `src/rtdsl/v4_generic_family_lifecycle.py`; and
- `src/rtdsl/v4_family.py`.

Their aggregate authority seal is
`c2a461c8a4a61650044b724d103a80d25241b44b7b486c071b601946292e5dae`.
The post-seal diff from `1ad0628` through the execution commit is empty for all
three files.

The complete challenge-table seal is
`0a2b2c01aed75ad08fad44f7fbc2509ef632d786545e0202b9a4b27425a30345`.
The NIST-based selection-result seal is
`9f543f52cd9453e0410766aa79c3f302a6a0e39314487279842fa5ad5e57ed61`.
At selection time, candidate implementation, candidate execution, GPU receipt,
and prospective-success counts were all zero.

## Selected topology and implementation

The selected topology has four Callback-IR roles:

| Role | Effect |
| --- | --- |
| `make_ray` | Emit one trace request per query |
| `any_hit` | Increment the U64 payload and continue traversal |
| `miss` | Return the final payload |
| `finalize` | Commit one U64 result per query |

The selected implementation follows the public generic lifecycle:
`compile -> materialize -> prepare -> execute -> close`. The frozen core owns
schema admission, canonical planning, provider binding, lifecycle state, and
generic receipts. Post-selection modules own the selected restricted Callback
IR, ABI proof, Numba leaf generation, trusted OptiX wrapper, and sphere-provider
binding. The case study owns only centers, radii, queries, case names, and the
independent oracle.

The provider builds one static built-in-sphere GAS and uses the OptiX built-in
intersection module. There is no user intersection program. Its generated
wrapper calls `optixTrace`; every accepted sphere hit reaches the any-hit role,
increments the U64 payload, calls `optixIgnoreIntersection`, and lets traversal
continue. The miss and finalize roles expose the per-query count. No primitive
metadata channel or application vocabulary is present.

No post-selection commit changed native C++ engine source. The provider DSO was
built from the existing full generic provider rooted at
`src/native/rtdl_optix.cpp`; selected code was added only in the allowed
extension, case-study, runner, verifier, and test layers.

## Pod and toolchain

The owner supplied only `root@213.173.108.100:12943`; environment provisioning
and compatibility negotiation were agent-owned.

| Property | Final value |
| --- | --- |
| OS | Ubuntu 24.04 |
| GPU | NVIDIA RTX 2000 Ada Generation, 16,380 MiB |
| Compute capability | 8.9 |
| Driver | 580.159.04 |
| CUDA | 12.8 / NVCC 12.8.93 |
| Host compiler | Ubuntu GCC 13.3.0 |
| Python stack | Python 3.12.3, NumPy 2.4.4, Numba 0.65.1 |
| Selected OptiX headers | 9.0.0, `optix-dev` commit `fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd` |
| Compiler-environment identity | `d12ed9d24a1857e95aa68ac2f115a9d891361b082389ad10bb99bff0db3f11a8` |

OptiX 9.1.0 at exact `optix-dev` commit
`f1f6dd803f3159992d248178f6e09421c6eb8b6d` compiled all four callback roles,
but its zero-launch `optixInit()` probe returned 7801 against this host. OptiX
9.0.0 passed that probe and was selected. This was SDK/driver ABI negotiation,
not a topology or core change.

The final compiler identity binds the exact NVRTC, NVVM, and libdevice files.
The provider DSO dynamically resolves the same versioned NVRTC bytes checked by
preflight and the verifier.

## Final execution evidence

The final run used a clean detached checkout of
`7da68056550818d8e2f6cdb4d7aa3e9029cc4524`. Generated artifacts were written
outside the Git checkout and copied to the Mac before Pod teardown.

| Evidence | Internal seal | Committed file SHA-256 |
| --- | --- | --- |
| Pod preflight | `ba20a3823032d37051c734cb0c1504618f9fdcee08483fbaadad52cca90155` | `a001e285fae610d5154528ec326104c3252011773e15324f6c9760f1ebf90f5c` |
| Native build manifest | `38523a2943177bc43735654d49cccf9a067e4e6428ac4ddf1cfb14aa623ece94` | `670782153e65a0ac9b5a9472aba981144861dc1d55fae49ef0aa2d90ee3fb9ad` |
| GPU exam | `89542280e402a663fbda184a2f8efd6e65447f67a922dbfa1c2f07c30f309dd0` | `560b88e53aa5bebaca0d6e1cf98ae19bfee9b9f0bda0187bdfa2b80344431593` |
| RTDL-free verification | `fb9d4ee3c779185eacb9f7db08038d824e1388d35a11bc3efb45899476f15b00` | `3451b9127260ef962a0d800302ec16dd2bb2d159debb5dec3e09476594b26783` |
| Final authority | `c0578a22e006e2bee2dec39e6de98201ce547eca95dc20b6b7f4c1a891479a8e` | `dafea025d8f9583cd186e914f6e2974b6aab2fdd59781a6d2a39087e0def7ce8` |

The generated provider DSO is 7,181,936 bytes with SHA-256
`c91a22edbd7855824c6ad111a11c77aa599bdbb767b54b0d2e3f4355a1932076`.
Generated native binaries are not committed to Git. The raw DSO remains in the
off-repository evidence directory, while its exact identity, inputs, exported
ABI checks, source inventory, and reproduction command are committed.

## True-RT and correctness result

The physical descriptor and traversal receipt record:

| Check | Observed value |
| --- | --- |
| Build input | `OPTIX_BUILD_INPUT_TYPE_SPHERES` |
| Primitive | `OPTIX_PRIMITIVE_TYPE_SPHERE` |
| Intersection implementation | OptiX built-in module; user intersection program false |
| Static geometry | 6 spheres, 1 GAS, no motion blur |
| Pipeline | 3 program groups, max trace depth 1 |
| SBT | 1 record |
| Any-hit guard | `OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL` |
| Continuation | `optixIgnoreIntersection` |
| Query launch | 6 raygen invocations per execution |
| Traversal classification | `optix_traversal_observed` for both executions |
| Launch accounting | 2 attempted, 2 successful, 0 failed, 0 incomplete |

The primary query order produced `(4, 1, 1, 0, 4, 0)`. The independently
checked reverse order produced `(0, 4, 0, 1, 1, 4)`. Both exactly matched the
oracle, yielding 12/12 exact rows. The reverse execution used the same prepared
family and raised its provider execution count from one to two. Close was
idempotent, and the lifecycle remained process-bound, thread-bound,
nonreentrant, and nonserializable as declared.

The RTDL-free verifier imported no RTDL module and rederived 34 source-file
identities, the selected fixture, family identities, native DSO bytes, physical
receipts, two true launches, 12 oracle matches, and zero frozen-core changes.
Running the same verifier on the Mac produced byte-identical verification JSON.

## Repairs and validity

The first diagnostic Pod run proved the path but was not promoted to final
evidence. It exposed three verifier assumptions: Git OIDs were incorrectly
treated as 64-hex SHA-256 values, detached HEAD was rejected, and the verifier
expected the provider receipt without the frozen generic lifecycle wrapper.
All were repaired with negative regressions, committed, and followed by a
fresh full run from one later clean commit.

The builder also initially passed a versioned NVRTC shared object directly to
NVCC, which CUDA 12.8 rejected. An isolated probe established the exact-linker
form, and the builder plus independent command rederivation were repaired. The
compiler path and bytes remained exact throughout.

These repairs affected only mutable build or evidence tooling. They did not
change the selected topology, fixture, oracle, provider semantics, or any
frozen-core byte. The complete incident history is retained in
`FIRST_POD_EXECUTION_REPAIR_LOG.md`.

The final whole-cohort audit also exposed a preexisting compositional defect in
the Goal5837 verifier: its frozen historical source inventory rehashed the
current `AGENTS.md`, so the legitimate Goal5838 status update at `f5ba21f` had
already invalidated it. The verifier now reads those inventory bytes from the
exact Goal5837 authority commit `0f5c9d4`; the stored authority was not
rewritten, and current semantic/API observations remain current. This
post-evidence tooling repair is documented separately in
`goal5837_owner_grouped_classification_20260902/POST_FREEZE_COMPOSITIONAL_VERIFIER_REPAIR.md`.

## Verification status

The final local focused denominator is 91/91 Goal5838 tests. The inherited
built-in-sphere Goal5833 denominator is 70/70. Ruff, Python compilation,
generic-core seal verification, selection verification, final-authority
rederivation, and frozen post-seal diff checks pass. The known historical
Goal5832 current-tree custody error remains unrelated and is not rewritten.
The complete Goal583x run is 312/313 with exactly that one known error; all 19
Goal5837 tests now pass.

## Exact conclusion

Goal5838 is complete at its preregistered bounded scope. The experiment supplies
one prospective counterexample to the narrower concern that every new callback
topology necessarily requires concrete dispatch or a semantic edit in the V4
core. It does not establish that every future topology will fit. The correct
research claim is therefore one independently selected, true-OptiX,
frozen-core-preserving success, not a universal generic-compiler claim.
