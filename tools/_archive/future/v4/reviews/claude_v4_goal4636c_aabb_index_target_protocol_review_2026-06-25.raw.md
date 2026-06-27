## Review: V4 Goal4636C AABB Index Target Protocol

**Verdict: `approve_with_required_amendments`**

---

### What is sound

**Operator name is genuinely generic.** `aabb_index_query_2d_all_ops_count` and `AABB_INDEX_QUERY_2D` contain no LibRTS-specific tokens. The coverage row `librts_spatial_index` is where the benchmark identity lives; the primitive and operator names are app-agnostic. This distinction is correctly maintained throughout.

**Scope declaration is honest.** Both backends use `prepared_execution_session_runner` as their `productized_execution_path` — Embree via `rt.run_aabb_index_query_2d_count_prepared_session`, OptiX via `rt.run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session`. The `rtdl_native_prepared_runner` scope is truthful.

**Non-authorization language is comprehensive.** All seven prohibited flags are `False` in the dataclass, verified by `validate_v4_goal4636_aabb_index_target`, tested in `test_target_preserves_non_authorization_boundaries`, and echoed in the runner's `claim_boundary` dict. The benchmark app repeats `authors_code_comparison: False` and `paper_reproduction: False` in every return path.

**Goal continuation is reasonable.** After threshold-summary (no-regression floor failure) and grouped-any-hit (wrapper-wall failure), pivoting to a different geometric class that has an existing runner and needs no CuPy is a proper selection step.

**Front-door/catalog gating boundary is correct.** Requiring a separate front-door goal after POD prevents premature public catalog promotion. The test confirms `aabb_index_query_2d_all_ops_count` is absent from `V4_TIER2_OPERATOR_SURFACES` pre-gate.

---

### Required Amendment 1 — Contract name mismatch will crash the gate

`scripts/v3_0_m30_librts_prepared_all_ops_refresh.py:22`:
```python
EXPECTED_CONTRACT = "generic_prepared_aabb_index_query_2d"
```

`examples/.../rtdl_librts_spatial_index_benchmark_app.py:506` (new prepared runner branch, `prepared_queries=True`):
```python
"primitive_contract": "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
```

`_compare_rows` (line 246–249) enforces `row["primitive_contract"] == EXPECTED_CONTRACT` for all rows, then the runner raises `RuntimeError("contract mismatch")` if `all_same_contract` is False. Since the OptiX new-runner path returns the longer contract string, the gate run will always error immediately on contract check — before any timing metrics are evaluated.

The protocol document requires both backends to share `generic_prepared_aabb_index_query_2d`. The code does not enforce this — it produces `generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count` for OptiX. **One of these must change:** either normalize the OptiX return value to the shorter string, or update `EXPECTED_CONTRACT` and the protocol to accept the qualified name and document the distinction.

---

### Required Amendment 2 — The two "10x floors" are not equivalent

The gate declares:
- `embree_over_optix_query_median >= 10.0x`
- `embree_query_total_sec / optix_query_total_sec >= 10.0x`

But `query_total_sec` is the **sum across all repeats** — Embree runs 240 repeats, OptiX 3,200. Therefore:

```
embree_total / optix_total
  = (embree_per_query × 240) / (optix_per_query × 3200)
  = (embree_over_optix_median) × (240/3200)
  = (embree_over_optix_median) × 0.075
```

To satisfy the total floor at 10x while running these repeat counts, the per-query speedup must be **≥ 133x**, not ≥ 10x. The two floors are not independent corroborating checks — they impose wildly different requirements. If 133x per-query speedup is genuinely expected for 1M-box AABB traversal on RT hardware, the protocol should say so explicitly ("the expected per-query ratio is ~100-200x; the 10x total floor is set conservatively below that"). If 133x is not guaranteed, the total floor is unachievable and the gate is broken.

**Required:** either document the implied 133x per-query assumption, or rebalance the repeat counts to be symmetric (e.g., both at 240 or both at 3200) so the two 10x floors mean the same thing.

---

### Moderate observation — CPU reference is skipped for correctness

The gate command omits `--validate-cpu-reference`. Cross-backend count matching (Embree vs OptiX agree on counts) is the sole correctness signal. For 1M boxes, O(n×m) CPU oracle is impractical, so this is a reasonable trade-off — but the protocol should acknowledge it explicitly rather than leaving `cpu_reference_skipped: True` as a silent output field.

---

### Minor observation — Warmup depth for OptiX

`--warmup 1` is declared but CUDA/OptiX JIT and BVH construction happen in the `prepare` phase, which is already separated from the query phase in the prepared-runner pattern. Single query-phase warmup is likely adequate. No amendment needed — worth confirming on first gate run.

---

### Summary of required amendments

| # | Location | Issue |
|---|---|---|
| 1 | `benchmark_app.py:506` or `runner.py:22` | Contract string mismatch causes gate RuntimeError; must align before gate can run |
| 2 | protocol doc + gate parameters | "10x total" floor implicitly requires ~133x per-query speedup given repeat asymmetry; must document or fix |

The structural design — generic primitive, honest scope, hard non-authorization boundaries, staged catalog promotion — is appropriate for a V4 POD gate. The two amendments above are blocking: one is a crash-on-run bug, the other is a silent geometric trap that would either make the gate unpassable or mislead the reader about what is actually being measured.
