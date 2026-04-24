**Verdict: Approved — clean and well-scoped.**

**Key reasons:**

1. **Correct scope isolation.** The gate filters exactly the two spatial apps (`service_coverage_gaps`, `event_hotspot_screening`) from the broader plan, which is the stated purpose — no accidental spillover to other app families.

2. **Three-state progression is sound.** `needs_required_baselines` → `needs_real_rtx_artifact` → `ready_for_review` maps directly to the real dependency chain and prevents premature promotion. The logic at lines 108–112 correctly short-circuits when required checks aren't all valid.

3. **Optional baseline is truly optional.** `scipy_baseline_when_available` is correctly segregated into `optional_checks` and excluded from the gate's blocking counters. Tests confirm the split (test line 27–29).

4. **RTX artifact validation is strict.** `_rtx_artifact_status` explicitly rejects non-`optix` mode artifacts and artifacts missing `optix_query` timing — no dry-run or placeholder can pass as valid.

5. **Test coverage is adequate.** Three tests cover row filtering, the optional/required split, and CLI output writing. They're behavioral, not overly coupled to internals.

6. **One minor nit:** `_rtx_artifact_status` does a direct dict lookup `RTX_ARTIFACTS[(app, path_name)]` (line 39) with no `KeyError` guard. If `build_plan()` ever returns a spatial row whose `path_name` doesn't match the hardcoded map, it will raise unchecked. Low risk given the map is exhaustive for the two apps, but worth noting.
