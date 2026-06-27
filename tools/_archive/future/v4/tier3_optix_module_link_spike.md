# V4 Tier-3 OptiX Module-Link Spike

Status: blocked spike evidence, not V4.0 support and not a release announcement

This spike tests the next step after Numba PTX generation:

> Can the scalar Numba device callback PTX be accepted directly by
> `optixModuleCreate`?

The answer from the 2026-06-24 POD run is **no, not directly**.

## Evidence

- Script: `scripts/v4_tier3_optix_module_link_probe.py`
- Dry-run evidence: `future/v4/evidence/v4_tier3_optix_module_link_probe_dry_run_2026-06-24.json`
- POD evidence: `future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.json`

POD result:

- Numba PTX generated: `true`
- C++ OptiX loader compiled: `true`
- `optixModuleCreate` attempted: `true`
- `optixModuleCreate` succeeded: `false`
- blocked stage: `optix_module_create`
- OptiX error: `Invalid input`
- OptiX log: `COMPILE ERROR: No functions with semantic types found`

## Interpretation

This is not evidence that custom callbacks are impossible. It is evidence that a
bare Numba-generated helper function is not an OptiX module by itself. OptiX
expects semantic entry functions such as raygen, miss, hitgroup, or callable
entry points. A future Tier-3 path therefore needs a real wrapper/direct-callable
ABI spike, not a public callback API.

The full falsifiable callback spike protocol is
`future/v4/tier3_callback_spike_protocol_2026-06-24.md`. This page records a
failed Stage 2 bare-helper attempt. It does not authorize Tier-3 callback
support, raw OptiX callbacks, or V4 release wording.

## Current Boundary

This spike does not attempt:

- direct-callable program group creation
- composition of Numba PTX with a hand-written OptiX traversal shell
- program group creation
- pipeline creation
- launch
- correctness inside traversal
- callback overhead measurement

## Non-Claims

This page does not authorize:

- V4 release
- Tier-3 callback/PTX support claims
- raw OptiX callback support
- broad speedup wording
- whole-application speedup wording
- app-specific native engine kernels
