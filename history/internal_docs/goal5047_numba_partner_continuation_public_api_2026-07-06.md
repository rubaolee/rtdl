# Goal5047 - Numba PartnerContinuation Public API

Date: 2026-07-06

Status:

```text
implemented_numba_partner_continuation_public_api__pod_cuda_smoke_pending
```

## Purpose

Goal5047 formalizes Numba as the first public RTDL partner continuation over `DeviceColumnBuffer` inputs.

This is a system/API consolidation goal.  It is not a RayJoin app optimization and not a performance claim.

## Implementation

Modified files:

```text
src/rtdsl/numba_partner_api.py
src/rtdsl/__init__.py
tests/goal5047_numba_partner_continuation_public_api_test.py
```

New public symbols:

```text
NUMBA_PARTNER_CONTINUATION_CONTRACT_VERSION
NUMBA_PARTNER_CONTINUATION_API_MATURITY
NUMBA_PARTNER_CONTINUATION_CLAIM_BOUNDARY
NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS
NumbaPartnerContinuationPlan
NumbaPartnerContinuationResult
describe_numba_partner_continuation_contract
numba_partner_continuation
run_numba_partner_continuation
validate_numba_partner_continuation_contract
```

The public API wraps existing Numba continuation assets from:

```text
src/rtdsl/numba_partner_continuation.py
```

It does not duplicate kernels and does not create a new RayJoin-specific partner lane.

## Public Operation Set

The v2.14.4 public operation set is intentionally restricted to generic operations whose descriptors already reject app-specific semantics:

```text
label_count_and_flag_count_i64
adjacent_midpoint_candidates_i64x2_by_key
consecutive_dedupe_mask_f64x2
range_has_sorted_values_i64
uint32_equal_mask
pairwise_l2_sq_score_rows_2d
pairwise_l2_sq_block_nearest_rows_2d
sqrt_f64
```

Grouped reduce remains outside the public `device_group_by` surface per Goal5046.  Existing grouped/segmented kernels remain internal/partner assets until a public grouped-reduce contract and POD proof exist.

## Contract

`numba_partner_continuation(...)` requires:

- a `DeviceColumnBuffer` input;
- explicit logical-input to column-name bindings;
- optional scalar inputs;
- optional execution options.

Default behavior:

- host-materialized buffers fail closed;
- host fallback requires `allow_host_fallback=True`;
- missing input bindings fail closed;
- unsupported operations fail closed;
- Numba CUDA unavailable returns `skipped_cuda_unavailable` by default rather than pretending work ran.

Metadata records:

- stream-ordering from `DeviceColumnBuffer`;
- stream-synchronization status;
- device-residency metadata;
- whether host fallback was allowed/used;
- operation descriptor;
- output metadata after execution.

## Claim Boundary

All public metadata keeps these false:

```text
replaces_rt_traversal
raw_kernel_required
public_speedup_claim_authorized
true_zero_copy_claim_authorized
app_specific_semantics_allowed
```

Numba partner continuation is a post-RT continuation path over typed columns.  It does not replace RT traversal and does not authorize broad RT-core or whole-app speedup claims.

## Verification

Command:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal5047_numba_partner_continuation_public_api_test tests.goal5046_device_group_by_public_readiness_decision_test tests.goal5045_public_device_order_by_contract_test tests.goal5044_public_prepared_geometry_session_contract_test tests.goal5043_public_device_column_buffer_contract_test
```

Result:

```text
Could not find platform independent libraries <prefix>
...........................
----------------------------------------------------------------------
Ran 27 tests in 0.082s

OK
```

Leak/boundary scan:

```powershell
rg -n "rayjoin|RayJoin|output_chain|descriptor_pair|carrier|raw_kernel_required|replaces_rt_traversal|true_zero_copy|public_speedup|allow_host_fallback" src/rtdsl/numba_partner_api.py tests/goal5047_numba_partner_continuation_public_api_test.py
```

Allowed hits:

- `rayjoin_overlay_kernel` appears only as an unsupported-operation rejection test;
- claim-boundary keys appear with false values;
- `allow_host_fallback` appears as explicit opt-in behavior.

## What This Proves

- RTDL now has a public Numba partner continuation API.
- The API consumes `DeviceColumnBuffer`, not app-shaped dict rows.
- Host fallback cannot happen silently.
- CUDA-unavailable local behavior is explicit and non-authorizing.
- The API records stream/residency/claim-boundary metadata.
- Unsupported app-shaped operation names fail closed.

## What This Does Not Prove

- It does not prove a Numba CUDA POD execution for this new public wrapper.
- It does not prove public `device_group_by`.
- It does not prove performance improvement.
- It does not authorize true-zero-copy wording.
- It does not migrate RayJoin to the public API; that is Goal5049.

## Next

Request external review.  If accepted, proceed to Goal5048: a non-RayJoin genericity proof using `DeviceColumnBuffer`, `PreparedGeometrySession` where relevant, public `device_order_by`, and the new Numba partner continuation API.
