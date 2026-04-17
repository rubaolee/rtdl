# Goal 432 External Review

Date: 2026-04-15
Reviewer: Claude Sonnet 4.6 (second-AI consensus slot)

---

## Summary finding

The two-phase RTDL vs PostgreSQL comparison is now technically honest, and no material overclaim remains.

---

## What was verified

### Phase-split implementation (db_perf.py `measure_backend_family_split`)

The harness correctly separates RTDL timing into three measurements on every repeat:

- `prepare`: calls `backend_preparer(kernel_fn).bind(**inputs)` — normalises Python-side inputs and constructs ctypes arrays for the backend call, resolves the C symbol
- `execute`: calls `prepared.run()` — dispatches into the C backend (BVH construction + scan/traversal happen here)
- `total`: wall-clock from before prepare through the end of execute

The timer placement is correct: `total_start` precedes `prepare_start`, `execute_start` is placed after bind returns, and `total_elapsed` is taken after execute completes. No double-counting or gap exists.

### Prepared-execution paths (embree, optix, vulkan runtimes)

All three backends implement `PreparedXxxDbExecution` as a frozen dataclass that captures pre-encoded ctypes arrays and a resolved C symbol. The `run()` method on each dispatches a single C call. This matches the stated definition of the prepare/execute split.

One technical nuance: the "prepare" phase in the Python layer does not call the C backend library at all — it only performs Python-side data encoding. The actual RT/BVH work (BVH construction + traversal) happens entirely in execute. This means the ~2.5 s prepare figure measures Python ctypes marshaling overhead for 200 k rows, not RT build time. This framing is not an overclaim — it is an accurate representation of where the Python overhead lives.

### Raw data consistency (artifact JSON)

There are first-call warmup outliers visible in the raw samples for OptiX and Vulkan execute on `conjunctive_scan`:

- OptiX execute samples: `[0.642s, 0.059s, 0.068s]` → median 0.068 s (warm GPU)
- Vulkan execute samples: `[0.525s, 0.076s, 0.064s]` → median 0.076 s (warm GPU)

Using medians correctly filters these. The warmup effect does not create an overclaim: even the warm-GPU execute medians (0.04–0.09 s) are still slower than PostgreSQL query (0.02–0.036 s), so the "RTDL execute does not beat PostgreSQL query" conclusion is conservative, not inflated.

PostgreSQL setup and query samples are tight (setup: 10.02–10.20 s; query: 0.021–0.036 s) with no anomalous outliers.

### Report interpretation

The clarification report explicitly states:

- RTDL total (~2.5–3.1 s) beats fresh PostgreSQL total (~10.0–10.2 s) in this harness — correct per the data.
- RTDL execute (~0.04–0.09 s) does **not** beat warm-query PostgreSQL (~0.02–0.036 s) — correct and appropriately stated as a loss.
- "RTDL is not a warm-query PostgreSQL winner" — explicitly called out.
- "RTDL is competitive only under the fresh-build one-shot reading in this bounded first-wave harness" — well-scoped.

No clause in the report asserts general database competitiveness or warm-query superiority. The bounded scope is maintained throughout.

---

## Minor observations (non-blocking)

1. The report could note that prepare time is dominated by Python-side ctypes marshaling rather than RT/BVH build. This would improve reader understanding of where RTDL optimisation headroom exists. It does not change the performance conclusion.

2. The warmup outliers in execute samples are worth a parenthetical mention in the report. Again, this does not change any stated conclusion.

Neither observation constitutes a material overclaim.

---

## Verdict

The two-phase RTDL vs PostgreSQL comparison is technically honest. No material overclaim remains. The comparison now correctly exposes that RTDL's total-time advantage over PostgreSQL comes from the fresh-setup cost of PostgreSQL, and that in the execute-vs-query dimension RTDL currently loses. The harness, runtime code, and report are consistent with one another.

**ACCEPT**
