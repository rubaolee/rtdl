## Review: Phoenix V3 M39 Component-Union Harness

**Verdict: `accept_m39_authorize_one_focused_component_union_pod`**

---

### Check-by-check findings

**1. Does the harness preserve the M38 component-label contract?**

Yes, with one stylistic note. All three variants call label-producing APIs:
- EMBREE: `radius_graph_components_3d_numba_prepared_grid_partner_columns()` → `signature_from_numba_label_columns()` (labels required by the call chain)
- LEGACY: `fixed_radius_graph_component_labels_3d_v2_8()` → `signature_from_numba_label_columns()`
- RUNNER: `run_radius_graph_component_union_3d_prepared_session()` + metadata-derived `component_label_columns_present`

The stylistic note: `component_labels_contract` and `component_label_outputs_present` are hardcoded `True` in `finalize_variant_payload()` (lines 514–515) for EMBREE and LEGACY rather than derived from runtime checks. This is not a blocking issue because the `signature_from_numba_label_columns()` call itself evidences label production (it would fail on empty columns), and `failure_checks()` independently catches the `canonical_component_signature is None` case (line 712). The enforcement path is real.

**2. Does it block component-signature-only substitution?**

Yes, through three independent layers:
- Static: test at line 75 asserts `run_radius_graph_component_signature_3d_prepared_session(` is absent from source
- Runtime (RUNNER): `component_signature_pass_executed` read from metadata, checked in `failure_checks()` (line 731)
- Runtime (RUNNER): `component_label_columns_present` also read from metadata, checked (line 729)
- Structural (EMBREE/LEGACY): no signature-only API is called; labels are the only path

The combination is strong.

**3. Are the three variants same-contract enough for a focused A/B?**

Yes. The point set is generated once in-process at lines 122–123 and passed to all variants under `--variant all`. `same_generated_point_set_enforced` reflects `args.variant == "all"` (line 585). All three variants call `signature_from_numba_label_columns()` with the same derivation logic. `comparison_payload()` enforces `all_variant_canonical_component_signatures_match`, and `failure_checks()` treats mismatch as a hard fail (line 717). Same input, same derivation, explicit equality check — sufficient for A/B.

**4. Does the productized route actually use `run_radius_graph_component_union_3d_prepared_session`?**

Yes. Direct call at line 407:
```python
result = rt.run_radius_graph_component_union_3d_prepared_session(
    point_rows=points, point_rows_fingerprint=point_fingerprint, ...
)
```
Test at line 68 also asserts the string is present in source.

**5. Are heartbeat and hard-cap enforcement sufficient for paid POD use?**

Yes. Two independent layers:
- `ensure_hard_cap()` (lines 762–765): pre-variant check, raises `TimeoutError` if elapsed already exceeds cap
- `hard_cap_watchdog()` (lines 768–788): `threading.Timer` calling `os._exit(124)` — kills the process if a single variant hangs past the cap, covering mid-variant stalls that `ensure_hard_cap` cannot reach

The 2h / $0.50 cap matches the M38 consensus requirement. The test at line 74 verifies `os._exit(124)` exists in source. Heartbeat runs every 30s per variant (default). Sufficient for paid POD use.

**6. Does the `radius=3.0` density risk need a protocol revision before POD?**

No revision needed. The report (lines 110–116) correctly frames the outcome space: timeout → hard cap fires → result is treated as **blocked/negative evidence, not timing data**. The harness cannot be massaged into a speed claim if it times out because `os._exit(124)` produces no JSON output. The fail-closed treatment is principled. The M38 consensus explicitly accepted `clustered3d_262144_points_repeat5` with `radius=3.0`; changing the parameters would require a new consensus row.

**7. Are any non-authorization boundaries weakened?**

No. Every output surface — `finalize_variant_payload()` (lines 524–531), `build_payload()` summary and `claim_boundary` (lines 590–631), `dry_run_variant_payload()` (lines 196–198), and the generated README — hardcodes all forbidden claims to `False`. The claim boundary explicitly covers V4, C ABI, and embedding work in addition to release/speedup/all-app/zero-copy. `STATUS_NOT_RELEASE = "component_union_m39_harness_ready_not_pod_run"` is the sole status string.

---

### Conditions on the authorized POD run

The M38 consensus conditions apply without modification:

- Run with `--variant all --require-rt-hardware` so same-point-set enforcement and hardware gate are active
- The outcome space is: pass (material Set-A candidate if all metadata bars are met), fail (negative evidence), or timeout/124 exit (blocked evidence — treat as negative, not re-runnable toward a speed claim)
- If `runner_vs_embree_hot_speedup < 1.20x` or any of the metadata flags fail, result is coverage-only, not release evidence
- No all-app POD, no public speedup wording, no V3 release authorization follows from this run regardless of outcome
