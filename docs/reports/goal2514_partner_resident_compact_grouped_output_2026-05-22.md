# Goal2514 Partner-Resident Compact Grouped Output

Date: 2026-05-22

## Summary

Goal2514 completes the compact-output half of the Goal2513 capacity work. The
experimental OptiX partner-resident grouped-i64 path no longer downloads the
capacity-sized `group_counts` or `group_sums` workspaces to host. Instead, it
launches a device compaction kernel that emits only non-empty grouped rows, then
downloads those compact rows.

## Native Change

The OptiX CUDA module now contains:

- `device_column_grouped_i64_compact_count_kernel`
- `device_column_grouped_i64_compact_sum_kernel`

The execution shape is:

```text
partner CUDA columns
-> device predicate/grouped-reduction kernel
-> device compact grouped-output kernel
-> host download of compact grouped rows only
```

The dense workspace still exists on device and is bounded by explicit
`group_capacity`. The host no longer materializes capacity-sized intermediate
arrays.

## Claim Boundary

Allowed internal wording:

- The experimental partner-resident grouped-i64 path downloads compact grouped
  rows, not full capacity-sized count/sum arrays.

Blocked wording:

- true zero-copy claim;
- arbitrary sparse/hash group-key support;
- SQL or DBMS support;
- public speedup claim;
- whole-app acceleration claim.

## Tests

Focused local validation:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2514_partner_resident_compact_grouped_output_test
```

Expected result:

```text
5 tests OK
```

RayDB-style local sequence through Goal2514:

```text
117 tests OK, 4 skipped
```

## Pod Evidence

Pod SSH used:

```text
ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519_rtdl_codex -p 22017 root@69.30.85.198
```

Build evidence:

- remote checkout: `/root/rtdl_python_only_goal2501`
- OptiX headers: `/root/vendor/optix-dev-9.0.0`
- CUDA prefix: `/usr/local/cuda`
- build log: `docs/reports/goal2514_make_build_optix_2026-05-22.txt`
- result: `make build-optix` completed successfully with only the CUDA
  deprecated-target warning.

The pod runner is:

```text
scripts/goal2514_partner_resident_compact_output_pod.py
```

Expected artifact:

```text
docs/reports/goal2514_partner_resident_compact_output_pod_2026-05-22.json
```

Observed artifact summary:

- status: `ok`
- compact_output_source_check: `true`
- group_capacity: `3`
- count_rows_downloaded: `3`
- sum_rows_downloaded: `3`
- all_match_cpu_reference: `true`

The source check asserts both compact kernels exist and that the current source
does not contain host downloads of `group_counts` or `group_sums` arrays.

Pod-focused unittest validation after syncing the final source/report/test
slice:

```text
22 tests OK
```
