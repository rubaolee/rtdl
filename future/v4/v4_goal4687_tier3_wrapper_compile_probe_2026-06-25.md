# V4 Goal4687 Tier-3 Wrapper Symbol Extraction And Compile Probe

Date: 2026-06-25

Status: `semantic_wrapper_compile_passed_no_module_link`

Goal status: `goal4687_tier3_wrapper_symbol_compile_probe_not_support`

## Decision

Goal4687 passed the compile probe on the current POD.

This is real Tier-3 progress: the route no longer fails at "bare Numba helper PTX has no OptiX semantic function." The probe generated Numba PTX, extracted the actual Numba callback symbol, specialized the semantic OptiX wrapper source to that symbol, and compiled the wrapper to PTX with `nvcc`.

It does not authorize Tier-3 support or release wording.

## Evidence

POD:

```text
root@194.68.245.170 -p 22089
```

Evidence files:

- `future/v4/evidence/v4_goal4687_tier3_wrapper_compile_probe_2026-06-25.json`
- `future/v4/evidence/v4_goal4687_tier3_wrapper_compile_probe_2026-06-25.md`
- `future/v4/evidence/v4_goal4687_tier3_wrapper_compile_probe_dry_run_2026-06-25.json`
- `future/v4/evidence/v4_goal4687_tier3_wrapper_compile_probe_dry_run_2026-06-25.md`

Observed result:

```text
numba_ptx_generated: true
symbol_probe.status: symbol_extracted
symbol_probe.c_identifier_compatible: true
wrapper_source_generated: true
wrapper_compile_attempted: true
wrapper_compile_succeeded: true
status: semantic_wrapper_compile_passed_no_module_link
optix_module_link_attempted: false
pipeline_launch_attempted: false
```

Extracted callback symbol:

```text
_ZN8__main__21_custom_scalar_reduceB2v1B96cw51cXTLSUwv1sCUt9Uw1VEw0NRRQPKiLTj0gIGIFp_2b2oLQFEYYkHSQB1OQAk0Bynm21OizQ1K0UoIGvDpQE8oxrNQE_3dEddd
```

Wrapper compile:

```text
/usr/local/cuda/bin/nvcc -ptx -std=c++17 -I /root/vendor/optix-dev/include tier3_wrapper.cu -o tier3_wrapper.ptx
returncode: 0
wrapper_ptx_length: 2179
```

## Important Boundary

This result proves only:

- Numba scalar callback PTX can be generated on the POD;
- the callback symbol can be extracted;
- the symbol is C-identifier-compatible in this case;
- a semantic OptiX wrapper source can be specialized to that symbol;
- `nvcc` can compile that semantic wrapper shape to PTX.

It does not prove:

- callback PTX and wrapper PTX can be linked into one OptiX module;
- `optixModuleCreate` succeeds on the composed semantic module;
- program group creation succeeds;
- pipeline creation succeeds;
- launch succeeds;
- callback correctness parity;
- callback dispatch overhead;
- public Tier-3 support.

## Goal-Level Decision Audit

1. Was I being stupid?

No. I did not treat the compile probe as module-link success or support.

2. If yes, what action made it stupid?

The risky action would have been to stop at wrapper compile and call Tier-3 solved. The report explicitly blocks that.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. Goal4688 must attempt the actual OptiX semantic module-link/program-group/pipeline gate.

4. Can I now try the different path that actually solves the problem?

Yes. The next gate is concrete: compose callback PTX and wrapper PTX/OptiX-IR, then test `optixModuleCreate`, program groups, pipeline, and a minimal launch.

## Next Goal

Goal4688: Tier-3 semantic wrapper OptiX module-link probe.

Required:

- compose the Numba callback PTX with the semantic wrapper PTX/OptiX-IR;
- attempt `optixModuleCreate`;
- attempt program group creation;
- attempt pipeline creation;
- attempt a minimal launch only if the earlier stages pass;
- preserve all support/release/speed non-authorizations.

## Non-Authorization

Goal4687 does not authorize V4 release, Tier-3 public support, raw OptiX callback support, public speedup wording, whole-app speedup wording, app-specific native kernels, C ABI, embedding, true-zero-copy, or non-Python host claims.
