---

## Verdict

**`accept_goal4622_complete_protocol_only_not_support`**

---

## Findings

### 1. Protocol document is well-formed and falsifiable

`future/v4/tier3_callback_spike_protocol_2026-06-24.md` delivers what the goal claims:

- **Accepted shape** is precisely scoped: `scalar per-hit reduce only`, Numba CUDA device function only, fixed scalar in → fixed scalar state, return type capped at one scalar or a fixed tuple of at most 4 scalars.
- **Rejected shapes** are enumerated explicitly (16+ categories: shared mutation, dynamic allocation, variable-length output, recursion, spawned action logic, direct OptiX API calls, raw OptiX callbacks as public API, app-identity kernels, cooperative groups, device sync, texture/surface writes, etc.).
- **Numeric gates** are concrete and falsifiable before implementation runs: compile reliability ≥95% across ≥20 attempts and ≥4 callback variants, OptiX wrapper/direct-callable link reliability ≥95%, correctness parity 100% on ≥3 datasets, median callback overhead ≤1.50x at each required size, hard kill at 2.00x.
- **Stage ordering is sequential and stopping** (Stage 0 → 5); failure at any stage halts the spike.
- **Honest about current state**: the protocol explicitly states Stage 2 is not passed — "bare Numba helper PTX failed direct `optixModuleCreate` because it had no OptiX semantic entry functions." This is not hidden or reinterpreted as Stage 2 passing.

### 2. Planner implementation correctly enforces the boundary

`src/rtdsl/v4_operator_catalog.py`:

- Constants are correct: `V4_TIER3_CALLBACK_SPIKE_PROTOCOL_STATUS = "tier3_protocol_goal4622_spike_only_not_support"`, `V4_TIER3_ACTION_CALLBACK_REJECTED_STATUS = "rejected_by_goal4622_action_shape_boundary"`, `V4_TIER3_CALLBACK_SPIKE_PROTOCOL_DOC` pointing to the correct file (line 9–11).
- `V4_SCALAR_TIER3_CANDIDATE_CONTINUATIONS` is a fixed set (`custom_scalar_reduce`, `custom_score`, `custom_threshold`, `custom_minmax`), so anything outside it falls through to `unsupported_no_fused_surface` — this is correctly conservative.
- Action-shaped check (`mutates_shared_state or dynamic_allocation or variable_length_output`) fires before the numba device function check, so no action-shaped request can accidentally reach the spike path.
- Scalar callback path: `api_surface=None`, `tier3_spike_authorized=True`, all 10 claim flags (`release_claim_authorized`, `tier3_callback_claim_authorized`, `raw_optix_callback_claim_authorized`, etc.) default to `False` (line 162–172 dataclass defaults). No claim flag is explicitly set to `True` for this path.
- Action callback path: `api_surface=None`, `tier3_spike_authorized` defaults to `False`, all claim flags `False`. The rejection status and protocol doc are both set correctly.

### 3. Tests verify the boundary mechanically

`tests/v4_tier3_callback_spike_protocol_test.py` — 5 tests:

- Protocol document is asserted for accepted shape wording, numeric gate values, all major rejected shape categories, and all non-authorization phrases.
- Planner for scalar callback: asserts exact status, exact protocol status, exact protocol doc, `api_surface is None`, `tier3_spike_authorized is True`, `tier3_callback_claim_authorized is False`, `raw_optix_callback_claim_authorized is False`, `release_claim_authorized is False`.
- Planner for action callback: asserts rejection status, `rejected_by_goal4622_action_shape_boundary` protocol status, correct protocol doc, `api_surface is None`, `tier3_spike_authorized is False`, `app_specific_native_kernel_authorized is False`.
- These are concrete, not smoke tests.

### 4. Gate integration and evidence

- `scripts/v4_catalog_regression_gate.py` includes both `operator_callback_planning_scalar_callback` and `operator_callback_planning_complex_callback` as gated cases (lines 135–140, 199–210).
- Gate checks: scalar must have `tier3_spike_only_not_v4_0_release_surface`, no api_surface, `tier3_spike_authorized=True`. Complex must have `rejected_action_shaped_callback_deferred`, no api_surface.
- Local dry-run evidence: status=passed, `release_authorized: False`, both cases pass.
- POD dry-run evidence: same result, both cases correctly classified.
- Test suite: 35 tests pass on Windows (including 5 new protocol tests), 27 on POD Linux — consistent with the expected platform delta.

### 5. Cross-doc consistency

README, `tier2_operator_catalog.md`, `tier3_numba_ptx_spike.md`, and `tier3_optix_module_link_spike.md` all reference the protocol file path. `callback_and_operator_planning.md` quotes the numeric gates accurately, names the correct protocol doc, and has an explicit non-claims section. No cross-doc inconsistency found.

---

## Non-Authorization Explicitly Confirmed

The following are **not** authorized by this goal or this review:

| Item | Status |
|---|---|
| V4 release | **NOT authorized** |
| V4 release-candidate status | **NOT authorized** |
| Tier-3 callback support | **NOT authorized** |
| Raw OptiX callback support | **NOT authorized** |
| True-zero-copy public claims | **NOT authorized** |
| Broad V4 speedup claims | **NOT authorized** |
| Whole-application speedup claims | **NOT authorized** |
| CuPy performance claims | **NOT authorized** |
| C ABI / embedding / non-Python-host | **NOT authorized** |
| App-specific native kernels | **NOT authorized** |
| Measured-catalog promotion of any Tier-3 operator | **NOT authorized** |

---

## Minor Observations (No Blockers)

- The planner only checks 3 action flags (`mutates_shared_state`, `dynamic_allocation`, `variable_length_output`). Other protocol-rejected shapes (recursion, device sync, cooperative groups, etc.) are not planner parameters. This is fine for a boundary tool — the protocol stage gate handles those at spike time, not at planning time.
- The `V4_SCALAR_TIER3_CANDIDATE_CONTINUATIONS` set is small and fixed. A `custom_scalar_reduce`-shaped callback with an unrecognized `callback_shape` string (e.g., `custom_custom_weighted_score`) routes to `unsupported_no_fused_surface` rather than the spike path. This is conservative and correct for a protocol goal.
- Stage 2 failure (bare PTX rejected by `optixModuleCreate`) is correctly surfaced in the protocol doc and planning doc. The goal does not attempt to hide or paper over this gap.

---

**Summary:** Goal4622 is complete as a protocol/boundary goal. The falsifiable gates are written and gated before implementation, the planner correctly separates spike-authorized scalar reduce from rejected action-shaped callbacks, no forbidden claims appear in any of the changed files, and the evidence is green on both local and POD. The goal does not implement or authorize Tier-3 callback support in any form.
