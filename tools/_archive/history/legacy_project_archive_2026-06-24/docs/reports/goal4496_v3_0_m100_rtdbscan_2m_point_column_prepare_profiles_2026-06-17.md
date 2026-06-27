# Goal4496 / V3 M100 RT-DBSCAN 2M Point-Column Prepare Profiles

## Conclusion

Goal4496 extends the isolated direct-status caller-owned coordinate-column prepare check to the two non-`road3d` 2M RT-DBSCAN profiles: `clustered3d` and `ngsim_dense`.

Both rows pass. At 2,097,152 points, caller-owned CuPy coordinate columns cut direct-status prepare by 127.93x on `clustered3d` and 82.07x on `ngsim_dense`, with matching component-size signatures.

This is intentionally narrower than Goal4495. It proves the coordinate-column handoff is not a `road3d` accident, but it does not run the full predicate count-threshold app route and does not promote temporary app-constructed columns as a default.

## Evidence

Hardware: RTX 4000 Ada pod, driver 550.127.08.

Artifacts:

- `docs/reports/goal4496_v3_0_m100_rtdbscan_2m_point_column_prepare_profiles_2026-06-17.json`
- `docs/reports/goal4496_v3_0_m100_rtdbscan_2m_point_column_prepare_profiles_2026-06-17.jsonl`

Protocol:

- datasets: `clustered3d`, `ngsim_dense`
- point count: 2,097,152
- seed: 20260519
- partition cell factor: 0.25
- route: isolated direct-status component-signature prepare/run
- comparison: Python point rows versus caller-owned CuPy `x/y/z` device columns

| Dataset | Point-column build | Row prepare | Column prepare | Prepare speedup if columns already owned | Row run | Column run | Signature |
|---|---:|---:|---:|---:|---:|---:|---|
| `clustered3d` | 1.255s | 1.280s | 0.0100s | 127.93x | 10.521s | 10.423s | match |
| `ngsim_dense` | 0.858s | 0.866s | 0.0106s | 82.07x | 2.302s | 2.292s | match |

Diagnostic prepare-phase speedups:

| Dataset | Phase speedup if columns already owned |
|---|---:|
| `clustered3d` | 123.44x |
| `ngsim_dense` | 77.42x |

## Reading

Together with Goal4495, this gives a sharper RT-DBSCAN rule:

- caller-owned coordinate columns are a real app-agnostic optimization at 2M scale across `road3d`, `clustered3d`, and `ngsim_dense`;
- column construction is not free and must stay visible when an app starts from Python rows;
- this row is direct-status prepare evidence only, not a predicate count-threshold app-total row;
- the default compact-signature route remains explicit predicate direct-status for measured profiles, with grouped-stream Numba as fallback/reference.

Claim boundary:

- isolated direct-status prepare only;
- not count-threshold app route;
- route promotion authorized: false;
- whole-app speedup claim authorized: false;
- true-zero-copy claim authorized: false.
