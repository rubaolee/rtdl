# Goal 442: v0.7 Vulkan Columnar Prepared DB Dataset Transfer

Date: 2026-04-16

## Verdict

Goal 442 is implemented and ready for external review.

This goal adds the native columnar prepared DB dataset transfer path to the
Vulkan backend. The existing row-struct compatibility transfer remains intact,
and the new path is opt-in through `transfer="columnar"`.

## Implemented Surface

Native Vulkan ABI:

- `RtdlDbColumn`
- `rtdl_vulkan_db_dataset_create_columnar`

Python API:

```python
rt.prepare_vulkan_db_dataset(table_rows, primary_fields=(...), transfer="columnar")
```

Compatibility path remains:

```python
rt.prepare_vulkan_db_dataset(table_rows, primary_fields=(...), transfer="row")
```

The default remains `transfer="row"` so existing callers are not changed.

## Correctness Evidence

Local macOS syntax gate:

```text
python3 -m py_compile src/rtdsl/vulkan_runtime.py tests/goal442_v0_7_vulkan_columnar_prepared_db_dataset_transfer_test.py scripts/goal442_vulkan_columnar_transfer_perf_gate.py
```

Linux `lestat-lx1` native rebuild:

```text
make build-vulkan
```

Linux `lestat-lx1` correctness gate:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal442_v0_7_vulkan_columnar_prepared_db_dataset_transfer_test -v
Ran 4 tests
OK
```

The test suite verifies row-transfer, columnar-transfer, and Python-truth parity
for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

It also verifies invalid transfer mode rejection.

## Linux Prepare-Time Gate

Command:

```text
PYTHONPATH=src:. python3 scripts/goal442_vulkan_columnar_transfer_perf_gate.py --row-count 200000 --repeats 5
```

Raw JSON:

```text
/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal442_vulkan_columnar_transfer_perf_linux_2026-04-16.json
```

| Workload | Row-transfer median prepare | Columnar-transfer median prepare | Columnar speedup |
|---|---:|---:|---:|
| `conjunctive_scan` | 2.761299 s | 0.820684 s | 3.36x |
| `grouped_count` | 2.707589 s | 0.846077 s | 3.20x |
| `grouped_sum` | 2.623332 s | 0.852379 s | 3.08x |

The row hashes match the existing DB truth hashes:

- `conjunctive_scan`: `19461bddd250025c3d24a174f82e5f66046e40dded85ef27614143a08c9590c8`
- `grouped_count`: `869ed487d7eda66115bb00dceaf75df016fac2e2e0a6d75119f993d63137a77b`
- `grouped_sum`: `123b2f6fc6fa9f69e2df8da24441116549271314ef3b602482467c6ad47ed330`

## Interpretation

This closes the Vulkan part of the compatibility row-ingestion caveat. Together
with Goals 440 and 441, the three RT backends now have native columnar prepared
DB dataset transfer paths while preserving the row-transfer ABI.

The justified claim is:

- Vulkan now has a native columnar prepared DB dataset creation path.
- The path preserves correctness for the bounded DB family.
- On the Linux 200k-row prepare gate, columnar transfer reduces Vulkan prepare
  time by about 3.08x to 3.36x against the row-struct transfer path.

The excluded claims are:

- RTDL is still not a DBMS.
- This does not add arbitrary SQL support.
- This does not by itself claim PostgreSQL-level indexing or query planning.

## Follow-Up

Next reasonable goal:

- refresh the cross-backend repeated-query gate after Embree, OptiX, and Vulkan
  all use columnar prepared dataset transfer
