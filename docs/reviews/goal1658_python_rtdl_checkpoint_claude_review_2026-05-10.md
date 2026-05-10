---

## Independent Checkpoint Review — Goal1658 v2.5 Prep

### Verdict

**Pass with minor notes.** Both reports are honest, correctly bounded, and do not overclaim. The implementation in `python_rtdl_app_purity.py` is properly fail-closed. The test gate is structurally sound. The user's three explicit directives — keep fastest collect-k, freeze optimization studies before v2.5, pivot to Python+RTDL app purity — are all faithfully recorded and enforced.

---

### Strengths

**Honest self-reporting.** The perf checkpoint explicitly notes timings are "exact-subpath measurements, not whole-application measurements" and warns against treating the `0.637297 ms` run as a universal device constant rather than the fastest observed baseline. No speedup language appears anywhere.

**Correct fail-closed design.** `validate_python_rtdl_product_checkpoint` (`python_rtdl_app_purity.py:205`) inverts the usual pass/fail convention: it *raises* if `product_ready=True`, raises if there are no app blockers, and raises if the native symbol audit unexpectedly clears. This means the gate can only pass while the system is still known-incomplete — the correct posture for a pre-release checkpoint.

**If native API files are absent, the gate fails loudly.** When `_exported_symbols` finds no C++ files, `classifications=[]` → `pure_native_app_contract_ready=True` → `validate_python_rtdl_product_checkpoint` raises `ValueError`. The test `test_native_audit_detects_legacy_app_shaped_exports` also fails if named symbols aren't found. Both paths are fail-closed independently.

**Claim boundary is explicit and multi-layered.** Both reports carry a dedicated "Claim Boundary" section. Between them they deny: v2.5 release action, stable `COLLECT_K_BOUNDED` promotion, public speedup wording, whole-app speedup wording, broad RTX/GPU acceleration wording, true zero-copy wording. Nothing slipped through.

**Freeze directive is machine-encoded.** `PYTHON_RTDL_OPTIMIZATION_FREEZE_UNTIL = "v2.5"` (`python_rtdl_app_purity.py:14`) and the corresponding `validate` check (`line 209`) mean the freeze boundary can't be silently removed from code without breaking the test.

**Test anchors report text against exact strings.** `test_perf_report_freezes_fastest_solution_until_v2_5` and `test_project_checkpoint_names_python_rtdl_purity_rule` are phrase-level regression tests against both markdown documents. If someone softens the freeze language in the reports, the test fails.

---

### Risks

**Unverifiable upstream dependency.** `python_rtdl_app_purity.py:8` imports `v1_5_standalone_app_classification.v1_5_standalone_app_classification_matrix`. The entire `python_rtdl_app_purity_matrix()` function — and therefore `product_ready` and all app-level blocker decisions — delegates to that module. Its classification correctness cannot be verified from the files provided. If it misclassifies a legacy app as `fully_generic`, the gate silently passes for that app.

**Regex only captures `int`-returning native exports** (`python_rtdl_app_purity.py:87`). The pattern `(?:extern\s+"C"\s+int|RTDL_EMBREE_EXPORT\s+int)` would miss any `void`-returning or `bool`-returning exported functions. If an app-shaped export uses a different return type, it escapes the audit entirely — no blocker, no `unclassified` fallback. This is a real coverage gap.

**Fragment lists are static and not exhaustively tested.** `_APP_SHAPED_NATIVE_SYMBOL_FRAGMENTS` and `_GENERIC_NATIVE_SYMBOL_FRAGMENTS` are maintained by hand. The tests verify that specific *known* app-shaped symbols are caught, but they don't assert an exhaustiveness floor (e.g., "at least N symbols classified, of which at least M are legacy"). A new app-shaped export using an unrecognized fragment name would fall to `"unclassified"` — which is a blocker, so fail-closed — but the test wouldn't tell you *which* symbol was new.

**Four-way merge probe entry in the rejected list is ambiguous.** The perf report states the four-way merge "preserved parity in diagnostic scope but was slower for production-relevant group counts." That's correct rejection reasoning, but "parity in diagnostic scope" could be read as partial evidence in its favor by a future reader. The phrase is not dangerous here, but it's the one place in the document where a reader could attempt to rehabilitate a rejected candidate.

---

### Required Changes

1. **Expand the `_exported_symbols` regex to cover non-`int` return types, or add a documented carve-out.** The current pattern silently skips `void` and other return types. Minimum fix: extend the alternation to `(?:extern\s+"C"\s+\w+|RTDL_EMBREE_EXPORT\s+\w+)`, or add a comment noting the limitation so a future auditor knows to check it explicitly.

2. **Add a symbol-count floor assertion to the native audit test.** `test_native_audit_detects_legacy_app_shaped_exports` currently asserts specific symbols are present but doesn't assert a minimum total. If the C++ API files shrink significantly (symbols removed, file renamed, path changed), the named-symbol assertions would still pass on whatever subset remains. Add `self.assertGreater(len(audit["native_symbols"]), N)` for a known-safe floor based on the current API surface.

3. **Document the dependency on `v1_5_standalone_app_classification_matrix`.** A comment or a test assertion that the matrix returns at least the four apps checked in `test_app_matrix_separates_pure_target_from_blockers` would make the upstream dependency explicit and catch silent regressions if that module changes app classifications.
