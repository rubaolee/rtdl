# Goal 1395 - v1.5 Release Readiness Decision

Date: 2026-05-06

## Status

RTDL `main` is ready for an explicit v1.5 release operation, but this report does not perform that operation.

Allowed conclusion:

> RTDL has enough evidence and 3-AI-reviewed wording to proceed to a bounded public `v1.5` release operation focused on generic traversal-plus-reduction primitive readiness.

Still required before public release exists:

- explicit user authorization to create a `v1.5` release/tag;
- final local release-surface check at the release commit;
- tag creation at the exact intended commit;
- no movement of `v1.0`.

## Release Scope

The accepted v1.5 public scope is generic primitive readiness, not a universal compute engine and not a performance release.

Stable v1.5 primitive surface:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN)`
- `REDUCE_FLOAT(MAX)`
- `REDUCE_FLOAT(SUM)`
- `REDUCE_INT(COUNT)`
- `REDUCE_INT(SUM)`

Active v1.5 engineering backends:

- Embree
- OptiX

Frozen before v2.1:

- Vulkan
- HIPRT
- Apple RT

Experimental and not promoted:

- `COLLECT_K_BOUNDED`

Usage boundary:

- source-tree execution only: `PYTHONPATH=src:. python ...`
- no package/install claim;
- no `pip install -e .` claim.

## Evidence Chain

Internal readiness:

- `docs/reports/goal1392_v1_5_readiness_decision_validator_refactor_2026-05-06.md`
- `docs/reports/goal1393_v1_5_stable_primitive_claim_evidence_2026-05-06.md`

Fresh-Git pod evidence:

- `docs/reports/goal1393_v1_5_stable_primitive_pod_results/rtdl_pod_env.json`
- `docs/reports/goal1393_v1_5_stable_primitive_pod_results/stable_primitive_evidence.json`

Goal1393 fresh-Git pod commit:

```text
c0b57ae274129aa536e6ae0069f188a138bbefc1
```

Goal1393 pod result summary:

```text
CPU direct ANY_HIT + COUNT_HITS: ok, hit_count 256
Embree direct ANY_HIT + COUNT_HITS: ok, hit_count 256
OptiX direct ANY_HIT + COUNT_HITS: ok, hit_count 256
Prepared OptiX ANY_HIT + COUNT_HITS: ok, hit_count 256
Scalar reductions: all stable scalar primitive cases ok
public_wording_authorized in evidence artifact: false
```

Public wording review:

- `docs/reports/goal1394_v1_5_public_wording_review_packet_2026-05-06.md`
- `docs/reports/goal1394_claude_v1_5_public_wording_review_2026-05-06.md`
- `docs/reports/goal1394_gemini_v1_5_public_wording_review_retry_2026-05-06.md`
- `docs/reports/goal1394_three_ai_v1_5_public_wording_consensus_2026-05-06.md`

Goal1394 consensus commit:

```text
595f4bd8d59892dee645c3034d48cbb3eb3c1bd0
```

3-AI consensus:

- Codex: acceptable.
- Claude: `Verdict: ACCEPTABLE`.
- Gemini retry: `Verdict: ACCEPTABLE`.

## Accepted Public Wording Boundary

The accepted public wording may say:

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

Publication-context warning:

- Claude accepted the wording but noted that the present-tense word "introduces" must not be used in surrounding text that implies a release/tag already happened before the explicit release operation.

## Prohibited Claims

The v1.5 release must not claim:

- whole-application speedup;
- broad NVIDIA RTX, OptiX, or GPU speedup;
- public speedup based on Goal1393 timings;
- package/install support;
- `pip install -e .` support;
- Graph, DB, polygon, Jaccard, KNN, ANN, DBSCAN, Hausdorff, Barnes-Hut, robot, or facility app speedups from this packet;
- `COLLECT_K_BOUNDED` stability;
- active Vulkan/HIPRT/Apple RT implementation work before v2.1;
- movement or replacement of `v1.0`;
- a universal native compute engine replacing Python app-specific control.

## Recommended Release Operation

If the user explicitly authorizes a release operation, use this order:

1. Refresh release-facing docs to say current public release is `v1.5` and preserve `v1.0` as the prior foundation release.
2. Add `docs/release_reports/v1_5/` with a release statement, support matrix, audit report, and tag preparation file using only Goal1393 and Goal1394 accepted wording.
3. Run focused public-doc and v1.5 readiness tests.
4. Run full local discovery if time permits or if docs/tests changed beyond release text.
5. Commit the release package.
6. Create tag `v1.5` at the exact release commit only after explicit authorization.
7. Push the commit and tag.

Do not:

- retag or move `v1.0`;
- tag from a dirty worktree;
- claim package install support;
- add speedup wording unless a separate reviewed exact-subpath speedup packet authorizes it.

## Decision

Release readiness: ready for explicit v1.5 release operation.

Release operation performed by this report: no.

Tag created by this report: no.

Public speedup wording authorized by this report: no.

