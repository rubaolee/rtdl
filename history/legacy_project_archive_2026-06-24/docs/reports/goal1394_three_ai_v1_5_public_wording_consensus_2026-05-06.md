# Goal 1394 - 3-AI v1.5 Public Wording Consensus

Date: 2026-05-06

## Packet Under Review

- `docs/reports/goal1394_v1_5_public_wording_review_packet_2026-05-06.md`

## Evidence Inputs

- `docs/reports/goal1393_v1_5_stable_primitive_claim_evidence_2026-05-06.md`
- `docs/reports/goal1393_v1_5_stable_primitive_pod_results/rtdl_pod_env.json`
- `docs/reports/goal1393_v1_5_stable_primitive_pod_results/stable_primitive_evidence.json`

Fresh-Git pod evidence commit:

```text
c0b57ae274129aa536e6ae0069f188a138bbefc1
```

Review packet commit:

```text
880ef556f8f99090e2fd7de998680290d9d0e571
```

## Reviews

Codex review:

- Result: acceptable.
- Rationale: The packet is bounded to the Goal1393 stable primitive evidence, avoids public speedup and whole-app claims, preserves source-tree usage, keeps `COLLECT_K_BOUNDED` experimental, keeps Vulkan/HIPRT/Apple RT frozen before v2.1, and does not authorize release/tag action.

Claude review:

- File: `docs/reports/goal1394_claude_v1_5_public_wording_review_2026-05-06.md`
- Explicit verdict: `Verdict: ACCEPTABLE`
- Note: Claude flagged a minor publication-context risk around the present-tense word "introduces"; it is acceptable because the packet framing blocks release/tag action, but final public placement must not imply a release has already happened before an explicit release/tag operation.

Gemini review:

- First attempt file: `docs/reports/goal1394_gemini_v1_5_public_wording_review_2026-05-06.md`
- First attempt status: unusable. The artifact records `MODEL_CAPACITY_EXHAUSTED` / HTTP 429 errors and a controlled timeout, with no explicit verdict. It does not count toward consensus.
- Retry file: `docs/reports/goal1394_gemini_v1_5_public_wording_review_retry_2026-05-06.md`
- Retry explicit verdict: `Verdict: ACCEPTABLE`

## Consensus Decision

3-AI consensus is achieved for the Goal1394 public v1.5 wording packet:

- Codex: acceptable.
- Claude: acceptable.
- Gemini: acceptable on retry.

The accepted wording is limited to generic primitive readiness:

- stable primitive names: `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, `REDUCE_INT(COUNT|SUM)`;
- Goal1393 bounded fixture evidence: CPU, Embree, and OptiX direct `ANY_HIT + COUNT_HITS` returned hit count `256`;
- Goal1393 bounded fixture evidence: prepared OptiX `ANY_HIT + COUNT_HITS` returned hit count `256`;
- scalar reductions returned expected values for all stable scalar primitive names;
- Embree and OptiX are active v1.5 engineering backends;
- Vulkan, HIPRT, and Apple RT remain frozen before v2.1;
- `COLLECT_K_BOUNDED` remains experimental;
- current usage remains source-tree execution with `PYTHONPATH=src:. python ...`.

## Remaining Blocks

This consensus does not by itself perform a release/tag action.

Still blocked until a separate explicit release operation:

- creating or moving any release tag,
- claiming that public v1.5 has already been released,
- changing `v1.0`,
- publishing package/install support,
- adding public speedup wording,
- adding broad NVIDIA RTX wording,
- adding whole-application performance claims.

## Final Status

Status: Accepted with 3-AI consensus for bounded public v1.5 wording.

