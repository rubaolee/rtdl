# Call For Review: V4 Tier-3 OptiX Module-Link Probe

Date: 2026-06-24

## Review Request

Please critically review the V4 Tier-3 OptiX module-link probe. This is blocked spike evidence, not a V4.0 release feature.

## Artifacts To Review

- Module-link script: `scripts/v4_tier3_optix_module_link_probe.py`
- PTX generation script: `scripts/v4_tier3_numba_ptx_probe.py`
- Module-link note: `future/v4/tier3_optix_module_link_spike.md`
- PTX note: `future/v4/tier3_numba_ptx_spike.md`
- Dry-run evidence: `future/v4/evidence/v4_tier3_optix_module_link_probe_dry_run_2026-06-24.json`
- POD evidence: `future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.json`
- Tests: `tests/v4_tier3_optix_module_link_probe_test.py`

## Facts Claimed

1. The probe generated Numba callback PTX on the POD.
2. The probe compiled a minimal C++ OptiX loader against the POD OptiX headers.
3. The loader attempted `optixModuleCreate` on the bare Numba helper PTX.
4. `optixModuleCreate` failed with `Invalid input`.
5. The OptiX module log included `COMPILE ERROR: No functions with semantic types found`.
6. The correct interpretation is that bare Numba helper PTX is not directly an OptiX module; a future path requires wrapper/direct-callable ABI work.
7. No V4.0 support claim, raw callback claim, or release claim is authorized.

## Questions For Reviewer

1. Is the blocked result correctly interpreted?
2. Does the probe cleanly distinguish PTX generation from OptiX module acceptance?
3. Does the documentation prevent overclaiming Tier-3 support?
4. Is wrapper/direct-callable ABI spike the right next engineering step if Tier-3 continues?
5. Should any additional negative test or evidence be added before this remains in `future/v4`?

## Expected Verdict Labels

- `accept_blocked_boundary_preserved`
- `accept_with_required_amendments`
- `reject_interpretation_overclaims_tier3`
- `reject_probe_not_valid`

## Non-Authorization

This review request does not authorize V4 release, Tier-3 callback support, raw OptiX callback API support, broad V4 speedup claims, app-specific native kernels, or movement of Tier-3 into the V4.0 release surface.
