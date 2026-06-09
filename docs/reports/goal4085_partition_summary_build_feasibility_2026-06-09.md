# Goal4085 Partition-Summary Build Feasibility

Date: 2026-06-09

## Verdict

`accept-with-boundary`

Goal4085 measures one of the acceptance bars added by the Goal4081 Claude
review and Goal4084 intake: partition-build overhead. The result is constructive
but blocking for a naive implementation. The current CuPy preview partition
summary is useful evidence, but its build cost is already too high to become the
production route.

## Pod Evidence

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05.

Source commit: `0c1a717f`.

Artifacts:

- `docs/reports/goal4085_partition_summary_build_feasibility_pod.json`
- `docs/reports/goal4085_partition_summary_build_feasibility_pod.stdout.txt`

Command shape:

```bash
python3 scripts/goal4085_partition_summary_build_feasibility.py \
  --repeat 3 \
  --warmup 1 \
  --point-count 65536 \
  --output docs/reports/goal4085_partition_summary_build_feasibility_pod.json
```

The runner times only:

`build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(...)`

with `pair_enumeration=device_count_then_emit`, `cell_factor=0.125`, and the
current benchmark radius for each profile.

## Results

| Profile | Radius | Partition build median sec | Partitions | Partition pairs | Safe-full pairs | Ambiguous pairs | Safe-skip pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 0.055 | 0.219861 | 16,772 | 19,668,778 | 7,338,133 | 3,622,448 | 8,708,197 |
| `road3d` | 0.030 | 0.201510 | 18,028 | 10,271,711 | 5,092,654 | 1,737,708 | 3,441,349 |
| `ngsim_dense` | 0.012 | 0.367637 | 60,094 | 30,525,629 | 9,203,113 | 2,382,110 | 18,940,406 |

The partition signal remains real:

- clustered has 7.34M safe-full partition pairs and 3.62M ambiguous pairs;
- road has 5.09M safe-full partition pairs and 1.74M ambiguous pairs;
- ngsim has 9.20M safe-full partition pairs and only 2.38M ambiguous pairs.

But the build cost is too large. Goal4074 measured the current production
recommended route at roughly 0.093s for clustered and 0.036s for road. The
current partition-summary builder alone costs about 0.220s and 0.202s
respectively before any component union, signature, or ambiguous traversal is
run.

## Feasibility Conclusion

The Goal4080 candidate remains strategically plausible, but the implementation
must not be a thin wrapper around the current CuPy preview summary builder.

The next native/runtime implementation must satisfy at least one of these:

1. **Prepared-reuse route:** amortize the partition summary across many
   repeated component/signature runs, with the build cost reported separately.
2. **Cheaper native producer:** replace the current sort/unique + exact-count
   CuPy preview path with a lower-overhead device/native partition producer.
3. **Fused native route:** build only the partition metadata actually needed by
   the grouped-union continuation, avoiding full visible pair materialization
   when the candidate only needs safe-full and ambiguous work streams.

The existing OptiX grouped-union API has contiguous query-range entry points,
but it does not consume partition-pair ranges. Therefore partition-aware
execution requires a new generic parameter/launch shape; blocked query ranges
are not enough.

## Next Engineering Gate

Before implementing a promoted candidate, require:

- `partition_summary_build_sec` below the current recommended route budget, or
  explicit prepared-summary amortization evidence;
- no `ngsim_dense_65536` regression;
- at least 50% lower candidate hits or root calls than Goal4079 on claimed
  profiles;
- production timing with repeat/warmup comparable to Goal4074.

## Boundary

This is feasibility evidence only. It does not promote
`partition_convergence_hybrid`, add a native ABI, authorize release wording,
public speedup wording, broad RT-core wording, whole-app acceleration wording,
paper-reproduction wording, hidden dispatch, automatic partner selection,
app-specific native-engine logic, or true-zero-copy wording.
