---

## M38 Review: Phoenix V3 Component-Union Focused POD Protocol

**Verdict: `accept_m38_authorize_one_focused_component_union_pod_after_harness_gate`**

---

### Working Through the Seven Review Questions

**1. Is the row serious enough?**

Yes. 262,144 clustered 3D points, fixed-radius, warmup 1, repeat 5, with `smoke_rows_do_not_count: true` and `serious_scale_floor_points: 262144` explicit in the JSON. Scope boundary is correctly bounded: "not full DBSCAN paper reproduction and not a broad RTDBSCAN app speedup claim." No issue.

**2. Are the variants truly same-contract for component-union labels?**

Yes. All three variants must report `component_labels_contract` and `canonical_component_signature`. The runner must additionally report `component_label_columns_present=true` and `component_signature_pass_executed=false`, ensuring the productized path is exercising label production, not a signature shortcut. The Embree same-contract variant is a genuine non-RT-core control, making the 1.20x gap specifically about the RT-core advantage. No issue.

**3. Does the protocol adequately block component-signature shortcuts?**

Yes, and the blocking is multiply redundant:
- Pre-run gate: "Component-signature rows cannot replace component-union label rows"
- Failure classification: `component_signature_substituted_for_labels` → "invalid run; no performance interpretation"
- Runner metadata: `component_signature_pass_executed=false` is a required must_report field
- Correctness success bar: "matching canonical component signatures from **component-label outputs**"
- MD text: "A signature-only route cannot replace component-union label work"

No issue.

**4. Are the success bars correct for a Set-A material candidate?**

Yes. The dual gate (both hot query median AND runner-inclusive wall must clear 1.20x over Embree same-contract) is the right structure — single-metric success bars have been the historical gap. The 0.98x legacy no-regression bar guards against productizing a regression. Both bars failing closed is correct behavior. No issue.

**5. Is the resource estimate reasonable and bounded?**

Yes. Hard cap of 2h/$0.50 before requiring a new review. All-app POD explicitly "not authorized" in the JSON field. The focused POD cost estimate ($0.19–$0.38) is calibrated, not inflated. No issue.

**6. M39 harness-only or POD after harness gate?**

The rationale for the more permissive verdict: M38 satisfies the "2-AI review before any focused POD run" pre-run gate. The harness gate (local dry-run, unit tests, must_report metadata flags) is a meaningful filter — specifically, `runtime_executed=true`, `runtime_trunk_executes_end_to_end=true`, `component_union_phase_accounting_visible=true`, and `component_label_columns_present=true` can only be emitted if the M37 path actually ran end-to-end. A harness that emits those flags and passes local unit tests has, by construction, exercised the correct code path. Requiring a third review round after M39 adds delay without proportionate safety gain given those gates are already predeclared and fail-closed.

**7. Are any non-authorization boundaries accidentally weakened?**

No. All seven forbidden flags (`release_authorized`, `public_speedup_claim_authorized`, `broad_v3_faster_than_v2_claim_authorized`, `true_zero_copy_claim_authorized`, `external_embedding_or_zero_copy_claim_authorized`, `focused_pod_spend_authorized_now`, `all_app_pod_spend_authorized`) are `false` in the JSON and consistent across the MD, the report, and the call-for-review. The success bar `claim_boundary` field explicitly names "V4" and "zero-copy." The test suite validates these flags machine-checkably.

---

### Validation Evidence

The report shows both test runs passed:
- 9 M38-specific unit tests: OK
- 614 v3_rebuild matrix tests across 118 modules: OK

---

### Non-Blocking Follow-Ups

1. **M39 harness implementation required before any POD spend.** `scripts/v3_phoenix_component_union_m38_pod_ab.py` does not exist yet. It must be written and pass local dry-run before any POD clock starts.
2. **All three variants on the same generated point set.** The harness must enforce this, not just the protocol text.
3. **OptiX RT hardware gate must be confirmed** on the target machine (RTX-class) before spending POD — an environment check, not a protocol gap.
4. **Heartbeat output every 30 seconds** is already required by the protocol; the harness must implement it.
5. **Hard cap enforcement.** The harness or caller must abort if wall time exceeds 2h or cost exceeds $0.50.

---

### Non-Authorization Confirmation

This review does not authorize: V3 release, all-app POD spend, public speedup wording, broad V3-over-V2 wording, true-zero-copy wording, automatic partner selection, V4 work, C ABI work, or embedding work.
