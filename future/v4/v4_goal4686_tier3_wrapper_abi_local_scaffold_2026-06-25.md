# V4 Goal4686 Tier-3 Wrapper ABI Local Scaffold

Date: 2026-06-25

Status: `goal4686_tier3_wrapper_abi_local_scaffold_complete_no_pod`

## Decision

Goal4686 implements the local scaffold for the Tier-3 semantic OptiX wrapper/direct-callable ABI.

This is the first concrete step beyond the old failed bare-PTX probe. The scaffold contains real OptiX semantic entry names:

- `__direct_callable__rtdl_tier3_scalar_reduce`
- `__raygen__rtdl_tier3_probe`
- `__miss__rtdl_tier3_probe`
- `__closesthit__rtdl_tier3_probe`

It also defines the callback symbol contract:

- `rtdl_user_scalar_reduce`

## Evidence

Generated local dry-run evidence:

- `future/v4/evidence/v4_goal4686_tier3_wrapper_abi_scaffold_2026-06-25.json`
- `future/v4/evidence/v4_goal4686_tier3_wrapper_abi_scaffold_2026-06-25.md`
- `future/v4/evidence/v4_goal4686_tier3_wrapper_abi_scaffold_2026-06-25.cu`

Dry-run result:

```text
validation_status: passed
dry_run_only: true
old_bare_ptx_success_path_allowed: false
pod_authorized: false
release_authorized: false
tier3_public_support_authorized: false
raw_optix_callback_authorized: false
```

## What This Proves

It proves the local scaffold is no longer the old bare helper PTX path. The next spike has a concrete semantic wrapper shape and a named callback symbol contract.

## What This Does Not Prove

It does not prove:

- Numba callback symbol extraction/aliasing works under real PTX;
- the semantic wrapper compiles on POD;
- callback PTX and wrapper PTX/OptiX-IR link into one OptiX pipeline;
- program group creation succeeds;
- launch succeeds;
- correctness parity;
- overhead within the `<=1.50x` ceiling;
- Tier-3 public support.

## Goal-Level Decision Audit

1. Was I being stupid?

No. I did not rerun the old failed probe or pretend the scaffold is support.

2. If yes, what action made it stupid?

The stupid action would have been to run bare Numba PTX through `optixModuleCreate` again and call that progress. Goal4686 avoids that.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. Use a semantic OptiX wrapper/direct-callable ABI and make symbol extraction the next explicit gate.

4. Can I now try the different path that actually solves the problem?

Yes. Goal4687 should prove symbol extraction/aliasing and compile the semantic wrapper shape. It must still not run a full POD overhead benchmark until compile/link gates pass.

## Next Goal

Goal4687: Tier-3 wrapper ABI symbol extraction and compile probe.

Required:

- extract or alias the Numba callback symbol to `rtdl_user_scalar_reduce`;
- compile the semantic wrapper shape or record the exact compile blocker;
- keep all Tier-3 support/release/speed claims false.

## Non-Authorization

Goal4686 does not authorize POD, V4 release, Tier-3 public support, raw OptiX callback support, public speedup wording, whole-app speedup wording, app-specific native kernels, C ABI, embedding, true-zero-copy, or non-Python host claims.
