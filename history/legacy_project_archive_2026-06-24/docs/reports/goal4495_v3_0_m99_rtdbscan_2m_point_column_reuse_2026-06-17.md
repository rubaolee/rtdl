# Goal4495 / V3 M99 RT-DBSCAN 2M Point-Column Reuse

## Conclusion

Goal4495 extends the Goal4489/Goal4490 RT-DBSCAN caller-owned coordinate-column evidence to the 2,097,152-point `road3d` profile.

The result is clean and conservative. When CuPy `x/y/z` device columns already exist, direct-status prepare is much faster: 45.90x for the isolated direct-status handle and 65.73x-73.21x inside the predicate direct-status app route. When the app constructs those columns from Python point rows and charges that build, the 2M app total is essentially flat: 1.018x for one-shot and 0.999x for warmed replay.

So the rule stays the same, now with larger-scale evidence: use point-column direct-status when the caller naturally owns device columns; do not build temporary columns solely to claim a speedup unless that build is charged.

## Evidence

Hardware: RTX 4000 Ada pod, driver 550.127.08.

Artifacts:

- `docs/reports/goal4495_v3_0_m99_rtdbscan_2m_point_column_reuse_2026-06-17.json`
- `docs/reports/goal4495_v3_0_m99_rtdbscan_2m_point_column_reuse_2026-06-17.jsonl`

Protocol:

- dataset: `road3d`
- point count: 2,097,152
- seed: 20260519
- partition cell factor: 0.25
- convergence: `single_pass_candidate`
- app protocols: `one_shot` (`w0/r1`) and `warm_replay` (`w1/r3`)

All primitive and app signatures matched.

## Matrix

| Scope | Protocol | Row prepare | Column build | Column handle prepare | Charged column prepare | Prepare speedup if columns already owned | Charged prepare speedup | Charged prepare+count speedup | Charged prepare+replay speedup |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| isolated direct-status | n/a | 0.934s | 1.029s | 0.020s | n/a | 45.90x | n/a | n/a | n/a |
| app predicate direct-status | one_shot | 0.568s | 0.565s | 0.0086s | 0.574s | 65.73x | 0.99x | 1.018x | 1.018x |
| app predicate direct-status | warm_replay | 0.623s | 0.564s | 0.0085s | 0.573s | 73.21x | 1.09x | 0.999x | 0.999x |

The app route still prepares the generic OptiX self-query count-threshold scene from the point rows. This test isolates the direct-status coordinate-column handoff; it is not a true-zero-copy end-to-end RT-DBSCAN claim.

## Reading

This closes the immediate "does point-column reuse survive beyond 1M?" question for RT-DBSCAN:

- caller-owned columns remain a real app-agnostic prepare optimization at 2M;
- app-constructed columns are accounted for honestly and are not a default promotion;
- the row-input predicate direct-status path remains the default measured compact-signature route;
- the point-column app mode remains explicit for callers whose upstream pipeline already owns partner-resident coordinate columns.

Claim boundary:

- route promotion authorized: false;
- whole-app speedup claim authorized: false;
- true-zero-copy claim authorized: false;
- automatic partner selection authorized: false;
- point-column construction is charged when the app constructs columns.
