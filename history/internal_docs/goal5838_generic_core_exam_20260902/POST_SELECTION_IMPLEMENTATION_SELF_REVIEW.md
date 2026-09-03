# Goal5838 post-selection implementation hostile self-review

Date: 2026-09-03

Verdict: `READY_FOR_CLEAN_COMMIT_AND_TRUE_GPU_EXAM__NOT_YET_SUCCESS`

Review type: internal hostile self-review. External review was owner-deferred
while traveling and no external consensus is claimed.

## Question under test

Can the three-file schema-driven family core frozen before challenge selection
execute the independently selected
`builtin_sphere::any_hit_count_continue_u64_per_query` topology without one
byte of frozen-core modification?

The post-selection implementation uses only preregistered mutable layers:
restricted Callback IR, selected protocol/compiler/provider adapters, case
fixture and independent oracle, tests, runner, verifier, and build tooling. It
does not modify the frozen core:

| Frozen file | SHA-256 at seal and current review |
| --- | --- |
| `src/rtdsl/v4_family_schema.py` | `2d118697d10cb2bc2a8672700ae5a991eaf94e66834bb3e08fd898323720f224` |
| `src/rtdsl/v4_generic_family_lifecycle.py` | `7ac68832de9d1e04fdd6f0f11bfa0de7d6109d892ab22e42c9aeb2825d28228c` |
| `src/rtdsl/v4_family.py` | `d25c487823e966a8e9083092811c9a1a2b6aa0fef6ce8f3a0a5b8919c5b809e8` |

The preselection route adapter also remains byte-identical at
`ff576b65d0161b3593a1509614edbf5cdea3aa63a68c63eebd49908f0815e1b8`.

## Architecture review

The family core sees only a canonical schema, plan, program-artifact bundle,
provider descriptor/projection, and lifecycle capabilities. It contains no
sphere branch and no selected-topology branch. The selected package-external
provider declares the five selected capabilities and reaches the same generic
`compile -> materialize -> prepare -> execute -> close` front door used by the
migrated pre-seal routes.

The Callback IR contains exactly four roles:

| Role | Effect |
| --- | --- |
| `make_ray` | Construct one finite segment trace with zero U64 payload |
| `any_hit` | Checked U64 increment and accept-continue |
| `miss` | Return the accumulated payload after ignored intersections |
| `finalize` | Commit one U64 count per query |

The trusted wrapper contains one `optixTrace`, no closest-hit program, and one
`optixIgnoreIntersection`. The existing native provider builds one OptiX
built-in-sphere GAS with
`OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL`, obtains the built-in sphere
intersection module from OptiX, and binds one SBT record. It does not contain
the selected count operation. The count operation is compiled from the
restricted callback leaves after selection.

The native ABI retains an `application_ids` compatibility column from the
pre-existing sphere provider. This selected wrapper never reads it. The public
extension supplies consecutive provider-private IDs, declares no metadata
channel, and exposes neither ID nor hit order in its result.

## Independent correctness review

The fixture contains six spheres and six conditioned finite segment queries,
including duplicate centers, multiple hits, offset hits, misses, and reverse
direction. The expected counts are `(4, 1, 1, 0, 4, 0)`.

The oracle imports no RTDL module. It first projects inputs to binary32 and then
uses exact `Fraction` arithmetic to classify the front sphere root against the
closed segment interval without numerically evaluating a square root. A second
direct-root implementation cross-checks 1,900+ deterministic random cases away
from discriminant and endpoint boundaries. The exact oracle rejects
start-inside and exact-tangent cases rather than pretending to prove a boundary
convention not covered by this bounded exam.

The independent result verifier imports no RTDL module. It hardcodes and
rederives the fixture, output, frozen authority identities, generic plan and
provider identities, native content fingerprints, physical descriptor,
device-role masks and counters, traversal-audit mixes, and result seals. The
native output fingerprint uses the wrapper's exact `0x7fffffff` observed-hit
sentinel bits; it does not normalize the NaN.

## Defects found and repaired before the GPU exam

1. The first build recipe targeted `rtdl_optix_v4_product.cpp`, but static
   inspection proved the current `RTDL_V4_PRODUCT_ONLY` guard excludes the
   built-in-sphere lifecycle ABI. The builder now compiles the existing full
   generic provider from `rtdl_optix.cpp` plus its CUDA helper and verifies the
   exact required exported symbols. No native source was changed.
2. The first independent verifier reconstructed the observed-hit NaN through
   Python's default NaN, whose binary32 bits can differ from the wrapper's
   explicit `0x7fffffff` sentinel. The verifier now reconstructs the exact
   sentinel bits, and a known-answer test binds both primary and reversed
   output fingerprints.
3. A generic-lifecycle mock returned `(4, 1, 0)` for the first three fixture
   rows although the independent oracle says `(4, 1, 1)`. The mock and
   assertion now use the true expected result.
4. The independent verifier could overwrite an existing output, including its
   input artifact. Verification output is now required outside the Git tree,
   distinct from the artifact, atomically published, and exclusive.

These are extension, evidence, and build-tool defects in explicitly mutable
post-selection layers. None demonstrates a need to modify frozen-core bytes,
so none satisfies the preregistered five-part scientific-failure condition.

## Local evidence

All commands used Python 3.12.14, Numba 0.65.1, and NumPy 2.4.4 from
`/Users/rl2025/.venvs/rtdl-goal5837-py312` with `PYTHONPATH=src:.`.

| Check | Result |
| --- | --- |
| Selected implementation tests under random hash, debug allocator, and `-W error` | 16/16 pass |
| All Goal5838 tests under `-OO`, random hash, debug allocator, and `-W error` | 69/69 pass |
| Reused Goal5833 sphere-provider tests under the same strict mode | 70/70 pass |
| Selected Python `compileall` | pass |
| Ruff `E,F,I,UP` with only `E501` excluded | pass |
| Stored generic-core seal verifier | pass; frozen changes 0 |
| Stored independent-selection verifier | pass; selected index 3 |
| Broad normal Goal583x discovery | 269/271 pass; exactly two disclosed historical errors |

The two broad errors are not Goal5838 regressions. Goal5832 rehashes a
Goal5831-era source-authority byte count after legitimate later exports, and
Goal5837 compares its historical authority against a later AGENTS file. Both
conditions already existed at the independent-selection commit. They must not
be erased by rewriting historical authorities.

## Remaining risks and required gate

Local macOS cannot compile or execute this OptiX path. The following statements
remain unproven until one clean-pod run succeeds and the independent verifier
accepts its artifact:

- the full generic native provider builds against exact OptiX 9.0.0 and the
  visible GPU's CUDA architecture;
- the four independently compiled Numba leaves link with the NVRTC wrapper;
- OptiX invokes one any-hit callback for each intersected sphere primitive;
- primary and reverse-order executions match all twelve oracle rows;
- native descriptors, device fingerprints, role counters, and traversal audit
  all agree with the independent reconstruction; and
- the repository and frozen core remain clean before and after execution.

The fixture is intentionally bounded and conditioned. It does not test exact
tangency, start-inside behavior, arbitrary callback programs, broad provider
portability, performance, or application correctness. The full provider DSO
exports unrelated generic RTDL symbols because the current product-only build
excludes the sphere ABI; the build manifest therefore proves presence of the
required symbols, not exclusivity of the DSO.

## Claim decision

Goal5838 is not complete at this checkpoint. There is no GPU result, speedup,
Paper App, arbitrary-callback, external-review, or consensus claim. The correct
next action is to commit and push the exact clean exam source, build that exact
commit on one visible NVIDIA GPU, run the public generic lifecycle twice
(primary and reverse query order), and independently verify the immutable
artifacts. A verified pass is the intended CGO evidence; an ordinary build or
extension defect must be repaired rather than mislabeled as scientific
failure.
