# Goal1690 Apple RT BFS-To-Frontier-Discover Native Migration

Date: 2026-05-11

Status: sixth local source migration from app-shaped native terminology to
generic primitive terminology; completes the remaining Apple RT slice of the
`frontier_edge_traversal` family classified by Goal1672.

## Verdict

BFS family is now zero in the strict real native app-shaped symbol scan.

Goal1690 migrated the two Apple RT discover names that Goal1688 deliberately
deferred:

| Old native name | New native name |
| --- | --- |
| `rtdl_apple_rt_run_bfs_discover_compute` | `rtdl_apple_rt_run_frontier_discover_compute` |
| `rtdl_bfs_discover` | `rtdl_frontier_discover` |

The first symbol is the exported Apple RT compute entry point. The second is
the embedded Metal kernel function name compiled through `MTLLibrary` and
looked up with `newFunctionWithName`.

This is a local source migration only. It does not claim new performance
evidence, because no pod was used and no Apple Metal hardware validation was
run for this local slice.

## Compatibility Boundary

Python-facing BFS semantics remain in Python:

- `bfs_discover_apple_rt` remains the public Python helper;
- the `"bfs_discover"` predicate remains in the Apple RT Python dispatcher;
- `run_apple_rt` still routes the BFS predicate to `bfs_discover_apple_rt`;
- only the ctypes native binding string changed to
  `rtdl_apple_rt_run_frontier_discover_compute`;
- the Metal kernel source and lookup site now use `rtdl_frontier_discover`.

The native ABI now describes generic frontier discovery, while graph/BFS meaning
stays at the Python expression layer.

`_run_frontier_discover_compute` is present in
`_GENERIC_NATIVE_SYMBOL_FRAGMENTS` so the purity audit classifies the renamed
entry point as generic. `_run_bfs` remains in app-shaped fragments as a guard
against reintroducing app-shaped native ABI names.

## Counts Delta

Before Goal1690 (post-Goal1688):

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 84 |
| Strict regex occurrences | 164 |
| Remaining app-shaped callable/export symbols | 75 |
| `bfs` family unique symbols | 2 |

After Goal1690:

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 82 |
| Strict regex occurrences | 159 |
| Known uppercase `RTDL_DB_*` constant false-positive symbols | 9 |
| Known uppercase `RTDL_DB_*` constant false-positive occurrences | 14 |
| Remaining app-shaped callable/export symbols | 73 |
| `bfs` family unique symbols | 0 |

Remaining real app-shaped native callable/export families:

| Family term | Unique symbols |
| --- | ---: |
| `db` | 30 |
| `polygon` | 29 |
| `knn` | 14 |

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src'
py -3 -m unittest tests.goal1690_apple_rt_bfs_to_frontier_discover_migration_test
```

No pod validation was run. Native rebuild and runtime validation on Apple
Metal hardware remain future evidence, not a claim made by this report.

## Blocked Wording

Still blocked:

```text
RTDL native internals are fully app-agnostic.
```

Allowed wording after Goal1690:

```text
RTDL has migrated the BFS-shaped native callable/export family to generic
frontier traversal and frontier discovery native terminology. Remaining
app-shaped native families (`db`, `polygon`, and `knn`) still block the full
app-agnostic native-engine release claim.
```

