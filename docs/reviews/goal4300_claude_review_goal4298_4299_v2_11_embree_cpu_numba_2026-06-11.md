# Review: Goal4298/Goal4299 v2.11 Embree CPU + Numba Reference Path

**Reviewer:** Claude (independent read-only review)
**Date:** 2026-06-11
**Verdict:** `accept-with-boundary`

---

## Files Reviewed

- `src/rtdsl/current_embree_cpu_partner_reference.py`
- `scripts/rtdl_v2_11_embree_cpu_partner_reference_runner.py`
- `src/rtdsl/partner_adapters.py` (Numba branch of `top_k_nearest_points_2d_partner_columns`)
- `examples/current/apps/ml/rtdl_ann_candidate_app.py`
- `docs/reports/goal4298_v2_11_embree_cpu_partner_reference_packet_2026-06-11.md`
- `docs/reports/goal4298_v2_11_embree_cpu_partner_reference_local_linux.json`
- `docs/reports/goal4299_numba_topk_partner_reference_for_v2_11_embree_cpu_packet_2026-06-11.md`
- `tests/goal4298_v2_11_embree_cpu_partner_reference_packet_test.py`
- `tests/goal4299_numba_topk_partner_reference_test.py`

---

## Scope Verification

### Registry coverage

`CURRENT_EMBREE_CPU_PARTNER_REFERENCE_ROWS` contains exactly ten entries — one per app — matching `V2_8_PROMOTED_BENCHMARK_APPS`. All ten `row_id` values are distinct. The `__post_init__` guard enforces this at import time by checking membership against the canonical app tuple and rejecting unknown apps. The runtime `validate_current_embree_cpu_partner_reference` function independently re-checks the same set coverage, uniqueness of row_ids, and structural constraints. Both the test and the local Linux artifact confirm `validation.status == "accept"` and `validation.errors == []`.

### Embree/Numba split

Nine apps use `uses_embree=True` and `requires_embree_library=True`. The RTNN row is the single exception:

```
route_class: numba_cpu_partner_reference_no_embree_front_door
uses_embree: False, requires_embree_library: False
uses_numba: True, requires_numba: True
```

The `__post_init__` guard explicitly enforces that only `rtnn` may have `uses_embree=False`, and that it must use Numba. The `validate_*` function mirrors this with an explicit per-app check (line 431-437). The registry and tests are consistent with each other and with the report.

No command in the registry routes through OptiX, CuPy, or `--require-rt-core`. Both the registry validator and the test confirm this by scanning command text.

### Runner behavior

`_cpu_thread_env` sets all six required thread env vars: `OMP_NUM_THREADS`, `TBB_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `NUMEXPR_NUM_THREADS`, and `RTDL_EMBREE_THREADS`. Per-row progress is printed to stdout before and after each row via `flush=True` calls, which prevents silent hangs. `--only` filters by app name or row_id, enabling resumable runs. The runner uses the current Python executable by default (`sys.executable`) rather than the literal `python` string.

The runner fails closed on claim-boundary violations via `_semantic_stdout_check`, which recursively walks the parsed stdout JSON looking for any key in `FORBIDDEN_TRUE_FLAGS` set to `True`. The forbidden list includes version-specific flags such as `v2_11_release_authorized` and all prior-version equivalents. If stdout JSON is unparseable, status is forced to `fail`. If returncode is non-zero, status is `fail` regardless of JSON content. This combination is correct and conservative.

### Local Linux artifact

`all_pass: true`, `dry_run: false`, `validation.status: "accept"`, `validation.errors: []`. All ten rows have `status: "pass"`. All top-level claim flags are `false`. The `v2_11_release_authorized` flag is explicitly present and `false`. The `summary.row_count` and `len(rows)` are both 10.

The RTNN row artifact confirms the Numba reference path was exercised:
- `route_class: numba_cpu_partner_reference_no_embree_front_door`
- `elapsed_sec: 1.31s`
- `stdout_tail` contains `"v2_11_numba_preview_kernel_status": "reference_host_rank_after_device_score_rows"`, `"host_rank_materialization_used": null` is absent (the field is present as `True`), and `whole_app_speedup_claim_authorized: false`.

---

## Question-by-Question Assessment

### Q1: Is the Embree CPU + Numba reference path correctly scoped for v2.11?

Yes. The packet is explicitly positioned as a compatibility and coverage reference, not a performance milestone. The claim boundary string is embedded in the module-level constant, the runner output, and all row metadata. No row authorizes release, public speedup, RT-core performance, Intel GPU performance, or zero-copy semantics. The scope is consistent across the code, the reports, and the tests.

### Q2: Is the RTNN Numba path honest enough as a reference path?

Yes. The path is transparently labeled at every layer:

- `route_class: numba_cpu_partner_reference_no_embree_front_door` (registry)
- `v2_11_numba_preview_kernel_status: reference_host_rank_after_device_score_rows` (metadata)
- `host_rank_materialization_used: True` (metadata)
- `host_rank_materialization_reason` string identifies the missing `grouped_topk_f64` device kernel as v2.11 debt
- The report section "Why This Is Still Useful" and "Boundary" describe the limitation and the future direction

Host-side top-k ranking after device-side pairwise scoring is a correct approach for a reference path. The device score rows are generated on the Numba partner device; only the sort is done on the host. This is a known and explicitly declared limitation, not a hidden shortcut.

### Q3: Do any names, docs, metadata, or tests overclaim performance, release readiness, zero-copy, or RT-core acceleration?

No overclaims found. The status constant is `internal_embree_cpu_partner_reference_not_release_authorization`. The report explicitly states this packet does not authorize any of the named claim categories. No row sets `rt_core_accelerated: True`. The RTNN artifact stdout shows `rt_core_accelerated: false`. The test suite checks all nine claim-boundary flags on every row and on the runner output.

One observation: `triangle_counting_embree_cpu_native_summary` stdout contains `ray_tracing_accelerated: true` and a note that Embree uses ray traversal. This is accurate description of Embree CPU ray traversal, not an RT-core claim, and `rt_core_accelerated: false` is separately confirmed. No overclaim here.

### Q4: Are there any correctness risks in the Numba top-k deterministic ordering or ANN output conversion?

**Tie-breaking is consistent.** The Numba path sorts by `(score, item_id)` where `item_id` is the actual candidate point ID. The Torch and CuPy paths sort candidates by ID first (`argsort(candidate_ids_i64)`) and then apply `stable` argsort on distances — effectively the same tie-break. The metadata field `"tie_break": "distance_then_candidate_id"` correctly documents this. The test case deliberately exercises ties (two candidates at distance 1.0 from each query) and passes.

**Group-index contract.** The Numba host-rank loop uses `host_group_ids == group_index` where `group_index` is a 0-based query position index, then looks up the actual query ID via `host_query_ids[group_index]`. This relies on `pairwise_l2_sq_score_rows_2d_partner_columns` returning `group_ids` as 0-based positional indices (not query point IDs). The test case uses query IDs 100 and 101 (not 0 and 1), and the test passes, confirming this contract holds. The coupling is implicit, not documented in the function signature, but the test validates it.

**ANN app output conversion.** The `_partner_column_to_list` function adds `if partner == "numba": return column.copy_to_host().tolist()`. This is correct: `copy_to_host()` moves the Numba device array to a NumPy array, and `.tolist()` converts it to a Python list. The branch is structurally identical to the CuPy branch (`cupy.asnumpy(column).tolist()`).

**Minor: `--partner` CLI choices in the ANN app.** The `run_app` function supports `partner="numba"` programmatically via the `_run_partner_exact_quality` path, but the CLI `--partner` argument (line 498) still lists only `choices=("torch", "cupy")`. The Numba branch in `_partner_column_to_list` is therefore unreachable from the ANN app's CLI. This is not a correctness bug — the RTNN benchmark row uses the RTNN app, not the ANN app — but it means the ANN app carries a Numba output conversion branch that can only be triggered programmatically. The test confirms the branch is present in source text, not that it is CLI-accessible. This is low risk but worth a follow-up comment if the ANN app is ever expected to expose `--partner numba` directly.

---

## Summary of Findings

| Item | Status |
|---|---|
| Registry: 10 apps, exactly once | Pass |
| Nine Embree rows, one Numba row (RTNN) | Pass |
| RTNN labeled as no-Embree-front-door explicitly | Pass |
| Runner sets 6 CPU thread env vars | Pass |
| Runner prints per-row progress | Pass |
| Runner supports `--only` for resumability | Pass |
| Runner fails closed on claim-boundary flags | Pass |
| Local Linux artifact: `all_pass: true`, 10/10 pass | Pass |
| Claim-boundary flags: all false, all layers | Pass |
| Numba top-k is generic (not RTNN-specific) | Pass |
| Host materialization explicitly declared as debt | Pass |
| Tie-breaking deterministic and consistent | Pass |
| ANN app change: output conversion only | Pass |
| ANN app CLI choices do not include `numba` | Minor observation (not blocking) |
| Group-index contract implicitly assumed | Minor observation (not blocking) |

---

## Verdict: `accept-with-boundary`

The work is correctly scoped as a v2.11 CPU/Embree compatibility and current-partner reference packet. All structural and semantic claim-boundary enforcements are in place. The RTNN Numba path is honest about host materialization and labeled as reference debt. The local Linux artifact provides complete pass evidence. No overclaims are present in names, docs, metadata, or tests.

The `accept-with-boundary` designation reflects:

1. The RTNN Numba path remains explicitly a reference path (`host_rank_materialization_used: True`). The Numba grouped top-k device kernel is not implemented; host-side ranking is declared debt. This is correctly labeled but is not yet resolved.
2. The ANN app's `--partner` CLI choices do not include `numba`, leaving the `_partner_column_to_list` Numba branch unreachable from the CLI. This does not affect the RTNN row but is an inconsistency worth noting before this path is relied upon more broadly.

Neither observation blocks acceptance of this packet as v2.11 internal Embree CPU plus CPU partner reference evidence. Neither constitutes an overclaim. Both are visible and labeled in the work itself.
