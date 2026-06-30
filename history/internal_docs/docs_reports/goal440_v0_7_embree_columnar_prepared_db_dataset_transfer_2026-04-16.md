# Goal 440: v0.7 Embree Columnar Prepared DB Dataset Transfer

Date: 2026-04-16

## Verdict

Goal 440 is implemented and ready for external review.

This goal adds the first native columnar prepared DB dataset transfer path, bounded to Embree. The existing row-struct compatibility transfer remains intact, and the new path is opt-in through `transfer="columnar"`.

## Implemented Surface

Native Embree ABI:

- `RtdlDbColumn`
- `rtdl_embree_db_dataset_create_columnar`

Python API:

```python
rt.prepare_embree_db_dataset(table_rows, primary_fields=(...), transfer="columnar")
```

Compatibility path remains:

```python
rt.prepare_embree_db_dataset(table_rows, primary_fields=(...), transfer="row")
```

The default remains `transfer="row"` so existing callers are not changed.

## Correctness Evidence

Local macOS:

```text
python3 -m py_compile src/rtdsl/embree_runtime.py tests/goal440_v0_7_embree_columnar_prepared_db_dataset_transfer_test.py scripts/goal440_embree_columnar_transfer_perf_gate.py
PYTHONPATH=src:. python3 -m unittest tests.goal440_v0_7_embree_columnar_prepared_db_dataset_transfer_test -v
Ran 4 tests
OK
```

Linux `lestat-lx1`:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal440_v0_7_embree_columnar_prepared_db_dataset_transfer_test -v
Ran 4 tests
OK
```

The test suite verifies row-transfer, columnar-transfer, and Python-truth parity for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

It also verifies invalid transfer mode rejection.

## Linux Prepare-Time Gate

Command:

```text
PYTHONPATH=src:. python3 scripts/goal440_embree_columnar_transfer_perf_gate.py --row-count 200000 --repeats 5
```

Raw JSON:

```text
/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal440_embree_columnar_transfer_perf_linux_2026-04-16.json
```

| Workload | Row-transfer median prepare | Columnar-transfer median prepare | Columnar speedup |
|---|---:|---:|---:|
| `conjunctive_scan` | 2.655424 s | 0.816905 s | 3.25x |
| `grouped_count` | 2.596275 s | 0.811773 s | 3.20x |
| `grouped_sum` | 2.526056 s | 0.804545 s | 3.14x |

The row hashes match the existing DB truth hashes:

- `conjunctive_scan`: `19461bddd250025c3d24a174f82e5f66046e40dded85ef27614143a08c9590c8`
- `grouped_count`: `869ed487d7eda66115bb00dceaf75df016fac2e2e0a6d75119f993d63137a77b`
- `grouped_sum`: `123b2f6fc6fa9f69e2df8da24441116549271314ef3b602482467c6ad47ed330`

## Interpretation

This closes the first concrete step toward removing the compatibility row-ingestion caveat. It does not yet close that caveat for all backends.

The justified claim is:

- Embree now has a native columnar prepared DB dataset creation path.
- The path preserves correctness for the bounded DB family.
- On the Linux 200k-row prepare gate, columnar transfer reduces Embree prepare time by about 3.1x to 3.25x against the row-struct transfer path.

The excluded claims are:

- OptiX and Vulkan columnar transfer are not implemented yet.
- RTDL is still not a DBMS.
- This does not add arbitrary SQL support.
- This does not by itself prove final large-table ingestion across every backend.

## Follow-Up

Next reasonable goals:

- add the same columnar prepared DB dataset transfer ABI to OptiX
- add the same columnar prepared DB dataset transfer ABI to Vulkan
- refresh the cross-backend repeated-query gate after all three RT backends use columnar transfer
