# V4 Goal4686 Tier-3 Wrapper ABI Scaffold

Status: local scaffold only, not Tier-3 support and not POD authorization

- status: `goal4686_tier3_wrapper_abi_local_scaffold_complete_no_pod`
- callback symbol: `rtdl_user_scalar_reduce`
- semantic entries: `__direct_callable__rtdl_tier3_scalar_reduce, __raygen__rtdl_tier3_probe, __miss__rtdl_tier3_probe, __closesthit__rtdl_tier3_probe`
- old bare PTX success path allowed: `False`
- pod authorized: `False`

## Boundary

This dry-run emits the semantic wrapper scaffold that a later compile/link gate must test. It does not compile OptiX, link Numba PTX, launch a pipeline, or authorize Tier-3 support.

## Non-Authorization

No release, no Tier-3 public support, no raw OptiX callback support, no broad speedup wording, no whole-app claim, and no app-specific native kernels.
