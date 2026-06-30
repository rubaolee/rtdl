Here is the review output:

---

## VERDICT: ACCEPT-WITH-BOUNDARY

### What Was Checked

**Source-of-truth alignment** — `v1_5_migration_inventory.py` declares 4 stable core primitives, 6 stable scalar reductions, 1 experimental primitive, and `grouped_reduction.py` declares 8 grouped-reduction operations. The catalog Layer 1–4 tables match exactly. Counts in the report match the code. No phantom or missing entries.

**Primitive vs app code distinction** — the catalog has a clear definitional section with a classification table, the correct examples (DBSCAN cluster expansion, robot pose/link sampling, Barnes-Hut inverse-square force law all marked app/partner code), and Layer 5 explicitly separates app adapters. Test `test_catalog_separates_primitives_from_app_code` covers the key phrases.

**Behavior/maturity organization** — five explicit layers: stable core execution, stable scalar reduction, experimental collection, shared grouped-reduction substrate, app adapters. Layers are not collapsed. ✓

**User selection guide** — "How Users Select Primitives" section is behavior-first, maps needs to layer and candidate primitive path, and includes the composition example (RT-DBSCAN pipeline). Test covers it. ✓

**Benchmark-app injection history** — all four benchmark apps (RT-DBSCAN, Robot collision, RayDB-style, Barnes-Hut) appear in the injection history table with pressure and result. The rejected candidate `generic_aggregate_frontier_inverse_square_scalar_sum_3d_v1` with the exact hardcoded math string is named. Test covers it. ✓

**Overclaim blocking — catalog status header:** blocks public release wording, public speedup claims, external ABI stability, authors-code parity, paper reproduction claims. ✓

**Overclaim blocking — report boundary section:** explicitly lists and blocks all six user-specified overclaims including grouped-reduction stability, COLLECT_K_BOUNDED promotion, and Barnes-Hut native aggregate-frontier support. ✓

**Overclaim blocking — runtime enforcement:** `grouped_reduction.py`'s `to_metadata()` and `grouped_reduction_contract_metadata()` emit blocking `claim_boundary` strings. `v1_5_migration_inventory.py`'s validator rejects any row with `public_wording_authorized: True` and requires every boundary string to contain "public speedup wording" or "public wording". ✓

**Test coverage:** `test_report_blocks_overclaims` checks the report for six of the seven specific overclaim phrases. ✗ — one gap below.

---

### Exact Constraint

**Test gap — Barnes-Hut aggregate-frontier blocking phrase is not asserted.** The report's boundary section contains the line `claiming Barnes-Hut native aggregate-frontier support.` and the catalog records it as future work, but `test_report_blocks_overclaims` does not assert that phrase. If that line were accidentally deleted from the report, no test would catch it.

Add to `test_report_blocks_overclaims`:

```python
"claiming Barnes-Hut native aggregate-frontier support",
```

That closes the gap. All other content, structure, source-of-truth alignment, and blocking language are accurate and consistent. The catalog is acceptable for internal use within the boundaries stated in the report's boundary section and in the catalog's own status header.
