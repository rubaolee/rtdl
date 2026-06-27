# V4 Goal4701 Specialized Tier-3 Support Candidate

Status: support-candidate packet, not public support

- validation: `passed`
- candidate label: `specialized_numba_scalar_callback_support_candidate`
- next goal: `Goal4702 specialized Tier-3 reliability matrix protocol`

## Candidate Scope

module-specialized Numba C-ABI scalar device callback called as a direct device function from an RTDL-generated OptiX hit-program route

## Evidence Chain

- Goal4689 minimal launch correctness for scalar callback
- Goal4691 SBT direct-callable overhead measured yellow at 1.6705538933080346x
- Goal4692 pivot away from SBT direct-callable support
- Goal4693 specialized hit-program callback correctness
- Goal4695 specialized hit-program callback overhead passed at 1.0355240926982583x
- Goal4696 productization decision for constrained specialized candidate
- Goal4697 API contract and negative validation scaffold
- Goal4698 compile/cache/error-reporting scaffold
- Goal4699 app-route validation protocol frozen
- Goal4700 weighted-sum app-route POD gate passed against Tier-2 denominator

## Satisfied Gates

- single scalar callback PTX generation
- OptiX module composition and launch correctness
- specialized hit-program overhead under 1.50x focused gate
- one weighted-sum app-route parity/performance gate passed
- fail-closed rejection for arbitrary Python/action/external-memory/dynamic-SBT shapes
- public support flags remain false

## Missing Before Public Support

- external 3-AI review of Goals4696-4700
- 20 compile/link/launch attempts across at least 4 accepted scalar callback variants
- dense/sparse/no-hit correctness datasets for the candidate route
- cache reuse and error-reporting behavior tested under repeated compiles
- user-facing docs wording reviewed and bounded
- final release/support authorization gate

## Boundary

This packet does not authorize public Tier-3 support, arbitrary callback support, raw OptiX callbacks, broad speedup claims, whole-app speedup claims, or V4 release wording.
