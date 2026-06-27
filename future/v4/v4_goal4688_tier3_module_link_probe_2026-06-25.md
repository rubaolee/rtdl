# V4 Goal4688: Tier-3 Semantic Wrapper Module-Link Probe

Date: 2026-06-25
Status: `semantic_module_pipeline_created_no_launch`

## Result

Goal4688 passed its narrow hardware gate on the current POD
`root@194.68.245.170:22089`:

- Numba scalar callback PTX generated: `true`
- callback symbol extracted: `_custom_scalar_reduce`
- wrapper compiled with `nvcc -ptx --keep-device-functions`: `true`
- combined callback + semantic wrapper PTX generated: `true`
- `optixModuleCreate` / `optixModuleCreateFromPTX` path succeeded: `true`
- raygen, miss, hitgroup, and direct-callable program groups created: `true`
- `optixPipelineCreate` succeeded: `true`
- pipeline launch attempted: `false`

Evidence:

- `future/v4/evidence/v4_goal4688_tier3_module_link_probe_2026-06-25.json`
- `future/v4/evidence/v4_goal4688_tier3_module_link_probe_2026-06-25.md`

## What Actually Moved

This goal moves Tier-3 from "Numba PTX can be generated and a wrapper can
compile" to "Numba callback PTX can be composed with a semantic OptiX wrapper
and accepted into an OptiX module, program groups, and pipeline."

The important fix was concrete: the semantic wrapper must be compiled with
`--keep-device-functions`. Without that flag, nvcc emits the direct callable as
an internal `.func`; OptiX can compile the module but cannot create the callable
program group. With the flag, the PTX exposes:

```text
.visible .func __direct_callable__rtdl_tier3_scalar_reduce()
```

The second fix was to keep Goal4688's raygen entry empty. A normal C call from
raygen to the direct callable caused `optixPipelineCreate` to fail with an
unresolved external symbol. The real launch path must use an OptiX callable
mechanism, which belongs to Goal4689.

## Boundaries

This is still Tier-3 spike evidence only.

Not authorized:

- public Tier-3 callback support
- raw arbitrary OptiX callback support
- performance or overhead claims
- app-level speedup claims
- V4 release or tag claims
- app-identity kernels

Goal4689 is the next concrete gate: minimal launch correctness. Until that
passes, this is module/pipeline construction evidence, not runnable user
callback support.

## Goal-Level Decision Audit

1. Was I being stupid?
   No after the corrective read of the evidence. The initial failure was not
   papered over; it was reduced to the direct-callable entry visibility problem.

2. If yes, what action made it stupid?
   The risky action would have been to call the first failed module-link result
   "almost done" or move to another target. I did not do that. I stayed on the
   failing ABI stage.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Instead of assuming an entry-name string bug, the path was to inspect
   generated PTX and test nvcc visibility flags on the POD.

4. Can I now try the different path that actually solves the problem?
   Yes. The next path is Goal4689: use the created pipeline in a minimal launch
   probe with an explicit callable invocation contract, then validate callback
   output before any overhead or public-support claim.
