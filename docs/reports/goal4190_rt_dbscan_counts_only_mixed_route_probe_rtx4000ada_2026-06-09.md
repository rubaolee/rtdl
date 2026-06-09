# Goal4190: RT-DBSCAN Counts-Only Mixed-Route Probe on RTX 4000 Ada

Date: 2026-06-09  
Source commit: `94933000`  
Artifact directory: `docs/reports/goal4190_rt_dbscan_counts_only_mixed_route_probe_rtx4000ada/`

## Purpose

Goal4165 and Goal4166 showed that mixed-predicate RT-DBSCAN rows have a
semantic contract problem: a predicate-false item can touch more than one
predicate-true component. If component-size distribution is part of the
contract, a route must publish a deterministic border-assignment policy. If the
caller only needs core/noise/assigned counts, those border tie-breaks can be
outside the contract.

Goal4190 measures that distinction directly at scale. It does not add an engine
primitive and does not promote a route. It compares:

- current grouped-stream Numba route;
- predicate direct-status until-stable route;
- predicate direct-status single-pass candidate route.

Each row records both `policy_bound_component_sizes` and
`core_noise_assigned_counts_only` signatures.

## Pod Setup

- Pod: `ssh root@157.157.221.29 -p 24101 -i ~/.ssh/id_ed25519`
- Effective RTDL working key used by Codex: `id_ed25519_rtdl_codex`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.08`

Command shape:

```bash
python3 scripts/goal4190_rt_dbscan_counts_only_mixed_route_probe.py \
  --dataset road3d --point-count <N> --warmup-point-count 4096 \
  --radius 0.003 --min-neighbors 16 --partition-cell-factor 0.25 \
  --repeat 1 --warmup 0 --seed 20260519
```

## Results

| Point count | Route | Elapsed sec | Speedup vs grouped | Component-size match | Counts-only match |
| ---: | --- | ---: | ---: | --- | --- |
| 262,144 | grouped-stream Numba | 0.492688 | 1.000x | true | true |
| 262,144 | predicate direct-status until-stable | 0.560486 | 0.879x | false | true |
| 262,144 | predicate direct-status single-pass | 0.524893 | 0.939x | false | true |
| 1,048,576 | grouped-stream Numba | 2.365394 | 1.000x | true | true |
| 1,048,576 | predicate direct-status until-stable | 2.504285 | 0.945x | false | true |
| 1,048,576 | predicate direct-status single-pass | 2.356724 | 1.004x | false | true |
| 2,097,152 | grouped-stream Numba | 4.974810 | 1.000x | true | true |
| 2,097,152 | predicate direct-status until-stable | 5.463750 | 0.911x | false | true |
| 2,097,152 | predicate direct-status single-pass | 4.912520 | 1.013x | false | true |
| 4,194,304 | grouped-stream Numba | 10.915954 | 1.000x | true | true |
| 4,194,304 | predicate direct-status until-stable | 11.234520 | 0.972x | false | true |
| 4,194,304 | predicate direct-status single-pass | 10.334723 | 1.056x | false | true |

## Interpretation

The semantic-contract split is correct:

- Counts-only signatures match the grouped-stream reference at every tested
  scale.
- Policy-bound component-size signatures do not match for direct-status routes,
  so component-size semantics still require an explicit border policy.

The performance result is more cautious:

- until-stable predicate direct-status is slower than grouped-stream on every
  tested scale;
- single-pass predicate direct-status reaches parity around 1M and a modest
  `1.056x` at 4M;
- this is not a major win and should not become a default route.

The next runtime-level performance target remains the larger primitive described
in the future design list: a generic predicate-aware direct-status grouped-union
primitive with deterministic border assignment, not a DBSCAN-specific shortcut.

## Boundary

Goal4190 does not authorize release, public speedup wording, broad RT-core
claims, whole-app claims, true-zero-copy claims, route promotion, hidden
dispatch, automatic partner selection, or app-specific native-engine logic.

The native vocabulary remains generic: predicate flags, fixed-radius pairs,
component roots, counts, and border-assignment policy. DBSCAN policy remains in
the benchmark app layer.

## Validation

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4190_rt_dbscan_counts_only_mixed_route_probe_test
```
