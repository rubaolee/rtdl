# Goal1609 v1.6.x Performance Roadmap

Date: 2026-05-09

## Verdict

Use `v1.6.1` through `v1.6.10` as the Python+RTDL performance-boosting lane
after the published `v1.6` architecture milestone.

The purpose is to restart and finish the tuning work that was intentionally not
closed before v1.6:

- promote or reject `COLLECT_K_BOUNDED` with strict evidence;
- reduce Python/native copy and materialization overhead;
- make prepared host-output paths real performance tools, not only parity
  artifacts;
- improve OptiX/NVIDIA RT-core paths against Embree on exact same-contract
  workloads;
- keep every public claim scoped to reviewed measured subpaths.

This roadmap does not authorize a release tag, true zero-copy wording, broad
RTX/GPU speedup wording, whole-app speedup wording, package-install wording, or
stable `COLLECT_K_BOUNDED` promotion by itself.

Short form: no true zero-copy wording, no broad RTX/GPU speedup wording, no
whole-app speedup wording, and no stable `COLLECT_K_BOUNDED` promotion without
a separate evidence gate.

## Starting Point

`v1.6` is complete and public. It establishes the first Python+RTDL architecture
boundary:

- Python remains the app/control layer.
- RTDL owns the supported RT-shaped primitive contract and bridge.
- Embree and OptiX execute validated stable primitive subpaths.
- Stable primitive surface:
  `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, and
  `REDUCE_INT(COUNT|SUM)`.
- `COLLECT_K_BOUNDED`, true zero-copy, partner tensor handoff, package install,
  broad app speedup, broad RTX speedup, and app-free native internals remain
  outside v1.6.

Important evidence already exists:

- Goal1438 accepted the post-hardening `COLLECT_K_BOUNDED` state as a current
  snapshot, while explicitly blocking stable promotion and public claims.
- Goal1455 accepted prepared host-output parity evidence with 3-AI consensus,
  while keeping prepared-buffer reuse, true zero-copy, speedup wording, and
  release action blocked.
- Goal1465 accepted internal reduced-copy candidate evidence with 3-AI
  consensus, limited to typed contiguous host input-buffer materialization
  count reduction.
- Goal1197 and follow-up OptiX investigation reports show that several apps
  remain slower or mixed versus Embree because Python/ctypes preparation,
  packing, transfer, row materialization, exact continuation, chunk handling, or
  scene preparation can dominate.

## North Star

By the end of the v1.6.x lane, RTDL should have at least one accepted
performance package where:

- a user writes normal Python+RTDL code, not a backend-specific program;
- the RT-shaped hot path is prepared, bounded, and measured;
- input and output movement are explicitly counted and reduced where possible;
- Embree and OptiX parity is strict for the same contract;
- OptiX/NVIDIA evidence is collected on real RTX hardware only after local
  readiness is complete;
- public performance wording names the exact subpath and excluded phases.

The milestone is not "RTDL optimizes all Python." The milestone is "RTDL makes
the RT part fast and honest, while Python remains the surrounding app layer."

## Release Roadmap

| Version | Goal | Deliverable | Acceptance Gate | Hardware Need |
| --- | --- | --- | --- | --- |
| `v1.6.1` | Measurement foundation | One command or script family that records per-phase time, copy/materialization counts, output contract, backend, commit, and host metadata for selected Embree/OptiX workloads. | Local Windows/Linux tests plus no public-claim wording. | No pod unless validating OptiX smoke. |
| `v1.6.2` | Prepared host-output performance gate | Convert Goal1455 parity evidence into reusable benchmarkable paths with explicit output-buffer ownership, overflow behavior, and phase timing. | Embree parity, OptiX parity where claimed, overflow fail-closed tests, no true zero-copy wording. | Local Linux first; pod only for real OptiX parity/perf. |
| `v1.6.3` | Reduced-copy host input path | Promote the Goal1465 typed contiguous host-input path from internal candidate to measured reduced-copy API for selected primitive shapes. | Copy-count deltas must be measured; timing is diagnostic unless same-contract benchmark is accepted. | No pod for API/tests; pod only for OptiX timing. |
| `v1.6.4` | `COLLECT_K_BOUNDED` fail-closed promotion attempt | Decide whether `COLLECT_K_BOUNDED` can become a stable primitive or must stay experimental. | Capacity metadata, valid-count metadata, overflow behavior, bounds tests, Embree/OptiX parity, and external review. OptiX performance evidence collected here is correctness-era evidence and must be re-sampled in the later v1.6.8 package after preparation/packing work. | Pod required for OptiX promotion evidence. |
| `v1.6.5` | OptiX preparation and packing reduction | Attack OptiX scene/ray preparation, Python packing, launch setup, and candidate/output transfers for the slower-app rows identified by Goal1197/Goal1267. | Phase evidence must show where time moved; positive wording remains blocked unless same-contract speedup is reviewed. | Pod required for RTX evidence. |
| `v1.6.6` | App-generic prepared session API | Provide a stable Python-facing session object for repeated RT-shaped queries without exposing app-specific native names. | Same user-visible contract across Embree and OptiX; stale-session and wrong-shape failures are explicit. | Local first; pod for OptiX. |
| `v1.6.7` | Thin result views | Reduce Python dictionary rematerialization for selected outputs by adding thin views or structured buffers while preserving compatibility row APIs. | Existing row API parity; new thin-view API tests; memory/row materialization counts. | No pod required unless measuring OptiX total time. |
| `v1.6.8` | Same-contract OptiX vs Embree performance package | Run accepted long-workload benchmark packets for at least DB compact summary, graph visibility/prepared rays, polygon overlap/Jaccard, Hausdorff threshold, robot prepared flags/counts, and one positive control. Include the v1.6.6 session paths where they apply, not just ad hoc prepared paths. | Strict parity, commit traceability, phase timing, same-contract comparison, 3-AI review. | Pod required. |
| `v1.6.9` | Public performance claim audit | Decide which, if any, exact subpaths earn public positive wording; keep mixed/slower results as engineering evidence. | Public claim matrix updated only for reviewed exact subpaths; blocked wording tests pass. | No new pod unless evidence gap remains. |
| `v1.6.10` | v1.6.x performance package | Publish a consolidated v1.6.x report package, support matrix delta, and next-track handoff to v1.7. | Windows/Linux/OptiX validation, 3-AI consensus, explicit release authorization if tagging. | Pod only if final OptiX validation is stale. |

The version numbers are planning slots, not mandatory tags. If a goal is not
ready, keep it internal and continue with `v1.6.11+` rather than weakening the
claim standard.

## Workstreams

### Workstream A: Measurement Before Optimization

Problem: performance discussions have repeatedly become confusing when setup,
packing, traversal, output, validation, and Python continuation are collapsed
into one time.

Plan:

- Standardize phase fields across new performance runners.
- Record copy/materialization counts alongside timing.
- Split scene preparation, probe/ray packing, host-to-device transfer, launch,
  traversal, output transfer, validation, and Python continuation when the
  backend can report those phases.
- Record backend, mode, output contract, commit, host, GPU, driver, and OptiX
  SDK metadata.
- Treat slow OptiX runs as useful if the bottleneck is precisely classified.

Exit criteria:

- A local benchmark runner can explain where time went before a pod is started.
- Pod runs are batched and never used for vague exploration.

### Workstream B: Prepared Host Output And Thin Results

Problem: RT traversal may be fast while Python row materialization destroys the
benefit.

Plan:

- Build on Goal1455 prepared host-output parity.
- Add reusable output-buffer descriptors and overflow/fail-closed checks.
- Add thin result views or structured host buffers for selected paths.
- Preserve compatibility rows for users who need dict output.
- Document a migration pattern from compatibility rows to thin views once thin
  views exist, so users can adopt the faster path without guessing.

Exit criteria:

- Same semantic output can be returned as compatibility rows or thin/native
  views.
- Materialization counts are measured.
- Public docs describe reduced materialization, not true zero-copy.

### Workstream C: Reduced-Copy Host Input

Problem: repeated Python object-to-native materialization can dominate long
workloads.

Plan:

- Build on Goal1465 typed contiguous host input-buffer evidence.
- Define which input shapes can accept typed contiguous buffers safely.
- Keep ownership/lifetime rules explicit.
- Count input materialization operations and bytes where possible.

Exit criteria:

- Selected benchmark paths show fewer materializations by measurement.
- No true zero-copy wording unless a later device-resident/shareable memory
  gate proves it.

### Workstream D: `COLLECT_K_BOUNDED`

Problem: bounded collection is the missing primitive for many app-shaped
workloads, but it is dangerous if overflow, capacity, ordering, or parity are
ambiguous.

Plan:

- Keep `COLLECT_K_BOUNDED` experimental until a promotion package passes.
- Require explicit `capacity`, `valid_count`, overflow flag, and deterministic
  result validation semantics.
- Test fail-closed overflow behavior.
- Require Embree and OptiX parity where claimed.
- Benchmark but separate speedup from stability.

Exit criteria:

- Either stable-promotion decision with evidence and 3-AI consensus, or a
  documented rejection/defer decision with exact blockers.

### Workstream E: OptiX/NVIDIA RT-Core Performance

Problem: OptiX can be correct but slower than Embree when launch/setup,
packing, transfer, or output dominates. That is not failure; it is a map.

Plan:

- Use Goal1197/Goal1267 slower-app findings as first targets.
- Prefer long workloads where setup can amortize.
- Reuse prepared scenes and prepacked rays/probes wherever semantics allow.
- Keep positive controls in every pod batch.
- Require same-contract Embree and OptiX comparisons.

Exit criteria:

- At least one exact subpath earns reviewed positive wording, or the roadmap
  produces a precise "OptiX still slower with reason" package that guides the
  next implementation.

A positive control means a workload/mode where prior evidence already suggests
OptiX can beat Embree under the same contract. It is included to detect broken
measurement environments before interpreting slower or mixed rows.

## Claim Rules

Allowed wording after this roadmap starts:

```text
RTDL v1.6.x is the performance-boosting lane after the v1.6 Python+RTDL
architecture milestone.
```

Allowed wording only after exact evidence and review:

```text
RTDL accelerates <exact prepared/native subpath> for <workload> on <backend>
under <measured contract>, excluding <phases>.
```

Blocked until separately proven:

- RTDL accelerates arbitrary Python.
- RTDL accelerates whole applications by default.
- `--backend optix` means NVIDIA RT-core speedup.
- `COLLECT_K_BOUNDED` is stable.
- True zero-copy is supported.
- Partner tensor handoff is part of v1.6.x.
- Package-install usage is supported.
- Vulkan/HIPRT/Apple RT are active v1.6.x optimization targets.

## Pod Policy

Do not start a paid pod for roadmap writing, local API work, doc work, or
unreviewed exploration.

Before asking for a pod:

- local tests must pass;
- benchmark commands must be scripted;
- expected artifacts and copy-back paths must be known;
- OptiX SDK/driver assumptions must be written down;
- positive controls and failure handling must be included.

When a pod is available:

- validate from Git;
- record commit, GPU, driver, CUDA, OptiX SDK, and command transcript;
- batch all ready workloads;
- copy artifacts back after every group;
- interpret only after parity and metadata checks pass.

## First Concrete Next Goals

1. Goal1610: create the v1.6.x phase/copy measurement manifest and local runner
   skeleton.
2. Goal1611: wire prepared host-output benchmark metadata for one Embree path
   and one OptiX-capable path, without claiming speedup.
3. Goal1612: add reduced-copy input-buffer materialization counters to the
   selected path and verify compatibility rows still match.
4. Goal1613: write the `COLLECT_K_BOUNDED` promotion/rejection gate with exact
   required evidence fields.
5. Goal1614: prepare the first RTX pod packet only after Goals1610-1613 produce
   executable local artifacts.

## Recommendation

Start with `v1.6.1` as a measurement-foundation release candidate. Do not jump
directly to GPU tuning before the local phase/copy contract exists. Once local
measurement is stable, use `v1.6.2-v1.6.5` to convert the existing prepared
host-output, reduced-copy, collect-k, and OptiX evidence into real
performance-engineering packages.

This keeps money-burning pod time productive and keeps the public story honest.
