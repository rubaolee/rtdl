# Call For Review: V4 Tier-3 Numba PTX Probe

Date: 2026-06-24

## Review Request

Please critically review the V4 Tier-3 Numba PTX probe. This is a spike-only boundary check, not a V4.0 release feature.

## Artifacts To Review

- Probe script: `scripts/v4_tier3_numba_ptx_probe.py`
- Spike note: `future/v4/tier3_numba_ptx_spike.md`
- Dry-run evidence: `future/v4/evidence/v4_tier3_numba_ptx_probe_dry_run_2026-06-24.json`
- POD evidence: `future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.json`
- User-facing index link: `future/v4/README.md`
- Local tests: `tests/v4_tier3_numba_ptx_probe_test.py`

## Facts Claimed

1. A scalar Numba CUDA device function can generate PTX on the POD when the packaged NVVM toolchain is available.
2. The probe records the Linux dynamic-linker requirement by re-executing once with the NVVM library directory in `LD_LIBRARY_PATH`.
3. The evidence records `ptx_generated: true`, `cuda_available: true`, and `contains_visible_func_directive: true`.
4. The probe does not attempt OptiX module linking.
5. The probe does not authorize V4 release, Tier-3 callback support claims, raw OptiX callbacks, app-specific native kernels, or broad speedup wording.

## Questions For Reviewer

1. Is this correctly scoped as Tier-3 spike evidence rather than V4.0 product support?
2. Is the dynamic-linker re-exec behavior appropriate and honestly documented?
3. Does the evidence prove only PTX generation, without implying OptiX callable integration?
4. Are the non-authorization fields and prose strong enough to prevent public overclaiming?
5. Are any missing tests or docs required before this can remain in `future/v4`?

## Expected Verdict Labels

- `accept_spike_boundary_preserved`
- `accept_with_required_amendments`
- `reject_overclaims_tier3_support`
- `reject_evidence_insufficient`

## Non-Authorization

This review request does not authorize V4 release, Tier-3 callback support, raw OptiX callback API support, broad V4 speedup claims, app-specific native kernels, or movement of Tier-3 into the V4.0 release surface.
