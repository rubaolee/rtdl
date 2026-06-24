# RTDL v2.12 Release Package

Status: published source-tree release package.

Version marker: `v2.12`

Release date: 2026-06-13

## Release Statement

RTDL v2.12 is an archived source-tree milestone for the row-scoped NVIDIA
OptiX/RT-core versus Embree CPU comparison campaign over the promoted benchmark
portfolio. It carries forward the v2.11 Python+RTDL+partner surface and closes
the v2.12 comparison cleanup: zero active boundary-limited rows, no remaining
contract-choice blockers, and no missing same-contract scale pair in the
optimized packet.

Use RTDL directly from a checkout:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

This is not a package-install release, not a broad RT-core speedup claim, not a
whole-application speedup claim, not automatic partner selection, not
RTDL-beats-RayJoin wording, not RayJoin paper reproduction, and not a general
zero-copy/device-residency product claim.

## What v2.12 Includes

- The v2.12 source-tree Python+RTDL+partner surface from v2.11.
- A release-facing scoped RT-core versus Embree CPU comparison table for the
  promoted benchmark apps.
- Goal4363 Robot Collision same-contract prepared-buffer evidence.
- Goal4364 RayDB-style same-contract prepared grouped-reduction evidence.
- A regenerated optimized comparison packet with `10` internally authorized
  app ratios, `0` active boundary-limited rows, and `0` contract-choice
  blockers.
- Updated source-tree version marker, setup doctor, and v2.12 public-doc
  boundary pages.

## Comparison Summary

Read the detailed table in
[v2.12 scoped RT-core vs Embree CPU comparison](public_rt_vs_embree_comparison.md).

| Result bucket | Count |
| --- | ---: |
| Promoted apps covered | 10 |
| Scoped comparison rows | 11 |
| OptiX-faster scoped rows | 10 |
| Embree-faster scoped rows | 1 |
| Active boundary-limited rows | 0 |
| Contract-choice blockers | 0 |

Important mixed rows stay visible:

- Contact Manifold is Embree-faster for the tiny bounded collect-k row.
- Spatial RayJoin PIP and RTNN are near-parity rows, not broad RT-core claims.
- RT-DBSCAN uses RTDL plus the same Numba continuation on both backends.
- RayDB-style is a generic prepared grouped-reduction row, not SQL or DBMS
  acceleration wording.

## Evidence

- [v2.12 publication note](publication.md)
- [v2.12 tag preparation](tag_preparation.md)
- [v2.12 scoped RT-core vs Embree CPU comparison](public_rt_vs_embree_comparison.md)
- [Optimized OptiX-vs-Embree packet](../../../reports/goal4359_optimized_embree_optix_comparison_packet_v2_12_2026-06-13.md)
- [Current OptiX-vs-Embree comparability index](../../../reports/goal4359_current_optix_embree_comparison_index_v2_12_2026-06-13.md)
- [Backend comparison campaign closeout](../../../reports/goal4345_backend_comparison_campaign_closeout_2026-06-11.md)
- [Robot Collision same-contract evidence](../../../reports/goal4363_rtx_a4000_v2_12_robot_collision_same_contract_2026-06-13.md)
- [RayDB-style same-contract evidence](../../../reports/goal4364_rtx_a4000_v2_12_raydb_same_contract_2026-06-13.md)
- [Current Claim Boundaries](../../learn/current_claim_boundaries.md)
- [Benchmark Evidence Index](../../learn/benchmark_evidence_index.md)
- [RT-Core Evidence Matrix](../../learn/rt_core_evidence_matrix.md)

## Minimal Smoke Commands

Portable source-tree smoke:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --run-smoke
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

With native CPU dependencies configured:

```bash
PYTHONPATH=src:. python examples/current/partners/rtdl_partner_anyhit.py --partner numpy --backend embree
```

With a configured NVIDIA pod and OptiX library:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python examples/current/partners/rtdl_partner_anyhit.py --partner cupy-cuda --backend optix
```

## Publication Validation

The publication packet was checked on 2026-06-13 with:

- local source-tree doctor with smoke: pass;
- current public-doc claim scan: pass with zero hard blockers;
- local focused release tests: pass;
- pod focused release tests: pass;
- cleanup scan: no Python cache files, pytest cache, or accidental
  `scripts/pip*.exe` debris remains.

## Tag And Head Note

Publish v2.12 only from a commit that contains the `VERSION` marker, this
release package, the regenerated public-doc claim scan, the optimized v2.12
comparison packet, and the Goal4363/Goal4364 same-contract evidence.

Recommended tag name after the publication commit is `v2.12`.

Do not move a published `v2.12` tag without explicit maintainer decision.

## Release Boundary

RTDL v2.12 is ready as a bounded engineering source-tree release. It authorizes
the version marker, release package, and row-scoped comparison wording above.
It does not authorize broad RT-core speedup, whole-application speedup,
package-install, automatic partner selection, RTDL-beats-RayJoin, RayJoin paper
reproduction, Intel GPU performance, or general zero-copy/device-residency
claims.
