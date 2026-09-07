# Protocol Witness and Fact Derivation

Date checked: 2026-09-07 America/New_York. This P-quadruple-prime authoring pass
preserves the earlier audit and adds the three source-traced result-route
witnesses required by the lead contribution directive.

Status: `N2_PQUADRUPLEPRIME_RESULT_ROUTE_REMEDIATED__AUTHOR_SCOPE__INDEPENDENT_REVIEW_PENDING`.

This report traces one RTDL protocol seam from requirement to representation,
target-side fact, admission point, execution guard, and public result. It is a
read-only audit of the measured implementation M and the current source. It
does not add a test, rerun a GPU experiment, prove a general soundness theorem,
or authorize a manuscript claim.

## 1. Identity and scope

| Item | Identity |
| --- | --- |
| Measured implementation M | commit `d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Read-only result-route audit starting HEAD | commit `b608f9aa5e4e04d083d8a2963d552e00287b47cd`, tree `bb8927c4d34eeb94a5656ce8da5b1df997329797` |
| Protocol implementation difference from M | None in the files hashed in Section 8 |
| Evidence type added here | Source trace and local replay of already committed unit checks only |
| GPU execution in this audit | None |

## 1A. Three result-route witnesses

These witnesses establish concrete compiler relations already present in the
measured source. They do not add an executable path, extend the experiment
population, or prove a general semantics.

### W1: role legality is weaker than fixed-route result legality

`src/rtdsl/v4_callback_ir.py:572-580` permits an any-hit role to return
`ACCEPT_CONTINUE`, `IGNORE`, or `TERMINATE`. The complete bounded-relation
target applies a stricter check at `src/rtdsl/v4_bounded_relation.py:241-263`:
it recursively collects all return effects and requires the set to be exactly
`{ACCEPT_CONTINUE}`, otherwise rejecting with `any_hit_effect`.

The result contract explains the extra restriction. A route promising the
current complete relation has no defined early-termination or filtering output
semantics. This proves the existence and location of a result-related family
rule, not that all complete-enumeration algorithms must reject `IGNORE`, nor
that this audit executed a deliberately terminating GPU program.

### W2: logical acceptance is lowered to physical intersection rejection

For triangle all-hit counting, the generic wrapper at
`src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py:418-430` updates the
payload for logical `ACCEPT_CONTINUE` and then emits
`optixIgnoreIntersection()`. The exact-standard specialization at the same file
around lines 486-534 performs the corresponding checked count/reduction action
and also ignores the physical intersection. Native geometry setup at
`src/native/optix/rtdl_optix_v4_callback_poc.cpp:1921` uses
`OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL`.

Physical acceptance would reduce the accepted traversal interval; physical
ignore preserves later events after the logical contribution has been recorded.
Payload-before-ignore and single-delivery controls are established OptiX
techniques. RTDL's source-traced implementation contribution is the combination
chosen by the trusted lowerer for this fixed result route, together with its
overflow/status checks. It is not the invention of all-hit traversal or an
independent proof of completeness.

### W3: callback semantics, not ABI shape alone, guards specialization

`tests/goal5759_v4_triangle_reduction_target_test.py:72-102` changes the
standard callback update from `payload.count + 1` to `payload.count + 2`. The
modified callback remains front-end legal and preserves role/ABI shape, but its
canonical IR identity changes. Wrapper generation consequently does not select
the fixed standard-count intrinsic and uses the general leaf path.

On 2026-09-07, the existing W3 test and three existing bounded-relation checks
were replayed with the frozen Python 3.12 environment: 4/4 passed in 0.017 s.
The run exercised parse, verification, contract/ABI construction, and wrapper
generation; no GPU was used. This is evidence for one recognizer boundary, not
GPU equivalence, a semantic-preservation theorem, or a result over arbitrary
specializations.

| Witness | Source or existing check | Evidence level | Explicit nonclaim |
| --- | --- | --- | --- |
| W1 | Role set plus bounded-relation family verifier | Source trace; three existing CPU contract checks replayed | No deliberately invalid GPU route and no general enumeration theorem |
| W2 | Generic and specialized triangle wrapper plus native GAS setting | Source trace; historical GPU results belong to unchanged M/F2 paths | No new GPU sample and no claim to invent OptiX all-hit mechanisms |
| W3 | Exact-standard count test with `+1` changed to `+2` | Existing source-to-wrapper test replay | No GPU equivalence or general optimization theorem |

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
| `PC-02_ATTRIBUTE_OWNER` | Family-fixed declaration `attr0=verified_intersection_attribute0_item_id` | Reads `CompiledBoundedRelationContract.row_sources[1]`, copied from trusted emission schema | `CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH` | Same pre-materialization rejection; prepare rechecks the stored verdict before per-route preparation/launch. Exact app-free native runtime initialization may already be in progress. | Schema/provider declaration gives the intended semantic name; lowerer honors contract | CP002 mutation sensitivity passes at pure and integrated gates; with overlap disabled, the integrated mutation is rejected before the native-library loader; correct mocked output is `(100,10),(101,20)` | Automatic inference of app meaning; an executed `(100,0),(101,1)` defect; independent target trust root |
| `PC-03_PHYSICAL` | `ProtocolPhysicalPlan` provides geometry family, output contract, reducer algebra, template ID, plus program protocol digest | `_compiled_protocol_facts` reads physical authority schema and compiled relation/reducer contract | `CP003_PHYSICAL_BINDING_MISMATCH`, grouped with family/task identity | `PL036` before object return | Trusted physical authority and contract describe the actual specialized lowerer | Single-field mutation and integrated gate pass | Proof that every topology-specific wrapper implements arbitrary plan semantics |
| `PC-04_CONTINUATION` | Fixed `REQUIRE_COMPLETE_BEFORE_CONSUME` | `_compiled_protocol_facts` checks runtime status codes and fail-closed relation/reducer contract | `CP004_CONTINUATION_STATUS_MISMATCH` | `PL036` before route acceptance; during execute, nonzero native/compact status blocks a normal application result | Native wrapper reports status faithfully and host reads the applicable status object | Mutation tests pass; execute source shows status checks before result construction | A general progress theorem; recovery after failure; correctness of app oracle |
| `PC-05_EXEC_ID` | `checked_executable_sha256` uses the just-produced executable digest | Projection receives that executable digest as `actual_executable_sha256` | `CP005_EXECUTABLE_IDENTITY_MISMATCH` | `PL036` before materialized object return | Digest function and compiler object identity are trusted | Identity mutation tests pass | Semantic correctness of equal bytes; independent derivation at the CP005 comparison itself |

### 4.1 Why PC-05 is useful but limited, by public interface

At the contract-comparison point, declaration and projection both receive the
same `executable_sha256` argument. CP005 is therefore primarily a substitution
or representation-drift guard; it is not independent evidence that the bytes
implement the source semantics.

The broader `ProtocolExecutableIdentity` is more informative. It binds the
program identity, target, physical schema, compiled contract, ABI, generated
executable, composed PTX, and native library digests
(`v4_callback_lifecycle.py:625-676`). The exact library is hashed before and
after `ctypes.CDLL` load (`1180-1197`). That statement applies to the
materialized-program interface: it checks returned PTX and native identities,
device status, output digest, and traversal receipt before returning a
`ProtocolExecutionResult` (`1572-1701`).

The measured AOT prepared interface is different. Its ordinary fast path in
`v4_rtdlexe.py:6254-6290,6535-6582` returns `RTDLExecutionResult` after its
owner/process/thread/reentrancy checks, native and compact-status handling, and
any supplied expected-output check. The ordinary fast result may have neither
an output digest nor a detailed traversal receipt. In the Goal5848 worker, the
returned value and digest oracle runs after the prepared-call timer but inside
the first-result endpoint (`worker.py:453-466`); steady `_sample` likewise times
the action before validating it. One separate post-loop diagnostic execution
per Arm-A worker supplies a detailed receipt (`476-502`). Consequently, the
formal population retained 4,096 timed Arm-A calls but only 32 separately
executed detailed receipts, not one receipt for every timed call. Equal hashes
still establish identity coherence, not semantic correctness.

## 5. Admission, initialization, and publication timeline

| Boundary | Actual check | Consequence |
| --- | --- | --- |
| IR verification | Role legality and exact effect fields/types in `v4_callback_ir.py:1247-1292` | Invalid callback IR is not verified. |
| ABI compilation | Re-verifies the callback/physical authority and flattens role inputs, effect variants, status, tags, and symbols in `v4_callback_abi.py:344-435` | ABI cannot be minted from an arbitrary unverified dataclass. |
| App-free runtime initialization | `begin_native_initialization` can start exact process-wide native loading/warming before route construction, and the formal worker starts provider initialization before `load_rtdlexe` (`v4_callback_lifecycle.py:477-512,1203-1285`; `worker.py:291-323`) | Initialization may overlap AOT artifact verification. It exposes no route handle and does not admit a route. |
| Target materialization/admission | Builds specialized authority/contract/ABI/executable, forms protocol declaration/projection, and compares five seams in `v4_protocol_contract.py:269-329`; the decision occurs in materialization before object return | A rejection raises `PL036` before `MaterializedProtocolProgram` is returned. With overlap disabled, the integrated mutation tests reject before `_load_exact_native_library` is called. |
| Per-route preparation | Joins or uses the exact warmed runtime, rechecks the accepted verdict, and binds the admitted route to its exact native/executable identities | App-free initialization alone does not authorize route preparation or launch. |
| Materialized-program execution | Checks execution identity, native status, output digest, and traversal receipt | Only this interface returns `ProtocolExecutionResult` with that complete pre-return validation. |
| Measured AOT prepared execution | Checks owner/process/thread/reentrancy boundaries, native/compact failures, and supplied expected output, then returns `RTDLExecutionResult` | Its ordinary fast result need not carry a digest or detailed receipt; do not generalize the materialized-program interface to this path. |
| Worker oracle | After public return, validates output and digest. For first-result measurements it is after the prepared timer but inside the endpoint. | It is experiment logic, not a compiler guarantee or part of the prepared steady timer. |
| Separate diagnostic | Executes once after the timed loop for each Arm-A worker and retains a detailed traversal receipt | It does not provide one detailed receipt for each of the preceding 128 timed calls. |

The phrase "before launch" is safe only when tied to route admission and
per-route preparation. A phrase such as "before native load" is safe only for
the tested mutation configuration with initialization overlap disabled and
must name the native-library loader. Neither phrase may imply that every
semantic defect is rejected or that the worker oracle is part of the compiler.

## 6. General lowering and the two measured specializations

The general callback path below is actual source/code generation, not
pseudocode. It is visible in the triangle diagnostic entries; it is not the hot
entry used for the reported prepared triangle measurements. It also does not
imply that every topology accepts every `EffectKind`.

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
5. A generic triangle diagnostic wrapper invokes that leaf. At
   `v4_triangle_reduction_optix_wrapper_codegen.py:386-430`, an admitted
   `ACCEPT_CONTINUE` tag updates the u64 payload and optional event; an admitted
   `IGNORE` tag follows its configured payload behavior; any unexpected tag
   records first error and calls `optixTerminateRay()`. The accepted all-hit
   path writes the payload via `optixSetPayload_*` and calls
   `optixIgnoreIntersection()` so traversal continues without shrinking
   `tmax`.

Thus the general route is typed effect -> deterministic ABI/tag -> generated
Numba leaf -> trusted wrapper check -> hardware action. The evaluated standard
routes partially evaluate that chain under exact callback-IR guards:

| Path | Admission condition and actual execution | Retained checks | Replaced checks | Trust premise and source |
| --- | --- | --- | --- | --- |
| General callback / triangle diagnostic entries | Verified role/effect IR is flattened into the ABI; generated Numba leaves emit status/tags/fields; diagnostic wrapper entries interpret those tags before payload, ignore, or terminate operations. | IR, schema/ABI, executable identity, leaf status/effect validation, runtime failure checks | None in this path | Numba leaf and topology wrapper are trusted (`v4_callback_numba_codegen.py:370-408`; triangle wrapper `386-485`). These entries remain generated but are renamed diagnostic entries when the count specialization is selected. |
| Measured triangle standard route | Exact callback IR SHA-256 plus checked-U64 reducer guard selects direct count/reduction raygen and any-hit entries. The hot any-hit increments payload directly and continues traversal; raygen reduces with checked overflow (`v4_triangle_reduction_optix_wrapper_codegen.py:129-141,463-534`). | Static callback/schema/ABI and executable-identity admission; native and compact failure handling; checked-U64 overflow; supplied expected-output check | Per-hit Numba leaf call and per-leaf status/effect-tag interpretation at the specialized roles | Exact standard IR and reducer guard, wrapper generator, and direct entries are TCB. The digest selects a known specialization; it is not a semantic proof. The measured runtime enters the replay/fast paths at `v4_rtdlexe.py:6254-6290,6304-6313,6412-6429`. |
| Measured bounded-relation standard route | Exact standard relation callback is required, then intersection, counting/row emission, and continuation are fused in trusted OptiX entries (`v4_bounded_relation_optix_wrapper_codegen.py:40-58,194-198,293-375,416-427`). Generated leaf identities remain bound but are not called (`linked_role_symbols=False`). | Static schema/ABI/contract and identity admission; native status; row capacity and overflow; canonical output and supplied expected rows where configured | Per-role Numba leaf calls and per-role status/effect-tag interpretation in the fused roles | Exact-standard-IR recognizer, fused wrapper, row-orientation logic, and native/runtime connection are TCB. This does not establish arbitrary-callback lowering. |

The measured prepared latencies therefore measure the two exact-standard-route
specializations, not the cost of executing every role through the general
Numba-leaf ABI. Trusted topology-specific wrappers, not arbitrary callback code,
perform hardware control. The canonical plan is not executable, RTDL does not
synthesize arbitrary wrappers from an unconstrained protocol graph, and these
specializations are part of the TCB.

## 7. Evidence classification

| Evidence class | Retained/current evidence | What it establishes | What it does not establish |
| --- | --- | --- | --- |
| Declaration/projection field mutation | `tests/goal5797_protocol_contract_test.py:61-118`; six selected checks replayed at current HEAD | Each of five comparison mechanisms is live; CP002 is sensitive to the semantic-owner name mismatch; ablation of that comparison changes this synthetic decision to accept | A real source program passed through the full public compiler and was rejected |
| Integrated projection mutation | `tests/goal5795_v4_public_lifecycle_test.py:268-336`; selected test replayed at current HEAD with native-initialization overlap disabled | Corrupting each target projection at materialization makes the integrated gate reject before `_load_exact_native_library` is called in that configuration | A prohibition on exact app-free runtime warmup before admission; independent target implementation or native/GPU execution of the defect |
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
| `src/rtdsl/v4_rtdlexe.py` | `99fdc5c0f4462fe153e9659ba5f2d541e9876be76e11cebbf46ede8fa8cc6a34` |
| `experiments/goal5848_strong_baseline/worker.py` | `353faec5a4dd46ad00c0979f2bb544eb278460d8b55fdf054127853a03ca11e4` |
| `tests/goal5759_v4_triangle_reduction_target_test.py` | `3d44b0285afba026333e81abd4f262232db075b5b8150871c9fc14bab767101f` |
| `tests/goal5760_v4_bounded_relation_test.py` | `faa1550b98990c771c20b516b808258edc96b5d0de49c9caca6bf5a9dd4b99fd` |
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
| Native provider status and receipt production | Supports fail-closed status handling and detailed evidence on the paths that request it | Native/provider bugs or collusion are outside the finite checker proof; an ordinary measured fast result need not include a detailed receipt. |
| Worker oracle | Validates experiment outputs | It runs after prepared return; it is inside the first-result endpoint but after the prepared timer, and is not a compiler guarantee for all calls. |

The strongest defensible statement is therefore: for the implemented bounded
families, RTDL represents five named route seams, derives declaration and
target projections through distinct compiler paths, rejects mismatches at the
materialization/prepare boundary, and carries the accepted identity into
per-route preparation and the checks implemented by each public interface. The
materialized-program path validates identity/status/output/receipt before its
return; the measured AOT prepared path has the narrower checks and evidence
sequence stated in Sections 4.1 and 5. RTDL does not independently infer
application semantics, synthesize arbitrary topology lowerers, prove arbitrary
semantic equivalence, or supply an executed wrong-output witness for the
illustrative example.

## 10. N2 conclusion and mandatory paper corrections

N2 establishes a real but bounded compiler mechanism. W1 shows a fixed output
obligation imposing a stricter effect rule than role legality. W2 shows a
trusted lowerer interpreting logical acceptance through a different physical
intersection action. W3 shows one same-shape source change invalidating a fixed
intrinsic. Together they support a concrete result-route contract argument,
while leaving schemas, recognizers, lowerers, runtime, and hardware in the TCB.

The same-width semantic ABI example remains useful because ordinary type/layout
validity does not distinguish physical index from application ID. Its wrong
output must remain illustrative. The paper may retain the replayed facts that
CP002 mutation is detected, the integrated projection mutation is rejected
before the native-library loader when initialization overlap is disabled, and
the correct route has separate existing correctness evidence, with each
evidence class named accurately. It must identify the measured exact-IR
specializations and distinguish the materialized-program result path, measured
AOT prepared result, worker oracle, and separate diagnostic execution. No W1,
W2, or W3 source trace may be described as a new GPU experiment or a general
semantic theorem.
