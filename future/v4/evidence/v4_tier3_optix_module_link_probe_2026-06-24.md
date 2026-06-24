# V4 Tier-3 OptiX Module-Link Probe

Status: spike evidence only, not Tier-3 support and not a release authorization

- status: `blocked`
- PTX generated: `True`
- OptiX module link attempted: `True`
- OptiX module link succeeded: `False`
- program group create attempted: `False`
- pipeline launch attempted: `False`

## Boundary

This probe checks only whether Numba-generated scalar callback PTX is accepted by `optixModuleCreate`. It does not prove OptiX callable wiring, program group creation, traversal integration, callback overhead, or public Tier-3 support.

## Non-Authorization

This probe does not authorize V4 release, Tier-3 callback/PTX support claims, raw OptiX callbacks, broad speedup wording, or app-specific native kernels.

## Blocked Stage

- blocked stage: `optix_module_create`
