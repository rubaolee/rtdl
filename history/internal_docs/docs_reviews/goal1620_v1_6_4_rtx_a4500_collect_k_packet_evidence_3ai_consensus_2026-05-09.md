# Goal1620 v1.6.4 RTX A4500 Collect-K Packet Evidence 3-AI Consensus

Date: 2026-05-09

## Verdict

ACCEPTED as representative RTX required-backend packet-execution evidence.

This consensus does not authorize public speedup wording, true zero-copy
wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, release
tags, or release action.

## Reviewed Files

- `docs/reports/goal1620_v1_6_4_rtx_a4500_collect_k_packet_evidence_2026-05-09.md`
- `tests/goal1620_v1_6_4_rtx_a4500_collect_k_packet_evidence_test.py`
- `docs/reports/goal1618_v1_6_4_rtx_a4500_required_backend_packet_2026-05-09.json`
- `docs/reports/goal1618_v1_6_4_rtx_a4500_required_backend_packet_2026-05-09.md`
- `docs/reviews/goal1620_v1_6_4_rtx_a4500_collect_k_packet_evidence_claude_review_2026-05-09.md`
- `docs/reviews/goal1620_v1_6_4_rtx_a4500_collect_k_packet_evidence_gemini_review_2026-05-09.md`

## Evidence

- Pod endpoint: `root@213.173.108.199 -p 18169`.
- Git commit: `a0dcb56cc2f727774a6abcb6e25bcf746ece9d78`.
- GPU: `NVIDIA RTX A4500`, driver `550.127.05`, memory `20470 MiB`.
- CUDA build prefix: `/usr/local/cuda-12.4`.
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`.
- Embree runtime probe: `(3, 12, 2)`.
- OptiX runtime probe: `(8, 0, 0)`.
- Goal1618 packet accepted with required backends `fake_native`, `embree`, and
  `optix`.
- Goal1614 bounds stress subpackage accepted.
- Goal1615 reduced-copy/materialization-count benchmark subpackage accepted.
- Claude returned `ACCEPTED` with no blockers.
- Gemini returned `ACCEPTED` with no blockers.

## Consensus

Codex, Claude, and Gemini agree that Goal1620 satisfies the representative RTX
required-backend packet-execution evidence item in the v1.6.4 collect-k chain.
The result is execution and materialization-count evidence only; timing remains
diagnostic and all public-performance and stable-promotion claims remain
blocked.

## Next Step

If the project wants to decide stable `COLLECT_K_BOUNDED` promotion, create a
separate stable-promotion decision package and request fresh Claude and Gemini
review. Do not infer stable promotion from Goal1620 alone.
