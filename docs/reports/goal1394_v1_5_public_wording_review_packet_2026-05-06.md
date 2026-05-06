# Goal 1394 - v1.5 Public Wording Review Packet

Date: 2026-05-06

## Status

This is a review packet only.

It does not authorize:

- public v1.5 release wording,
- release tags,
- package/install claims,
- public speedup wording,
- broad NVIDIA RTX claims,
- whole-application performance claims,
- promotion of `COLLECT_K_BOUNDED` from experimental status.

Public wording and any release/tag action remain blocked until Codex, Claude, and Gemini all provide explicit acceptable verdicts on this packet.

## Evidence Inputs

Primary fresh-Git evidence:

- `docs/reports/goal1393_v1_5_stable_primitive_claim_evidence_2026-05-06.md`
- `docs/reports/goal1393_v1_5_stable_primitive_pod_results/rtdl_pod_env.json`
- `docs/reports/goal1393_v1_5_stable_primitive_pod_results/stable_primitive_evidence.json`

Fresh-Git pod commit:

```text
c0b57ae274129aa536e6ae0069f188a138bbefc1
```

Current integration commit after evidence intake:

```text
c3b4524a4a68ee03f3cad2d89f20e47609623a98
```

Pod environment summary:

```text
system: Linux x86_64
kernel: 6.8.0-49-generic
python: 3.12.3
os_id: ubuntu
package_manager: apt-get
cuda_prefix: /usr/local/cuda
nvcc: /usr/local/cuda/bin/nvcc
optix_prefix: /root/vendor/optix-dev
optix_header_exists: true
embree_version: 4.3.0
```

Goal1393 evidence summary:

```text
scalar_statuses:
  COUNT_HITS: ok
  REDUCE_FLOAT(MAX): ok
  REDUCE_FLOAT(MIN): ok
  REDUCE_FLOAT(SUM): ok
  REDUCE_INT(COUNT): ok
  REDUCE_INT(SUM): ok

direct_anyhit_count:
  cpu: ok, hit_count 256
  embree: ok, hit_count 256
  optix: ok, hit_count 256

parity:
  embree: ok, hit_count_matches true, row_count_matches true
  optix: ok, hit_count_matches true, row_count_matches true
  optix_prepared_count: ok, hit_count_matches true

prepared_optix_anyhit_count:
  status: ok
  hit_count: 256

public_wording_authorized: false
```

## Proposed Public v1.5 Wording

The following wording is proposed for later public use only if 3-AI consensus accepts it:

```text
RTDL v1.5 introduces a reviewed generic traversal-plus-reduction primitive layer.
The stable v1.5 primitive surface covers app-name-free `ANY_HIT`, `COUNT_HITS`,
`REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)` contracts.

On a fresh Linux x86_64 pod checkout, RTDL validated the stable primitive packet
with CPU reference execution plus Embree and OptiX backend checks for the direct
ray/triangle `ANY_HIT + COUNT_HITS` path. In that evidence run, CPU, Embree, and
OptiX all produced hit count 256 on the same bounded fixture; the prepared OptiX
`ANY_HIT + COUNT_HITS` path also produced hit count 256. The scalar reduction
contracts for `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, and
`REDUCE_INT(COUNT|SUM)` all returned expected values.

The public v1.5 scope is generic primitive readiness, not a universal compute
engine and not a whole-application speedup claim. Python remains the app-specific
control and lowering layer. Embree and OptiX are the active v1.5 engineering
backends; Vulkan, HIPRT, and Apple RT remain frozen before v2.1. `COLLECT_K_BOUNDED`
remains experimental.
```

## Allowed Public Claims If Accepted

If reviewers accept the packet, public wording may say:

- RTDL v1.5 introduces a reviewed generic traversal-plus-reduction primitive layer.
- Stable v1.5 primitive names are `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`.
- The Goal1393 fresh-Git pod evidence validates the stable primitive packet on Linux x86_64 with Python 3.12.3.
- In the Goal1393 bounded fixture, CPU, Embree, and OptiX direct `ANY_HIT + COUNT_HITS` each returned hit count `256`.
- In the Goal1393 bounded fixture, prepared OptiX `ANY_HIT + COUNT_HITS` returned hit count `256`.
- The scalar reductions returned expected values for all stable scalar primitive names.
- Embree and OptiX are the active v1.5 engineering backends.
- Vulkan, HIPRT, and Apple RT remain frozen before v2.1.
- `COLLECT_K_BOUNDED` remains experimental.
- Current usage remains source-tree execution with `PYTHONPATH=src:. python ...`.

## Prohibited Public Claims

Even if reviewers accept this packet, public wording must not say:

- RTDL v1.5 is publicly released before an explicit release/tag action.
- `v1.0` was moved or retagged.
- `pip install -e .` or package installation is supported.
- Any whole application is faster because of v1.5.
- NVIDIA RTX, OptiX, or GPUs are broadly faster for RTDL.
- Goal1393 timing is a public speedup benchmark.
- Graph, DB, polygon, Jaccard, KNN, ANN, DBSCAN, Hausdorff, Barnes-Hut, robot, or facility applications have new public speedup claims from this packet.
- `COLLECT_K_BOUNDED` is stable.
- Vulkan, HIPRT, or Apple RT are active v1.5 implementation targets.
- Python app-specific control has been replaced by a universal native compute engine.

## Reviewer Questions

Please answer explicitly:

1. Is the proposed wording supported by the cited Goal1393 evidence?
2. Does the wording avoid public speedup claims and whole-application claims?
3. Does the wording preserve source-tree usage and avoid package/install claims?
4. Does the wording correctly keep `COLLECT_K_BOUNDED` experimental?
5. Does the wording correctly keep Vulkan, HIPRT, and Apple RT frozen before v2.1?
6. Does the wording avoid implying a release/tag action has already happened?
7. Verdict: is this packet acceptable for public v1.5 wording after 3-AI consensus, yes or no?

An acceptable review must include an explicit yes/no verdict.

