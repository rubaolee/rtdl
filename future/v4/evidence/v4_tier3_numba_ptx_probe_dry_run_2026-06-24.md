# V4 Tier-3 Numba PTX Probe

Status: generated spike evidence, not Tier-3 support and not a release authorization

- status: `dry_run`
- PTX generated: `False`
- OptiX module link attempted: `False`

## Boundary

This probe only checks whether a scalar Numba device callback can produce PTX. It does not prove OptiX module linking, callable overhead, correctness inside traversal, or public Tier-3 support.

## Non-Authorization

This probe does not authorize V4 release, Tier-3 callback/PTX support claims, raw OptiX callbacks, broad speedup wording, or app-specific native kernels.
