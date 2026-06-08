# Claude Review: Goal4047 RT-DBSCAN Partition Signature App Mode

Date: 2026-06-08
Reviewer: Claude (external review pass)
Verdict: **accept**

---

## Scope

This review covers the app-mode exposure added in Goal4047:

- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `docs/reports/goal4047_rt_dbscan_partition_signature_app_mode_2026-06-08.md`
- `docs/reports/goal4047_rt_dbscan_partition_signature_app_mode_pod_smoke.json`
- `tests/goal4047_rt_dbscan_partition_signature_app_mode_test.py`
- Related primitives: Goal4045/4046 reports and tests

---

## Question 1 — Correct primitive exposure, no promoted-route change

**Finding: Pass.**

The new mode `partner_cupy_partition_convergence_component_signature_3d` is implemented at
`rtdl_rt_dbscan_benchmark_app.py:1183–1234`. It calls
`rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d`
(line 1185), which is the Goal4045 primitive. This is the correct delegation point.

The two plan functions `plan_rt_dbscan_execution` (lines 61–84) and
`plan_rt_dbscan_continuation_execution` (lines 87–150) are unmodified and do not
reference the new mode. The new mode therefore cannot be reached by the
`planned_rt_dbscan` or `planned_rt_dbscan_continuation` dispatch paths. The
`argparse` choices at lines 1882–1902 list the new mode alongside the other
research modes, confirming it is an explicit user selection, not an inferred one.

The metadata set at lines 1196–1224 reinforces this:

- `current_default_route: False` (line 1204)
- `partition_convergence_hybrid_candidate: True` (line 1201)
- `partition_convergence_hybrid_promoted: False` (line 1202)
- `explicit_candidate_preview: True` (line 1203)

No promoted route is touched.

---

## Question 2 — Fixed-radius graph component contract, not DBSCAN semantics

**Finding: Pass.**

The mode returns `rows = ()` (line 1192) and sets `signature_override` from
`component_sizes = result["columns"]["component_size_signature"]` (lines 1193–1194).
This eliminates the per-point DBSCAN `is_core`/`cluster_id` output entirely.

Metadata at lines 1219–1221 is explicit:

```
"full_dbscan_semantics": False,
"dbscan_core_border_noise_semantics": False,
"graph_component_contract_only": True,
```

The `_component_size_signature_payload` helper at lines 755–762 uses the contract
string `fixed_radius_graph_component_size_signature_3d`, with no DBSCAN vocabulary.

The validation path at lines 1225–1234, when `validate=True`, computes the
reference from
`build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d`
rather than `cpu_spatial_bucket_dbscan`. This is correct: validating a
graph-component signature against a graph-component reference rather than against
a DBSCAN core/border/noise oracle. The caller at lines 1822–1825 then uses
`reference_signature_override` (set at line 1234) when it is present, so the
CPU DBSCAN oracle is never consulted for this mode.

The `full_dbscan` claim-boundary field at line 1858 uses:

```python
bool(metadata.get("full_dbscan_semantics", mode != "partner_core_flags_3d"))
```

For this mode, `full_dbscan_semantics` is explicitly `False` in `metadata`, so the
default branch is never reached. Result: `full_dbscan: False`.

---

## Question 3 — Claim boundaries

**Finding: All tested boundaries preserved.**

### No full DBSCAN claim
`full_dbscan_semantics: False`, `dbscan_core_border_noise_semantics: False`,
`full_dbscan: False` in `claim_boundary`. Confirmed in pod smoke.

### No RT-core acceleration claim
`rt_core_accelerated: False` (line 1210), `optix_backend_used: False` (line 1209).
The native execution path is
`partner_cupy_fixed_radius_partition_convergence_preview_3d` — a pure-CuPy path
with no OptiX involvement. `rt_core_accelerated: False` propagates to
`claim_boundary.rt_core_accelerated` at line 1857.

### No release / public speedup claim
`public_speedup_claim_authorized: False` (line 1221),
`release_authorized: False` (line 1222). Both confirmed in pod smoke metadata.

### No app-specific native-engine logic
`native_abi_added: False` (line 1216). Pod smoke metadata confirms
`app_specific_engine_logic_allowed: false` and `native_abi_added: false`.

### No automatic partner selection / hidden dispatch
Pod smoke metadata confirms `automatic_partner_selection_allowed: false` and
`hidden_dispatch_allowed: false`. The plan functions are unchanged and never
select this mode. No conditional dispatch to this mode was introduced anywhere.

---

## Question 4 — Pod smoke sufficiency

**Finding: Sufficient for this scope.**

The pod smoke at commit `f36ad087` ran:

```bash
python3 ... --mode partner_cupy_partition_convergence_component_signature_3d --dataset tiny
```

It records:

- `matches_reference: true` — signature `{1, 4, 4}` matches reference `{1, 4, 4}`
- `signature.contract: fixed_radius_graph_component_size_signature_3d`
- All seven boundary flags false
- Nested `partition_summary_validation.status: accept`
- `typed_result_stream_validation.status: accept`

This is a narrow app-mode exposure goal, not a performance-promotion goal. The
smoke confirms end-to-end CuPy execution, correct signature output, and
explicit claim-boundary recording. A larger-scale timing run is not required
here because Goal4046 already provided the timing comparison over eight
profiles at a prior commit; Goal4047's new contribution is the app surface, not
new timing evidence.

The `component_signature_sec: 0.507s` in the smoke reflects first-run JIT
overhead, which is expected and not a performance claim.

---

## Question 5 — Test adequacy

**Finding: Tests are focused and adequate.**

**`test_signature_mode_rejects_python_rows_before_cupy_is_needed`** (lines 48–60):
This is the most important correctness gate. The test confirms the
`include_rows=True` guard fires at lines 948–956 of the app — before any CuPy
import or GPU call. The test name makes the "before CuPy" property explicit.
The error message check `"signature mode does not materialize Python rows"` is
precise.

**`test_component_size_signature_payload_is_generic`** (lines 40–46):
Tests `_component_size_signature_payload` directly. Verifies zero-size filtering,
sort order, component count, and the generic contract string. No GPU required.

**`test_app_and_docs_expose_explicit_candidate_mode`** (lines 26–38):
Source-level check that all boundary vocabulary is present in the app, README,
and report. This catches regressions where a key term is accidentally removed.

**`test_pod_smoke_artifact_records_boundary`** (lines 62–76):
Reads the pod artifact and asserts all seven boundary flags. This is the
right static gate to keep the artifact honest without requiring GPU re-execution
in CI.

**`test_candidate_mode_matches_graph_component_reference`** (lines 81–111):
CuPy-gated end-to-end test. Verifies signature matches reference, checks all
boundary metadata flags. Appropriately skipped when CuPy is unavailable.

One minor omission: there is no test that verifies `reference_signature_override`
is used (rather than the CPU DBSCAN oracle) when `validate=True`. The existing
test `test_candidate_mode_matches_graph_component_reference` exercises
`validate=True` end-to-end and checks `reference_signature.contract ==
fixed_radius_graph_component_size_signature_3d`, which implicitly verifies the
correct reference path — but this is worth noting as a reader gap rather than a
defect.

---

## Minor Observations (non-blocking)

1. **Validation reference path implicit** (`app:1225–1234`): The correct
   reference path is taken because `reference_signature_override` is set when
   `validate=True`. This is correct but relies on the conditional at line 1822
   checking `reference_signature_override is not None` first. The logic is sound;
   a future reviewer adding modes should be aware of this ordering.

2. **`component_signature_sec` timing** (`app:1191`): This measures wall time for
   the entire `build_v2_8_...` call including first-run JIT. The smoke value
   (0.507s) is dominated by JIT and not a steady-state figure. The metadata does
   not claim it is. No issue.

3. **README entry** (`README.md:37–38`): The table entry correctly states "no
   Python rows, no full DBSCAN semantics, no RT cores" inline. This is
   appropriately concise for the README format.

---

## Verdict

**accept**

Goal4047 is a clean, narrow surface-exposure step. The new app mode correctly
delegates to the Goal4045/4046 primitive, records the fixed-radius graph-component
contract consistently, preserves all claim boundaries, does not touch any promoted
route, and has focused tests that cover the no-row guard, the generic payload
helper, the pod-smoke boundary, and the end-to-end CuPy path. The pod smoke is
sufficient given this goal's scope.
