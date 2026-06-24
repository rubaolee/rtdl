Goal3520: v2.8 Claim-Boundary And Stale-Doc Audit Review

Status: accept-with-boundary

## Findings:

1.  **Stale `v2.x` / `v2.5` wording:** The goal correctly addresses stale `v2.x` / `v2.5` wording. Legacy versioned helper names (`v2_5`, `v2_6`) in Python source are explicitly identified as compatibility/protocol debt, quarantined in constants, and documented for future work in `docs/research/future_version_to_do_list.md`. This is appropriately verified by `tests/goal3520_v2_8_claim_boundary_stale_audit_test.py`.

2.  **Active learner Markdown surface claims:** The active learner Markdown surface is largely free of overclaims. Python example files (e.g., in `examples/v2_0/research_benchmarks/`) consistently use `claim_boundary` dictionaries to set various authorization flags (e.g., `release_claim_authorized`, `public_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `full_rayjoin_reproduction`) to `False`.
    **Boundary noted:** The `README.md` file contains references to "Historical v2.6 Release Package" and "Historical v2.3 Release Package". While these refer to historical versions, the audit's `rg` check explicitly includes "release package" with an expectation of "no output". This indicates a slight deviation from the strict "no output" rule for the specified pattern in the active learner Markdown surface. This should ideally be removed or rephrased if the "no output" rule is to be strictly adhered to.

3.  **`v2_5` / `v2_6` Python names quarantined:** Yes, the remaining `v2_5` / `v2_6` Python names are legitimately quarantined as compatibility/protocol debt. They are referenced in constants (`RAYJOIN_V2_6_NUMBA_COMPACT_MASK_VERSION`, `RAYJOIN_V2_5_NUMBA_HAUSDORFF_VERSION`) and explicitly noted for future work in `docs/research/future_version_to_do_list.md` under "Legacy Versioned Helper Names".

4.  **`tests/goal3520_v2_8_claim_boundary_stale_audit_test.py` as a guard:** The test provides a meaningful fail-closed guard for checking the legitimate quarantining of `v2_5` / `v2_6` names and their documentation.
    **Boundary noted:** The test *does not fully cover all specified claim-boundary risks*. Specifically, it does not check for the presence of forbidden phrases (such as "release package", "public speedup claim authorized", etc.) within the active learner Markdown surface files (e.g., `README.md`, `docs/learn/*.md`, `docs/tutorials/*.md`) as comprehensively as the `rg` command in the suggested checks. Additionally, it does not explicitly assert the `False` values within the `claim_boundary` dictionaries found in the Python example applications. This means some material stale-doc/claim-boundary risks could be missed by the current test suite.

5.  **Authorization of release/public claims:** This goal explicitly does not authorize release or public claims. The audit report clearly states "internal closeout audit; not release authorization," and this is consistently reflected in the `claim_boundary` flags within the Python example code.

## Recommendation:
The goal generally meets its objectives, but the minor discrepancies regarding "release package" mentions in `README.md` and the partial coverage of `claim_boundary` checks in the unit test warrant an `accept-with-boundary` status. It is recommended to either remove/rephrase the "Historical Release Package" mentions in `README.md` to comply with the strict "no output" rule or clarify if such historical mentions are acceptable. Additionally, consider expanding `tests/goal3520_v2_8_claim_boundary_stale_audit_test.py` to include checks for forbidden phrases in Markdown and explicit assertions for the `claim_boundary` dictionaries in Python example files to fully close all described risks.
