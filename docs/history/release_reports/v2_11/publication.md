# RTDL v2.11 Publication Note

Status: published source-tree publication packet.

Date: 2026-06-12

Version marker: `v2.11`

## Published Statement

RTDL v2.11 is the current source-tree release for the Python+RTDL+partner
programming model over generic, app-agnostic native RT engines.

The release publishes:

- the v2.11 learner-facing source-tree surface;
- the Embree CPU plus partner reference lane for the promoted ten-app benchmark
  portfolio;
- the optimized RT-core versus Embree CPU evidence packet with row-specific
  boundaries;
- the RayJoin original-code same-stream LSI/PIP diagnostic comparison;
- the current claim-boundary and evidence-index pages.

Use RTDL from a checkout:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

## Public Wording That Is Allowed

Use wording like this:

```text
RTDL v2.11 provides a source-tree Python+RTDL+partner surface with current
Embree CPU and NVIDIA OptiX/RT-core benchmark evidence for promoted RT-shaped
application kernels. Performance statements are row-specific and evidence-linked.
```

For Spatial RayJoin, use wording like this:

```text
The LSI prepared scalar-count route shows strong RTDL/OptiX hot-query evidence.
The current generic exact PIP route is correct and comparable, but slower than
RayJoin's specialized PIP implementation on the same stream.
```

## Public Wording That Is Blocked

Do not publish wording that says or implies:

- RT cores make every benchmark app faster;
- RTDL beats RayJoin as a whole system;
- the RayJoin paper has been fully reproduced;
- v2.11 is a PyPI, wheel, or distribution-package release;
- RTDL automatically selects CuPy or Numba;
- RTDL accelerates arbitrary CuPy or Numba programs;
- v2.11 proves Intel GPU performance;
- v2.11 proves general zero-copy or device-resident execution.

## Evidence Links

- [Release package](README.md)
- [Current Claim Boundaries](../../learn/current_claim_boundaries.md)
- [Benchmark Evidence Index](../../learn/benchmark_evidence_index.md)
- [RT-Core Evidence Matrix](../../learn/rt_core_evidence_matrix.md)
- [Goal4298 v2.11 Embree CPU + partner reference packet](../../../reports/goal4298_v2_11_embree_cpu_partner_reference_packet_2026-06-11.md)
- [Goal4308 RTNN Embree front door for v2.11](../../../reports/goal4308_rtnn_embree_front_door_for_v2_11_packet_2026-06-11.md)
- [Goal4345 backend comparison campaign closeout](../../../reports/goal4345_backend_comparison_campaign_closeout_2026-06-11.md)
- [Goal4353 human-scale RT-core vs Embree CPU comparison](../../../reports/goal4353_human_scale_rt_vs_embree_run_20260612_pod_v3/summary.md)
- [Goal4354 RayJoin original-code same-stream comparison](../../../reports/goal4354_rayjoin_original_vs_rtdl_pod/goal4354_rayjoin_original_vs_rtdl_same_stream_summary.md)

## Validation Summary

- Local source-tree doctor: pass.
- Local hello-world smoke: pass.
- Pod source-tree doctor with CuPy, Numba, OptiX, and Embree visible: pass.
- Pod release tests: `22 passed`.
- Current public-doc claim scan:
  `docs/reports/goal4248_current_public_docs_claim_boundary_scan.json`
  reports `status: pass`, `public_file_count: 36`, and
  `hard_blocker_count: 0`.
- Cleanup scan found no Python cache files, pytest cache, or accidental
  `scripts/pip*.exe` debris.
- Release hygiene excludes raw pod logs, scratch clones, build outputs, and
  bulky per-run JSON payloads from the source-tree release while retaining the
  compact summaries and reproduction scripts.

## Publication Boundary

This publication packet is the v2.11 public source-tree statement. It authorizes
the version marker and bounded release wording above. It does not authorize
broad speedup wording, whole-app speedup wording, package-install wording,
automatic partner-selection wording, RTDL-beats-RayJoin wording, RayJoin paper
reproduction wording, Intel GPU performance wording, or general
zero-copy/device-residency wording.
