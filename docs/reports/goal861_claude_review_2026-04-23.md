**Verdict: Goal861 is complete and correct. No issues.**

Key reasons:

1. **All 4 required artifacts are valid.** Both apps (`service_coverage_gaps`, `event_hotspot_screening`) produced `cpu_oracle_summary` and `embree_summary_path` artifacts with `status: ok`, `correctness_parity: true`, and `matches_reference: true` against their respective reference backends.

2. **Summary SHA256 parity holds within each app.** For `service_coverage_gaps`, both CPU and Embree artifacts share the same `summary_sha256` (`2c397aa1...`). For `event_hotspot_screening`, both share `70cdab00...`. This confirms semantic equivalence across backends.

3. **Phase separation is correct.** All four artifacts have `phase_separated: true` and all required phases covered (`input_build`, `optix_prepare`, `optix_query`, `python_postprocess`). The `optix_prepare: 0.0` on the local machine is expected since there is no RTX hardware.

4. **Claims are properly scoped.** All four set `authorizes_public_speedup_claim: false` and `claim_limit` to "prepared compact summary only; not nearest-row or whole-app speedup" — no overreach.

5. **Gate status is correct.** Goal860 reports `needs_real_rtx_artifact` with 0 required-missing and 0 required-invalid. The one remaining blocker is the absence of real OptiX phase artifacts (`goal811_service_coverage_rtx.json`, `goal811_event_hotspot_rtx.json`) from an RTX host — which is an external dependency, not a Goal861 deficiency.

6. **Minor note:** `event_hotspot_screening` ran at `copies: 2000` while `service_coverage_gaps` ran at `copies: 200`. Both are within the `scale: null` contract, so this is fine, but worth noting if future comparisons assume identical scale.
