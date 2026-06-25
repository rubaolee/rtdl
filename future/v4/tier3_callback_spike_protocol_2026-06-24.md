# V4 `goal4622` Tier-3 Callback Spike Protocol

Date: 2026-06-24
Status: `tier3_protocol_goal4622_spike_only_not_support`

This protocol defines the only callback shape that may be tested as a future
Tier-3 spike. It does not authorize Tier-3 support, raw OptiX callbacks, V4
release wording, or measured-catalog promotion.

## Purpose

Tier 2 covers recognized fused operators. Tier 3 exists only for user logic that
cannot be expressed as a recognized Tier-2 operator but still has the shape of a
small scalar reduce.

The protocol is intentionally strict. It is designed to falsify the idea before
implementation expands. Passing this protocol would authorize only a later
reviewed implementation spike, not a public V4.0 feature. Tier-3 callbacks
must not be documented as supported unless a later release decision explicitly
promotes them after all gates pass.

## Accepted Callback Shape

The only accepted shape is:

`scalar per-hit reduce only`

A callback must satisfy all of these constraints:

- Numba CUDA device function only.
- Pure function from fixed scalar inputs to fixed scalar state.
- Signature shape:
  `new_state = f(hit_t, primitive_id, payload0..payloadN, old_state0..old_stateM)`.
- Scalar argument types only:
  `bool`, `int32`, `uint32`, `int64`, `uint64`, `float32`, `float64`.
- Return type is one scalar or one fixed tuple of at most four scalar values.
- No writes except to the RTDL-owned fixed output state selected by the
  traversal shell.
- No dependence on Python objects, host memory, dynamic dispatch, or runtime
  reflection.
- Determinism requirement:
  - any-hit unordered traversal reducers must be associative and commutative, or
    must declare that their result is order-insensitive;
  - closest-hit/single-event callbacks may be order-sensitive because there is
    one selected event.

Examples that match the accepted shape:

- weighted sum accumulator
- min/max score update
- thresholded scalar flag
- bounded fixed-state argmin

## Rejected Callback Shapes

The spike must reject these shapes before compilation:

- shared mutation
- global memory mutation outside the fixed RTDL-owned output state
- atomics used as user-visible semantics
- dynamic allocation
- variable-length output
- append/list/emit-row behavior
- Python object access
- arrays as mutable callback outputs
- recursion
- spawned action logic
- device synchronization
- cooperative groups
- texture/surface writes
- random-number generation
- exceptions
- `printf` as semantics
- direct OptiX API calls from the user callback
- raw OptiX callbacks as the public API
- application-identity kernels such as DBSCAN, Barnes-Hut, RayJoin, or
  collision-response kernels

Rejected callbacks must return planner status:

- `rejected_action_shaped_callback_deferred`
- `rejected_by_goal4622_action_shape_boundary`

## Pinned Toolchain Assumptions

A future implementation spike must record and pin the complete toolchain before
running any performance or support claim:

- Python executable and version.
- Numba package version and CUDA target version.
- CUDA Toolkit / NVVM path and version.
- PTX ISA version emitted by Numba.
- NVIDIA driver version.
- GPU model and compute capability.
- OptiX ABI version.
- OptiX include/library path.
- C++ compiler used to build the OptiX wrapper shell.

The current V4 measured surface scope is no broader than:

- GPU family: RTX A5000 / Ampere
- driver evidence: `570.195.03`
- maximum validated OptiX ABI for measured surfaces: `8.0`

A Tier-3 spike may not inherit broader scope from the host machine. If the
toolchain differs, the evidence must say so and the result is toolchain-local.

## Required Spike Stages

The spike must run in this order. A failure at any stage stops the spike.

### Stage 0: Planner Boundary

Required result:

- scalar reduce request returns
  `tier3_spike_only_not_v4_0_release_surface`
- action-shaped request returns
  `rejected_action_shaped_callback_deferred`
- no API surface is exposed
- all release/support/callback/raw OptiX authorization flags are false

### Stage 1: Numba PTX Generation

Required result:

- at least 20 compile attempts across at least 4 accepted scalar callback
  variants
- compile reliability floor: `>= 95%`
- every successful PTX artifact records the emitted PTX ISA/version header
- failed compiles are classified by stage and error type

Current evidence only proves a narrower fact: one scalar device callback can
generate PTX in a particular environment.

### Stage 2: OptiX Wrapper / Direct-Callable ABI

Required result:

- the callback PTX is linked through a real OptiX traversal wrapper or direct
  callable ABI, not passed as a bare helper module
- module creation succeeds
- program group creation succeeds
- pipeline creation succeeds
- launch succeeds
- reliability floor across the same 20 attempts: `>= 95%`

Current evidence explicitly does not pass this stage: bare Numba helper PTX
failed direct `optixModuleCreate` because it had no OptiX semantic entry
functions.

### Stage 3: Correctness Parity

Required result:

- correctness parity: `100%`
- at least three deterministic datasets:
  - dense hits
  - sparse hits
  - no-hit / empty reduction
- CPU or existing Tier-2 reference must be named
- tolerance must be fixed before execution:
  - integer/flag outputs: exact
  - floating outputs: `rtol <= 1e-6` and `atol <= 1e-9`

### Stage 4: Overhead Ceiling

Required result:

- compare against a matching hand-written Tier-2 fused operator or wrapper
  baseline for the same traversal shape
- run at least two sizes:
  - `32768`
  - `131072`
- warmup count: `>= 2`
- repeat count: `>= 10`
- overhead ceiling: median callback route time `<= 1.50x` the matching
  hand-written fused route at every tested size
- hard kill: no tested size may exceed `2.00x`
- all timing windows must exclude one-time compilation and include traversal,
  callable dispatch, and output write

### Stage 5: Review Gate

Required result:

- external review confirms the result is still spike evidence only
- no public Tier-3 support wording
- no raw OptiX callback support wording
- no V4 release wording
- no broad speedup wording

## Kill Conditions

The spike must stop and remain V4.x/deferred if any condition is true:

- compile reliability is `< 95%`
- wrapper/direct-callable reliability is `< 95%`
- any correctness parity case fails
- median overhead is `> 1.50x` at any required size
- any tested size exceeds `2.00x`
- the implementation requires raw OptiX callbacks as the user-facing API
- the implementation requires app-identity native kernels
- the implementation requires C ABI / non-Python-host embedding work
- the implementation requires mutable variable-length outputs

## Planner Contract

The V4 planner may expose only the following Tier-3 statuses:

- scalar reduce candidate:
  `tier3_spike_only_not_v4_0_release_surface`
- protocol status:
  `tier3_protocol_goal4622_spike_only_not_support`
- action-shaped rejection:
  `rejected_by_goal4622_action_shape_boundary`

The planner must not return an API surface for Tier-3 requests.

## Relationship To Existing Evidence

Existing evidence remains narrow:

- `future/v4/tier3_numba_ptx_spike.md` proves only Numba PTX generation scope.
- `future/v4/tier3_optix_module_link_spike.md` records that bare PTX direct
  module creation is blocked.

This protocol defines the next honest experiment. It does not reinterpret prior
evidence as support.

## Non-Authorization

This protocol does not authorize:

- V4 release
- V4 release-candidate status
- measured-catalog promotion
- Tier-3 callback support
- raw OptiX callback support
- public true-zero-copy wording
- broad V4 speedup claims
- whole-application speedup claims
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels
