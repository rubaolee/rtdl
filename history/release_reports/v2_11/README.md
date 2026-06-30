# RTDL v2.11 Release Package

Status: published source-tree release package.

Version marker: `v2.11`

Release date: 2026-06-12

## Release Statement

RTDL v2.11 is the current source-tree milestone for the Python+RTDL+partner
programming model over a generic, app-agnostic native engine. It carries forward
the v2.10 learner surface and closes the Embree CPU plus partner reference lane
for the promoted ten-app benchmark portfolio.

Use RTDL directly from a checkout:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

This is not a package-install release, not a broad RT-core speedup claim, not a
whole-application speedup claim, not an automatic partner-selection promise,
not RTDL-beats-RayJoin wording, and not a general zero-copy/device-residency
product claim.

## What v2.11 Includes

- The current v2.11 Python+partner+RTDL learner surface, tutorials, and
  source-tree usage model, carrying forward the v2.10 language boundary.
- A closed Embree CPU plus partner reference packet for the ten promoted
  benchmark apps.
- A fair RT-core versus Embree CPU comparison packet with per-row wording
  boundaries.
- A RayJoin original-code same-stream comparison for LSI and PIP, used as
  external diagnostic evidence rather than broad paper-reproduction wording.
- Updated claim-boundary and evidence-index pages that keep performance wording
  path-specific.

## Promoted Benchmark App Surface

| Benchmark app | v2.11 release boundary |
| --- | --- |
| Hausdorff / X-HD-style | Exact-distance benchmark and RT-assisted threshold evidence; not every input beats CUDA or CPU. |
| Spatial RayJoin-style | LSI prepared scalar-count evidence is strong; PIP exact count is correct but slower than RayJoin's specialized PIP implementation on the same stream. |
| RT-DBSCAN-style | Generic fixed-radius/component benchmark with explicit Numba continuation where used; no DBSCAN-native ABI. |
| Robot collision | Prepared static-scene screening; not a full motion planner. |
| RayDB-style grouped aggregate | Fused primitive-first aggregates when they match; not SQL or a DBMS. |
| Barnes-Hut / RT-BarnesHut-style | Aggregate-frontier pressure and partner continuation evidence; not a broad force-solver speedup claim. |
| LibRTS spatial index | Prepared AABB-index benchmark slice; not full mutable LibRTS. |
| RTNN neighbor search | Prepared ranked-summary paths and Embree candidate-quality reference; not full RTNN paper reproduction. |
| Triangle counting | Scalar primitive preferred for scalar answers; row interpretation stays app code. |
| Contact witness / contact manifold | Bounded witness collection; no contact/manifold native ABI. |

## Evidence

- [v2.11 publication note](publication.md)
- [v2.11 tag preparation](tag_preparation.md)
- [Goal4298 v2.11 Embree CPU + partner reference packet](../../reports/goal4298_v2_11_embree_cpu_partner_reference_packet_2026-06-11.md)
- [Goal4308 RTNN Embree front door for v2.11](../../reports/goal4308_rtnn_embree_front_door_for_v2_11_packet_2026-06-11.md)
- [Goal4345 backend comparison campaign closeout](../../reports/goal4345_backend_comparison_campaign_closeout_2026-06-11.md)
- [Goal4353 human-scale RT-core vs Embree CPU comparison](../../reports/goal4353_human_scale_rt_vs_embree_run_20260612_pod_v3/summary.md)
- [Goal4354 RayJoin original-code same-stream comparison](../../reports/goal4354_rayjoin_original_vs_rtdl_pod/goal4354_rayjoin_original_vs_rtdl_same_stream_summary.md)
- [Current Claim Boundaries](../../learn/current_claim_boundaries.md)
- [Benchmark Evidence Index](../../learn/benchmark_evidence_index.md)
- [RT-Core Evidence Matrix](../../learn/rt_core_evidence_matrix.md)

## Minimal Smoke Commands

Portable source-tree smoke:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
PYTHONPATH=src:. python examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
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

The publication packet was checked on 2026-06-12 with:

- local source-tree doctor: pass;
- local hello-world smoke: pass;
- pod source-tree doctor with CuPy, Numba, OptiX, and Embree visible: pass;
- pod release tests:
  `tests/goal4248_current_public_docs_claim_boundary_scan_test.py`,
  `tests/goal4298_v2_11_embree_cpu_partner_reference_packet_test.py`,
  `tests/goal4345_backend_comparison_campaign_closeout_test.py`, and
  `tests/goal4349_human_scale_rt_vs_embree_comparison_test.py`: `22 passed`;
- cleanup scan: no `__pycache__`, `.pyc`, `.pyo`, `.pytest_cache`, or
  accidental `scripts/pip*.exe` debris remains.
- release hygiene: raw pod logs, scratch clones, build outputs, and bulky
  per-run JSON payloads are excluded from the source-tree release; compact
  summaries and reproduction scripts are retained.

## Tag And Head Note

Publish v2.11 only from a commit that contains the `VERSION` marker, this
release package, the v2.11 claim-boundary pages, the Embree CPU reference
packet, the RT-core-vs-Embree comparison evidence, and the RayJoin original-code
diagnostic packet. Do not place a `v2.11` tag on an older head that lacks those
files.

Recommended tag name after the publication commit is `v2.11`.

Do not move a published `v2.11` tag without explicit maintainer
decision.

## Release Boundary

RTDL v2.11 is ready as a bounded engineering source-tree release. It authorizes
the version marker, release package, Embree CPU plus partner reference wording,
and evidence-index updates. It does not authorize broad RT-core speedup,
whole-application speedup, package-install, automatic partner selection,
RTDL-beats-RayJoin, RayJoin paper reproduction, Intel GPU performance, or
general zero-copy/device-residency claims.
