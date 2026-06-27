# RTDL v2.12 Publication Note

Status: published source-tree publication packet.

Date: 2026-06-13

Version marker: `v2.12`

## Published Statement

RTDL v2.12 is an archived source-tree release for row-scoped NVIDIA
OptiX/RT-core versus Embree CPU comparison evidence over the promoted benchmark
portfolio.

The release publishes:

- the v2.12 source-tree marker and setup doctor;
- the scoped RT-core versus Embree CPU comparison table;
- the optimized packet with zero active boundary-limited rows and zero
  contract-choice blockers;
- Robot Collision and RayDB-style same-contract evidence from Goal4363 and
  Goal4364;
- updated v2.12 claim-boundary and evidence-index pages.

Use RTDL from a checkout:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --run-smoke
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

## Public Wording That Is Allowed

Use wording like this:

```text
RTDL v2.12 provides a source-tree, row-scoped comparison of NVIDIA OptiX/RT-core
paths against Embree CPU paths for the promoted benchmark portfolio. The
accepted optimized packet has no active boundary-limited rows and no
contract-choice blockers; performance wording must cite the exact row and
artifact.
```

For the mixed rows, use wording like this:

```text
Contact Manifold is Embree-faster on the tiny bounded collect-k row. Spatial
RayJoin PIP and RTNN are near-parity scoped rows. RT-DBSCAN uses RTDL plus the
same Numba continuation on both backends.
```

## Public Wording That Is Blocked

Do not publish wording that says or implies:

- RT cores make every benchmark app faster;
- the rows are whole-application speedups;
- RTDL beats RayJoin as a whole system;
- the RayJoin paper has been fully reproduced;
- v2.12 is a PyPI, wheel, or distribution-package release;
- RTDL automatically selects CuPy or Numba;
- RTDL accelerates arbitrary CuPy or Numba programs;
- v2.12 proves Intel GPU performance;
- v2.12 proves general zero-copy or device-resident execution.

## Evidence Links

- [Release package](README.md)
- [Scoped comparison table](public_rt_vs_embree_comparison.md)
- [Current Claim Boundaries](../../learn/current_claim_boundaries.md)
- [Benchmark Evidence Index](../../learn/benchmark_evidence_index.md)
- [RT-Core Evidence Matrix](../../learn/rt_core_evidence_matrix.md)
- [Optimized OptiX-vs-Embree packet](../../../reports/goal4359_optimized_embree_optix_comparison_packet_v2_12_2026-06-13.md)
- [Backend comparison campaign closeout](../../../reports/goal4345_backend_comparison_campaign_closeout_2026-06-11.md)

## Validation Summary

- Local source-tree doctor with smoke: pass.
- Local public-doc claim scan: pass with zero hard blockers.
- Local release tests: pass.
- Pod focused release tests: pass.
- Cleanup scan found no Python cache files, pytest cache, or accidental
  `scripts/pip*.exe` debris.

## Publication Boundary

This publication packet is the v2.12 public source-tree statement. It
authorizes the version marker and bounded row-scoped wording above. It does not
authorize broad speedup wording, whole-app speedup wording,
package-install wording, automatic partner-selection wording,
RTDL-beats-RayJoin wording, RayJoin paper reproduction wording, Intel GPU
performance wording, or general zero-copy/device-residency wording.
