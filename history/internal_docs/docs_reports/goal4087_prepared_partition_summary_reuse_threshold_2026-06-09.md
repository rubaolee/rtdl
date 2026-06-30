# Goal4087 Prepared Partition-Summary Reuse Threshold

Date: 2026-06-09

## Verdict

`accept-with-boundary`

Goal4087 measures whether the existing explicit prepared CuPy partition-summary
preview can become useful through repeated reuse at the current 65K RT-DBSCAN
profiles. The answer is mixed and policy-relevant:

- clustered reuse can pay off only after roughly 12 repeated component-signature
  queries over the same prepared summary;
- road-shaped reuse does not break even because replay alone is slower than the
  current recommended RTDL/OptiX grouped-stream plus Numba route.

Therefore prepared partition-summary reuse remains a user-selected repeated-run
preview, not a default route and not the next primary performance direction.

## Pod Evidence

Artifacts:

- `docs/reports/goal4087_prepared_partition_summary_reuse_threshold_pod.json`
- `docs/reports/goal4087_prepared_partition_summary_reuse_threshold_pod.stdout.txt`

Hardware:

- NVIDIA RTX 4000 Ada Generation, driver 550.127.05

Source commit:

- `534446d1d98328c887318f101f42ecc518bdf4ee`

Command shape:

```bash
python3 scripts/goal4087_prepared_partition_summary_reuse_threshold.py \
  --profiles clustered3d,road3d \
  --point-count 65536 \
  --signature-runs 5 \
  --warmup 1 \
  --output docs/reports/goal4087_prepared_partition_summary_reuse_threshold_pod.json
```

The runner prepares one
`fixed_radius_partition_convergence_summary_3d` CuPy preview stream, then reuses
that prepared handle for repeated component-size signature probes. It compares
against the Goal4074 recommended-route references:

- `clustered3d_65536`: 0.093321s
- `road3d_65536`: 0.036245s

## Results

| Profile | Prepare sec | Replay median sec | Current route reference sec | 5-run prepared total sec | 5-run current reference sec | 5-run ratio prepared/current | Break-even runs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 0.443674 | 0.053135 | 0.093321 | 0.709351 | 0.466605 | 1.520x slower | 11.04 |
| `road3d` | 0.232281 | 0.042079 | 0.036245 | 0.442678 | 0.181225 | 2.443x slower | never |

Both rows kept component-size signatures stable and all claim-boundary booleans
closed.

## Interpretation

Prepared summary reuse is real but narrow. For clustered repeated workloads,
the replay part is faster than the current route: 0.053135s versus 0.093321s.
However, the one-time prepare cost is 0.443674s, so the break-even point is
about 11.04 repeated signatures. A five-run user does not win.

For road-shaped workloads, the prepared replay itself is slower than the current
recommended route: 0.042079s versus 0.036245s. No number of repeated signatures
can amortize that, because the replay term is already worse before prepare cost.

This confirms the Goal4085/4086 direction:

1. a thin prepared-summary wrapper should not become the default;
2. prepared reuse can remain an explicit option for repeated clustered
   experiments;
3. the next serious primitive must reduce work inside native/device production,
   not merely reuse the current expensive partition summary.

## Next Engineering Consequence

The next candidate should prioritize a cheaper native/device producer or fused
safe-full/ambiguous work stream:

- avoid full visible partition-pair materialization on the critical path;
- preserve exact ambiguous RT traversal;
- include partition-build cost in production timing;
- keep `ngsim_dense_65536` as a regression guard;
- require at least 50% candidate-hit or root-call reduction before promotion.

## Boundary

This report does not promote `partition_convergence_hybrid`, add a native ABI,
change default routing, authorize release wording, public speedup wording, broad
RT-core wording, whole-app acceleration wording, paper-reproduction wording,
hidden dispatch, automatic partner selection, app-specific engine logic, or true
zero-copy wording.
