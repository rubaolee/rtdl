# Goal 709: Embree Threading Configuration And Dispatch Contract

Date: 2026-04-21
Status: accepted by Codex, Claude, and Gemini Flash

## Purpose

Goal709 creates the public and internal contract required before native Embree
parallel dispatch is implemented in Goal710.

This goal does not yet parallelize native kernels. It defines how users and
apps configure Embree threading, how tests observe the effective configuration,
and how native Goal710 kernels must partition and merge work.

## User-Facing Configuration

RTDL now exposes:

- `rt.configure_embree(threads=...)`
- `rt.embree_thread_config()`
- `rt.EmbreeThreadConfig`

Environment variable:

- `RTDL_EMBREE_THREADS=<N|auto|1>`

Rules:

- Default is `auto`.
- `auto` maps to `max(1, os.cpu_count() or 1)`.
- A positive integer selects that thread count.
- `0`, negative values, and arbitrary strings fail clearly.
- API override wins over environment until cleared with
  `rt.configure_embree(threads=None)`.

The returned config records:

- requested value;
- effective thread count;
- source: `default`, `env`, or `api`;
- whether the value is auto-derived.

## Native Dispatch Contract For Goal710

Native parallel Embree kernels must follow this contract:

- Partition independent query units into contiguous index ranges.
- Use one range per worker thread.
- Do not use work-stealing for the first implementation.
- Accumulate per-worker output into thread-local vectors.
- Merge output vectors in ascending worker/range order.
- Treat committed Embree scenes as read-only during dispatch.
- Move RTDL-owned mutable callback state to thread-local or per-task scope
  before declaring a kernel parallel-safe.
- Preserve row ordering and exact parity against CPU reference and single-thread
  Embree execution.

## First Goal710 Target

Start with fixed-radius/KNN point-query families:

- `rtdl_embree_run_fixed_radius_neighbors`
- `rtdl_embree_run_fixed_radius_neighbors_3d`
- `rtdl_embree_run_knn_rows`
- `rtdl_embree_run_knn_rows_3d`

Reason:

- they cover the most apps;
- they force the hardest common output problem, deterministic variable-length
  row merging;
- ray-query kernels can reuse the same partition/merge structure afterward.

## Boundary

Goal709 is not a speedup claim. It is the configuration and dispatch-contract
foundation for Goal710.

## Review And Verification

- Claude Sonnet 4.6 review:
  `docs/reports/goal709_claude_review_2026-04-21.md`, verdict ACCEPT.
- Gemini 2.5 Flash review:
  `docs/reports/goal709_gemini_flash_review_2026-04-21.md`, verdict ACCEPT.
- Codex consensus closure:
  `docs/reports/goal709_codex_consensus_closure_2026-04-21.md`, verdict
  ACCEPT.

Focused verification passed:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal708_v1_0_plan_test tests.goal709_embree_threading_contract_test
python3 -m py_compile tests/goal708_v1_0_plan_test.py tests/goal709_embree_threading_contract_test.py src/rtdsl/embree_runtime.py src/rtdsl/__init__.py
git diff --check
```
