# RTDL v2.13 Release Package

Status: published source-tree release package.

Version marker: `v2.13`

Release date: 2026-06-13

## Release Statement

RTDL v2.13 is the current source-tree release for the refreshed row-scoped NVIDIA OptiX/RT-core versus Embree CPU comparison. The release keeps every published performance sentence tied to a benchmark row, contract, direction, and caveat.

Use RTDL directly from a checkout:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

This is not a package-install release, not automatic partner selection, not whole-application speedup wording, not RTDL-beats-RayJoin wording, not RayJoin paper reproduction, and not Intel/AMD GPU performance wording.

## Comparison Summary

Read the detailed table in [v2.13 row-scoped RT-core vs Embree CPU comparison](public_rt_vs_embree_comparison.md).

| Result bucket | Count / value |
| --- | ---: |
| Promoted apps covered | 10 |
| Scoped comparison rows | 11 |
| Row-scoped wording-authorized rows | 10 |
| Blocked rows | 1 |
| Human-scale rows in 1-10s band | True |
| Human-scale PIP Embree/OptiX | 0.947x |
| Goal4368 exact PIP Embree/OptiX | 3.216x |

## Important Mixed Rows

- Spatial RayJoin PIP is near parity and slightly Embree-faster in the refreshed human-scale public CDB slice.
- Goal4368 separately records the full same-stream exact PIP executor: OptiX is faster than Embree there, but RayJoin RT is still faster than RTDL PIP.
- RTNN remains blocked as an RT-core neighbor-search claim.
- RT-DBSCAN uses RTDL plus the same fixed Numba continuation policy.

## Evidence

- [v2.13 publication note](publication.md)
- [v2.13 tag preparation](tag_preparation.md)
- [v2.13 row-scoped comparison](public_rt_vs_embree_comparison.md)
- [Goal4370 public wording packet](../../reports/goal4370_v2_13_public_wording_packet_2026-06-13.md)
- [Goal4349 refreshed human-scale packet](../../reports/goal4349_human_scale_rt_vs_embree_comparison_2026-06-12.md)
- [Goal4369 Embree CPU fairness packet](../../reports/goal4369_embree_cpu_fairness_hardening_2026-06-13.md)
- [Goal4368 PIP exact prepared-points executor](../../reports/goal4368_pip_exact_prepared_points_executor_2026-06-13.md)
- [Goal4367 RayJoin authors-code packet](../../reports/goal4367_rayjoin_authors_code_comparison_packet_2026-06-13.md)

## Release Boundary

RTDL v2.13 authorizes the source-tree marker and the row-scoped wording above. It does not authorize broad RT-core speedup, whole-application speedup, package-install, automatic partner selection, RTDL-beats-RayJoin, RayJoin paper reproduction, Intel GPU performance, AMD GPU performance, or general zero-copy/device-residency claims.

Validation status: `accept`.
