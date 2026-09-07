# Protocol Witness and Fact Derivation

Date checked: 2026-09-06 America/New_York.

Status: `N2_COMPLETE_WITH_CLAIM_DOWNGRADE__AUTHOR_SCOPE__FINAL_REVIEW_PENDING`.

This report traces one RTDL protocol seam from requirement to representation,
target-side fact, admission point, execution guard, and public result. It is a
read-only audit of the measured implementation M and the current source. It
does not add a test, rerun a GPU experiment, prove a general soundness theorem,
or authorize a manuscript claim.

## 1. Identity and scope

| Item | Identity |
| --- | --- |
| Measured implementation M | commit `d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Read-only audit starting HEAD | commit `50ca45521013f56b141402f4902a3af189b469f9`, tree `3651be79cff13aa9493fe9cc0558c6c26ab5bb92` |
| Protocol implementation difference from M | None in the files hashed in Section 8 |
| Evidence type added here | Source trace and local replay of already committed unit checks only |
| GPU execution in this audit | None |

## 2. Running example: same machine type, different meaning

### 2.1 Intended relation

Consider two indexed physical primitives and two source queries:

| Physical primitive index | Application `item_id:u32` | Source query ID | Intended overlap row |
| ---: | ---: | ---: | --- |
| 0 | 10 | 100 | `(100,10)` |
| 1 | 20 | 101 | `(101,20)` |

The bounded-relation output is a canonical sequence of `(source_id:u32,
item_id:u32)` rows. The application expects `((100,10),(101,20))`.

The trusted relation schema names the second row source
`verified_intersection_attribute0_item_id`. In the selected OptiX lowerer, the
intersection program reports `primitive.item_id` in attribute slot zero; the
any-hit wrapper reads `optixGetAttribute_0()` into `row.item_id`. Source IDs
come from the query object's application ID. This is the adjacent correct
combination.

### 2.2 Illustrative defective combination

If only the producer meaning changes so attribute zero carries the physical
`primitive_index` while the consumer and declared relation still interpret it
as application `item_id`, the apparent rows become `((100,0),(101,1))`.
Every field remains a valid `u32`; the row width, alignment, capacity, and
machine-level load/store behavior can remain valid. The defect is the semantic
producer/consumer relation, not a memory-layout error.

This defective output is **illustrative, not executed evidence**. Repository
history contains it in the Goal5794 execution plan, but the current audit found
no retained run that executed that exact defective source route. The current
manuscript's statements that this route was "executed," "reached launch," and
"returned" those rows therefore exceed the evidence and must be replaced.

### 2.3 Adjacent control discipline

The useful conceptual control changes only one fact:

| Element | Correct control | Illustrative defect |
| --- | --- | --- |
| Physical objects and queries | Identical | Identical |
| Machine type and attribute slot | `attr0:u32` | `attr0:u32` |
| Consumer interpretation | application item ID | application item ID |
| Producer value | `primitive.item_id` | physical `primitive_index` |
| Expected semantic rows | `(100,10),(101,20)` | consumer would observe `(100,0),(101,1)` |

No retained end-to-end execution of the right-hand column was found. The
existing adjacent correct public-lifecycle test also uses a mocked backend; it
checks publication/lifecycle logic but is not a native OptiX execution control.

## 3. Where the requirement comes from

The phrase "the compiler infers that attribute zero means item ID" would be
incorrect. The actual chain is:

1. `BoundedRelationEmissionSchema.row_sources` has the trusted default
   `(launch_source_id, verified_intersection_attribute0_item_id)` in
   `src/rtdsl/v4_bounded_relation.py:88-122`.
2. `compile_bounded_relation_contract` re-verifies a live authority and copies
   those enum values into `CompiledBoundedRelationContract.row_sources` at
   `src/rtdsl/v4_bounded_relation.py:275-299`.
3. The public-side declaration is family-fixed by
   `_declared_attribute_ownership` to
   `attr0=verified_intersection_attribute0_item_id` at
   `src/rtdsl/v4_callback_lifecycle.py:855-862`.
4. The target-side projection reads `contract.row_sources[1]` in
   `_compiled_attribute_ownership` at
   `src/rtdsl/v4_callback_lifecycle.py:865-878`.
5. `_materialized_protocol_contract_decision` compares declaration and
   projection through `verify_protocol_contract` at
   `src/rtdsl/v4_callback_lifecycle.py:1012-1026`.

The schema is a trusted semantic assertion admitted by earlier verification.
The target-side fact is separately derived from the compiled contract, but both
derivations live inside the same compiler and ultimately rely on the trusted
schema. They are not independent trust roots. The check catches drift between
two representations; it does not discover the application's intended meaning
from arbitrary code or prove that the schema author chose the right meaning.

## 4. Five admitted seams and their fact sources

| Obligation ID | Declared value and source | Target extraction and actual object read | Comparison point | Failure behavior | Trusted premise | Positive/negative evidence | Not covered |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `PC-01_ROLE_EFFECT` | `_declared_role_effects(program.callback)` walks verified callback IR | `_compiled_role_effects(abi)` reads `CompiledCallbackAbi.roles[*].effects` | `verify_protocol_contract`, `CP001_ROLE_EFFECT_MISMATCH` | Materialization raises `PL036_PROTOCOL_CONTRACT_REJECTED` before a materialized object is returned | IR verifier and ABI compiler faithfully represent role effects | Pure mutation test and integrated projection-mutation test pass at current HEAD | General equivalence of arbitrary callback code and generated device behavior |
| `PC-02_ATTRIBUTE_OWNER` | Family-fixed declaration `attr0=verified_intersection_attribute0_item_id` | Reads `CompiledBoundedRelationContract.row_sources[1]`, copied from trusted emission schema | `CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH` | Same pre-materialization rejection; prepare also rechecks stored verdict before native load | Schema/provider declaration gives the intended semantic name; lowerer honors contract | CP002 mutation sensitivity passes at pure and integrated gates; correct mocked output is `(100,10),(101,20)` | Automatic inference of app meaning; an executed `(100,0),(101,1)` defect; independent target trust root |
| `PC-03_PHYSICAL` | `ProtocolPhysicalPlan` provides geometry family, output contract, reducer algebra, template ID, plus program protocol digest | `_compiled_protocol_facts` reads physical authority schema and compiled relation/reducer contract | `CP003_PHYSICAL_BINDING_MISMATCH`, grouped with family/task identity | `PL036` before object return | Trusted physical authority and contract describe the actual specialized lowerer | Single-field mutation and integrated gate pass | Proof that every topology-specific wrapper implements arbitrary plan semantics |
| `PC-04_CONTINUATION` | Fixed `REQUIRE_COMPLETE_BEFORE_CONSUME` | `_compiled_protocol_facts` checks runtime status codes and fail-closed relation/reducer contract | `CP004_CONTINUATION_STATUS_MISMATCH` | `PL036` before load; during execute, nonzero device error/status blocks application result with `PL029` | Native wrapper reports status faithfully and host reads the complete status object | Mutation tests pass; execute source shows status check before result construction | A general progress theorem; recovery after failure; correctness of app oracle |
| `PC-05_EXEC_ID` | `checked_executable_sha256` uses the just-produced executable digest | Projection receives that executable digest as `actual_executable_sha256` | `CP005_EXECUTABLE_IDENTITY_MISMATCH` | `PL036` before materialized object return | Digest function and compiler object identity are trusted | Identity mutation tests pass | Semantic correctness of equal bytes; independent derivation at the CP005 comparison itself |

### 4.1 Why PC-05 is useful but limited

At the contract-comparison point, declaration and projection both receive the
same `executable_sha256` argument. CP005 is therefore primarily a substitution
or representation-drift guard; it is not independent evidence that the bytes
implement the source semantics.

The broader `ProtocolExecutableIdentity` is more informative. It binds the
program identity, target, physical schema, compiled contract, ABI, generated
executable, composed PTX, and native library digests
(`v4_callback_lifecycle.py:625-676`). The native library is hashed before and
after `ctypes.CDLL` load (`1180-1197`). Execution checks returned PTX and native
library identities against the materialized identity (`1572-1577`), validates
device status (`1578-1591`), validates output digest (`1592-1617`), and validates
the traversal receipt (`1618-1690`) before constructing and returning the
public result (`1691-1701`). These checks establish identity coherence and
fail-closed publication for the implemented paths. Equal hashes still do not
prove semantic correctness.

## 5. Admission and publication timeline

| Boundary | Actual check | Consequence |
| --- | --- | --- |
| IR verification | Role legality and exact effect fields/types in `v4_callback_ir.py:1247-1292` | Invalid callback IR is not verified. |
| ABI compilation | Re-verifies the callback/physical authority and flattens role inputs, effect variants, status, tags, and symbols in `v4_callback_abi.py:344-435` | ABI cannot be minted from an arbitrary unverified dataclass. |
| Target materialization | Builds specialized authority/contract/ABI/executable, forms protocol declaration/projection, compares five seams in `v4_protocol_contract.py:269-329` | A rejection raises `PL036` before `MaterializedProtocolProgram` is returned. |
| Preparation/native load | Stored verdict is checked again at `v4_callback_lifecycle.py:1406-1413`; exact native bytes are checked around load | A rejected route does not load the native provider through this entry. |
| Launch/result collection | Native status, PTX/native identities, output digest, and receipt are checked | Device failure or inconsistent identity cannot be published as a normal result. |
| Public return | `ProtocolExecutionResult` is constructed only after the preceding checks | This is the implemented public publication boundary. |
| Experiment worker oracle | Goal5848 workers compare expected outputs outside the compiler timer | This is experiment evidence, not a guarantee performed by every RTDL call. |

The existing manuscript phrase "before launch" is safe only when tied to the
specific materialization/prepare checks. It must not imply that every possible
semantic defect is statically rejected or that the experiment oracle is part of
the compiler.

## 6. One concrete typed-effect lowering chain

The following is an actual source/code-generation path, not pseudocode. It is
shown for the admitted triangle-reduction topology because that wrapper visibly
consumes generated effect tags. It does not imply that every topology accepts
every `EffectKind`.

1. A callback return is represented as
   `ReturnEffectStatement(CallbackEffect(kind, fields))`
   (`v4_callback_ir.py:295-304,355-360`).
2. `_verify_effect` checks that the effect is legal for the role and has exactly
   the required typed fields. For any-hit, the language-level set includes
   `ACCEPT_CONTINUE`, `IGNORE`, and `TERMINATE`; a concrete topology may admit a
   smaller subset (`v4_callback_ir.py:1247-1292`).
3. `compile_callback_abi` re-verifies the program, flattens each role's inputs
   and effect variants, assigns stable role/stage/effect tags, and includes the
   first-error status record (`v4_callback_abi.py:196-240,344-435`).
4. The Numba leaf generator evaluates effect expressions, checks effect
   contracts, stores flattened output fields, writes `out.effect_tag` and
   `status.effect_tag`, marks status success, and returns
   (`v4_callback_numba_codegen.py:370-408`).
5. The triangle-reduction OptiX wrapper invokes that leaf. At
   `v4_triangle_reduction_optix_wrapper_codegen.py:386-430`, an admitted
   `ACCEPT_CONTINUE` tag updates the u64 payload and optional event; an admitted
   `IGNORE` tag follows its configured payload behavior; any unexpected tag
   records first error and calls `optixTerminateRay()`. The accepted all-hit
   path writes the payload via `optixSetPayload_*` and calls
   `optixIgnoreIntersection()` so traversal continues without shrinking
   `tmax`.

Thus the user callback returns a typed effect; a trusted topology-specific
wrapper, not arbitrary callback code, performs the hardware control operation.
The wrapper is part of the trusted computing base and remains specialized. The
canonical plan is not itself executable and RTDL does not synthesize arbitrary
wrappers from an unconstrained protocol graph.

## 7. Evidence classification

| Evidence class | Retained/current evidence | What it establishes | What it does not establish |
| --- | --- | --- | --- |
| Declaration/projection field mutation | `tests/goal5797_protocol_contract_test.py:61-118`; six selected checks replayed at current HEAD | Each of five comparison mechanisms is live; CP002 is sensitive to the semantic-owner name mismatch; ablation of that comparison changes this synthetic decision to accept | A real source program passed through the full public compiler and was rejected |
| Integrated projection mutation | `tests/goal5795_v4_public_lifecycle_test.py:268-336`; selected test replayed at current HEAD | Corrupting each target projection at materialization makes the integrated gate reject before `_load_exact_native_library` | Independent target implementation or native/GPU execution of the defect |
| Adjacent correct public control | `tests/goal5795_v4_public_lifecycle_test.py:337-361`; selected test replayed | Public lifecycle publishes mocked correct rows and carries accepted contract identity | Native OptiX correctness, since the owner is mocked |
| Existing correct GPU authorities | Goal5848/5851 M evidence and F2 projection, identities retained elsewhere | The frozen evaluated paths produced expected outputs under their worker oracles and met the recorded gates | The illustrative wrong-output route; a general semantic theorem; a rerun in this audit |
| Executed same-type wrong output | None retained for the `(100,0),(101,1)` route | Nothing | Cannot support "executed," "reached launch," or "returned wrong rows" wording |

### 7.1 Current local validation record

1. A first command omitted `PYTHONPATH=src:.` and failed at import with two
   `ModuleNotFoundError` errors. No tests ran.
2. The prescribed environment then ran both complete modules: 19 tests passed,
   while one custody check errored because
   `history/internal_docs/goal5797_s0_five_mechanism_ablation_preaction_20260823.json`
   is absent from the current repository.
3. Six N2-relevant committed tests were then selected explicitly: valid
   contract, all five single mutations, seal tamper, pre-load block, integrated
   projection mutations, and adjacent correct public lifecycle. All six passed
   in 0.045 seconds.

The missing historical fixture is preserved as a failure and is not repaired
under the executable freeze. The six-test result is not reported as a full
module pass.

## 8. Source identities

The current bytes and M bytes are identical for every implementation/evidence
source in this table.

| File | SHA-256 at M and current audit |
| --- | --- |
| `src/rtdsl/v4_callback_lifecycle.py` | `2038d50934578d63ca9503f8ddbee15098c7ebcead2e533337d4569be09313b0` |
| `src/rtdsl/v4_protocol_contract.py` | `e60f83f5a15df58de2f3f38b681331efb51b797c1b12628ebdaaf1c26a448973` |
| `src/rtdsl/v4_bounded_relation.py` | `4ac50a83ffb80400c6b950150a5702633b3cafa0e43b0b54527f7db44949467a` |
| `src/rtdsl/v4_callback_ir.py` | `edf571196dde4a557b328b5a35fd65e2e57e63cf4a48180d1fa87dba363c1ec7` |
| `src/rtdsl/v4_callback_abi.py` | `3f4be4d998ee91600c6a1f4bba4fadbb435f23d193a49f4cbf6dc50522d74fb5` |
| `src/rtdsl/v4_callback_numba_codegen.py` | `4c72a5886dc43b0f5a3ccb71fd84c5ccb9076110f13813800f188132b69fc29f` |
| `src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py` | `ef1a7ec9a54d150db11ea7aa1eecf87e536b9de7b982e5254b96c627afd533a2` |
| `src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py` | `f7d1f07b4462a6713a4bcda7aaf64f3a480575f1034059f3fbe61d640044eecb` |
| `tests/goal5797_protocol_contract_test.py` | `a24b3a32204b57bbf2e4af3bf3860941d4938e99f3bb304b14ef3ca6a0b82554` |
| `tests/goal5795_v4_public_lifecycle_test.py` | `abfd85654a1ec7aa867b87a4633762eb87f0776188f85a8a592c2f55bc425e31` |

The protocol contract and these two tests entered the retained history at
commit `d0bb938170cd227a33a5237cf5b7e48102cb5c7e`. Later source changes recorded in
the repository did not change the bytes listed above between M and this audit.

## 9. Trust boundary and residual gaps

| Trusted or assumed component | Why it matters | Current limit |
| --- | --- | --- |
| Restricted Python frontend and IR verifier | Supplies typed callback structure | The allowlist and verifier may contain bugs; no general metatheory is proved. |
| Physical schema and relation contract provider | Names semantic sources such as item ID | A wrong but internally coherent declaration can pass; semantics are not inferred from application intent. |
| ABI compiler and specialized wrapper generators | Translate effects and route facts | They are in the TCB; topology-specific code remains substantial. |
| Hash implementation and artifact custody | Tie compared/loaded bytes to identities | Hash equality is not semantic correctness. |
| Native provider status and receipt production | Supports fail-closed public publication | Native/provider bugs or collusion are outside the finite checker proof. |
| Worker oracle | Validates experiment outputs | It is post-execution experiment logic, not a compiler guarantee for all calls. |

The strongest defensible statement is therefore: for the implemented bounded
families, RTDL represents five named route seams, derives declaration and
target projections through distinct compiler paths, rejects mismatches at the
materialization/prepare boundary, and checks identity/status/output/receipt
before public return. It does not independently infer application semantics,
synthesize arbitrary topology lowerers, prove arbitrary semantic equivalence,
or supply an executed wrong-output witness for the illustrative example.

## 10. N2 conclusion and mandatory paper corrections

N2 establishes a real but bounded compiler mechanism. The same-width semantic
ABI example remains useful because ordinary type/layout validity does not
distinguish physical index from application ID. However, its wrong output must
be marked illustrative. The paper must remove or rewrite every claim that the
defective route was executed, reached launch, or returned the illustrative
rows. It may retain the current, replayed facts that CP002 mutation is detected,
the integrated projection mutation is rejected before native load, and the
correct route has separate existing correctness evidence, with each evidence
class named accurately.
