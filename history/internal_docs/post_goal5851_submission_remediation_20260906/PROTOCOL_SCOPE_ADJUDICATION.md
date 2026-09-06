# Goal5848 protocol-scope adjudication after Goal5851

Date: 2026-09-06

Status: `CLOSED_WITH_EVIDENCE__IMPLEMENTATION_DEFECT_NOT_REPAIRED`

Measured successor source M:
`d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree
`d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`.

This adjudication does not modify M, the original Goal5848 contract, any
authority, any raw worker, or any archive. It separates numerical validity,
runtime checks, literal protocol compliance, and admissible paper wording.

## 1. Binding decision

```text
machine_numerical_contract_passed = true
original_written_per_execution_receipt_requirement_fulfilled = false
wrong_output_observed_in_final_gpu_samples = false
public_prepared_a_over_direct_observation_retainable = true
implementation_entry_positive_performance_claim_allowed = false
```

The two successful transactions remain valid as limited observations of the
exact public prepared path and exact checks that actually ran. They do not
establish the original written requirement that every execution validate and
retain a complete physical receipt before output publication.

## 2. Source and evidence identities

| Item | SHA-256 or identity |
| --- | --- |
| Original Goal5848 contract | `e4f08161e1c146918368e562c3057895ed3054331fd3fad9f2c35088a5ab3403` |
| `src/rtdsl/v4_rtdlexe.py` at M | `99fdc5c0f4462fe153e9659ba5f2d541e9876be76e11cebbf46ede8fa8cc6a34` |
| `src/native/optix/rtdl_optix_v4_callback_poc.cpp` at M | `4e9c05bdc227c48ccc998b10ec382d84e041a8c268c1dff9ca04d987455045a7` |
| Formal worker at M | `353faec5a4dd46ad00c0979f2bb544eb278460d8b55fdf054127853a03ca11e4` |
| Formal contracts at M | `58eaa97abacb43fdb05884b02f72cc6dd2d5729851a70ff3890dc07c9a5dc942` |
| Ada authority/recount | `191e85ea19a2af2186cddf873d19483753197f258b5afddba06abd57cc0a66b7` |
| Ampere authority/recount | `35049de227c9c251314615039f07aaf6af71dd26bf24e8c6f5e1c74fb8ceadb3` |
| Cross-generation authority/recount | `99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692` |

`git diff d653fe4..HEAD -- src include experiments scripts tests` was empty at
R0. Current source references below therefore identify the measured M bytes.

## 3. Obligation-to-phase matrix

| Obligation | Established | Checked before ordinary successful return | Checked on deferred observation | Retained by each formal worker | Adjudication |
| --- | --- | --- | --- | --- | --- |
| Protocol roles, effects, resource contract and static executable identity | compile, admission, materialize and bind | Yes, for the admitted loaded image and prepared owner | Not applicable | Deployment identities and source pins are retained | Supported only as loaded-image identity, not per-execution disk reread or semantic proof by hashing |
| Native function return | native call boundary | Yes; nonzero return is raised before result construction | Not applicable | Formal successful workers imply zero native return | Supported |
| Compact device status | native status D2H precedes output D2H; Python reads the status scalar | Yes; nonzero status forces validation and raises | Successful detailed status mapping is lazy | The successful status value is represented indirectly; a separate diagnostic is retained | Supported as synchronous failure rejection, not as eager validation of all receipt fields |
| Bounded relation count/capacity relations | native control and Python constructor | Yes; malformed counts or overflow fail before public return | Full operation receipt is forced on the failure route | Public rows and one separate diagnostic are retained | Supported for the bounded route |
| Triangle scalar oracle when supplied | public fused replay | Yes; `expected_reduced_u64` mismatch raises before result return | Not applicable | Every formal timed result is checked again by worker output validator | Supported for the measured workload, not proof that every user supplies an oracle |
| Relation exact-row oracle when supplied | prepared relation execute | Yes; returned canonical rows are compared with expected rows | Not applicable | Every formal timed result is checked again by worker output validator | Supported for the measured workload |
| Per-timed-call output digest/oracle | formal `_sample` after each timed action | No, relative to public API return; yes before the experiment accepts that sample | Not applicable | The worker retains the expected digest and public output, not 128 distinct digest records | Supported as experiment validation, not public-return validation or per-call physical trace |
| Detailed 27-field fast operation receipt | native fills a per-call ctypes object | On a successful ordinary call, no | Yes, at first mapping observation; failures force observation | No complete receipt for each of 128 timed calls | Original written per-execution requirement not fulfilled |
| Launch/raygen/traversable physical audit | separate diagnostic execution | No for each ordinary timed call | Diagnostic receipt is eagerly consumed by worker | Exactly one separate diagnostic receipt per A worker | Supports one diagnostic per worker, not 128 timed-call traces |
| Output digest inside traversal receipt | separate diagnostic execution | No; ordinary result has `output_sha256=None` and `traversal_receipt=None` | Available in diagnostic receipt | One diagnostic digest per worker plus worker-level expected output digest | Not a per-timed-call traversal receipt |
| Monotonic execution identity | compact diagnostic schema has an execution-sequence slot; current full diagnostic schema retains a nonce | No | Diagnostic validation only | One diagnostic nonce per worker; no per-timed-call sequence series | Original monotonic per-execution evidence not established |

Primary source locations:

- Original obligations: `GOAL5848.md:267-289`.
- Receipt ABI: `src/rtdsl/v4_rtdlexe.py:3951-3980`.
- Detailed validator: `src/rtdsl/v4_rtdlexe.py:5005-5184`.
- Deferred validation: `src/rtdsl/v4_rtdlexe.py:5308-5487`.
- Triangle public replay: `src/rtdsl/v4_rtdlexe.py:6254-6295`.
- Formal per-call output check: `experiments/goal5848_strong_baseline/worker.py:168-186,268-273,476-484`.
- Formal diagnostic validation: `experiments/goal5848_strong_baseline/worker.py:482-502`.
- Archive accepts `latest_output_sha256=None` and one diagnostic:
  `experiments/goal5848_strong_baseline/contracts.py:627-653`.

## 4. The 27 fast-receipt fields

All fields below are populated in the native per-call object. On an ordinary
successful call, constructing the deferred objects does not run
`_validate_fast_operation_receipt`. The exact checks in the third column run
only when the mapping is observed. None of the 27-field objects is persisted
for every formal timed invocation.

| Field | Native establishment | Successful pre-return handling | Deferred validation | Per-timed-call archive |
| --- | --- | --- | --- | --- |
| `schema_version` | initialized to 2 | raw object retained | equals 2; structure size equals 128 | No |
| `optix_launch_count` | initialized to family launch count | not read | triangle=1, bounded=2 | No |
| `host_blocking_boundary_count` | incremented from status/output and setup sync boundaries | not read | equals computed success/failure boundary count | No |
| `control_d2h_bytes` | set from selected native control layout | status scalar itself is read, field is not | equals family/mode layout | No |
| `output_d2h_bytes` | set after successful output transfer | output value is read, field is not | equals expected output bytes on success, zero on failure | No |
| `status_before_output` | set to 1; native sequence performs status D2H before output D2H | sequencing occurs, field value not read | exact boolean domain and value 1 | No |
| `output_d2h_after_status_failure` | initialized/set to zero on failure | failure path forces receipt validation; success path does not | equals zero | No |
| `role_counters_materialized` | set by native mode | not read | equals exact family/monitor expectation | No |
| `prepared_input_reused` | set from selected reuse route; native validates reuse identity | reuse path executes, field is not read | equals expected reuse decision | No |
| `dynamic_device_upload_call_count` | counted by native | not read | checked against reuse and family expectations | No |
| `dynamic_accel_build_count` | counted by native | not read | checked against reuse and family expectations | No |
| `dynamic_explicit_sync_count` | counted by native | not read | checked against expected dynamic setup | No |
| `dynamic_blocking_upload_call_count` | counted by native | not read | checked for range and expected dynamic setup | No |
| `dynamic_device_upload_bytes` | counted by native | not read | zero for reuse, positive for required rebuild/upload | No |
| `dynamic_input_generation` | copied from prepared cache generation | not read | required positive; not a per-call execution sequence | No |
| `semantic_compaction_launch_count` | counted by native | not read | bounded=1, triangle=0 | No |
| `semantic_compaction_key_capacity` | copied from native capacity | bounded count relations checked separately; field not read | exact power-of-two capacity for bounded, zero for triangle | No |
| `semantic_compaction_scratch_bytes` | computed by native | not read | exact capacity-derived bytes for bounded, zero for triangle | No |
| `callback_status_kernel_launch_count` | counted by native | compact status is read; this counter is not | exact family/monitor count | No |
| `checked_product_kernel_launch_count` | counted by native | scalar is read; this counter is not | triangle mode expectation, zero for bounded | No |
| `compact_control_finalizer_kernel_launch_count` | counted by native | compact status is read; counter is not | exact family/monitor count | No |
| `total_auxiliary_cuda_kernel_launch_count` | counted by native | not read | equals exact sum expected for mode | No |
| `execution_parameter_h2d_bytes` | counted by native | execution occurs; field not read | equals selected ABI parameter bytes | No |
| `execution_parameter_h2d_copy_call_count` | counted by native | not read | exact family count | No |
| `stream_ordered_memset_call_count` | counted by native | not read | exact family/monitor count | No |
| `status_d2h_copy_call_count` | counted by native | status transfer occurs; field not read | equals one | No |
| `output_d2h_copy_call_count` | counted by native | output transfer occurs only after success; field not read | one on successful output, zero on failed/no-output route | No |

The important distinction is not whether the native object exists. It does.
The distinction is whether its detailed fields are validated before public
success and whether one validated object is retained for every measured call.
For success, both answers are no.

## 5. Native ordering and failure semantics

The source contains real status-before-output ordering:

- Triangle copies and synchronizes its status control at native lines
  `5438-5456`, returns without output on nonzero status at `5457-5460`, and only
  then copies the scalar at `5461-5470`.
- Bounded relation copies and synchronizes control at native lines
  `6818-6844`, returns without rows on nonzero status at `6845-6847`, and only
  then begins row transfer at `6860-6867`.
- Python raises nonzero native return before result construction and the
  deferred status constructor forces detailed validation on compact failure.

Therefore this adjudication does not claim that a wrong GPU value escaped in
the retained transactions. It also does not reinterpret the native ordering as
proof that the original requirement to validate the compact execution receipt
before publication was fulfilled.

## 6. Formal evidence recount for this issue

Read-only inspection of all final A-arm worker JSON produced:

```text
Ada A workers=16; Ampere A workers=16
each worker steady samples=128
all 32 latest_output_sha256 values=null
all 32 workers contain exactly the worker-level separate diagnostic field
all 32 worker-level output_sha256 values are present
task split per generation=8 triangle + 8 relation
```

This means 4,096 timed A samples exist across both generations, but only 32
separate post-loop diagnostic executions are represented by detailed traversal
receipts. The diagnostic execution cannot be relabeled as any timed execution.

## 7. Failure and lifecycle limitations retained in the ledger

The provider bind cleanup at `src/rtdsl/v4_rtdlexe.py:3078-3092` can let a
secondary release/close exception replace the primary exception and clear
retry ownership. No public output is produced on that path and it did not occur
in the retained successful workers. The defect remains unrepaired; universal
cleanup/root-cause preservation is removed from the paper claim set.

Python registers an `os.register_at_fork` child hook at
`src/rtdsl/v4_rtdlexe.py:239-260`, and prepared owners compare cached PID at
`5680-5684` and `6184-6188`. This supports the documented Python-managed fork
lifecycle. It does not establish rejection for native `fork()` that bypasses
Python's hook. Inherited GPU owners after unsupported native fork are outside
the supported contract.

## 8. Allowed and forbidden wording

Allowed candidate wording:

> We evaluate the exact prepared public path with synchronous native and
> compact-status failure rejection and per-call experiment output-oracle
> checks. Detailed operation-receipt validation is deferred, and each formal
> worker retains one separate diagnostic receipt rather than a complete
> physical trace for every timed invocation. The measurements therefore do not
> establish the original preregistered per-execution receipt requirement.

Forbidden wording includes:

- every original Goal5848 safety invariant passed unchanged;
- every timed execution had a complete physical receipt validated before
  output publication;
- the mock corruption probe proves a real GPU corruption occurred;
- all process forks or all provider double-faults fail closed while preserving
  original cause and retry ownership;
- the limited performance numbers are intrinsic language speedup, universal
  parity, or confirmatory unseen-workload evidence.

## 9. Closure

R1 scope adjudication is closed because the written obligation, implementation
phase, retained evidence, deviation and admissible wording are now explicit.
The underlying detailed-receipt, provider double-fault and native-fork limits
are not repaired. Any paper claim requiring the stronger properties must be
removed rather than marked fixed.
