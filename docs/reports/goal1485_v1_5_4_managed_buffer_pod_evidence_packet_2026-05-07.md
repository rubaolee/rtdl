# Goal 1485: v1.5.4 Managed Buffer Pod Evidence Packet

## Verdict

Accepted as local pre-pod preparation for v1.5.4 Python+RTDL managed-buffer allocation evidence.

This goal does not need a pod. It prepares the exact packet and runner that should be used once a pod is running.

## What It Prepares

The packet runner records:

- source commit
- platform details
- `nvidia-smi` output
- `nvcc --version` output
- managed-buffer descriptor
- RTDL-owned lifecycle
- allocation evidence envelope
- transfer counts
- hardware identity
- backend version
- claim guardrails

The local default mode is fail-closed: it uses `synthetic_contract_only`, records a nonzero host-to-device transfer, and does not mark real NVIDIA evidence.

## Pod Command

From a clean Linux checkout on a real NVIDIA pod:

```bash
git fetch origin
git reset --hard origin/main
chmod +x scripts/goal1485_v1_5_4_managed_buffer_pod_evidence_runner.sh
RESULT_DIR=docs/reports/goal1485_v1_5_4_managed_buffer_pod_results_2026-05-07 \
  scripts/goal1485_v1_5_4_managed_buffer_pod_evidence_runner.sh
```

The runner writes:

- `docs/reports/goal1485_v1_5_4_managed_buffer_pod_results_2026-05-07/goal1485_pod_environment.log`
- `docs/reports/goal1485_v1_5_4_managed_buffer_pod_results_2026-05-07/goal1485_managed_buffer_pod_evidence.log`
- `docs/reports/goal1485_v1_5_4_managed_buffer_pod_results_2026-05-07/goal1485_managed_buffer_pod_evidence_2026-05-07.json`
- `docs/reports/goal1485_v1_5_4_managed_buffer_pod_results_2026-05-07/goal1485_managed_buffer_pod_evidence_2026-05-07.md`

## Claim Boundary

Even if the pod packet produces `true_zero_copy_evidence_candidate=True`, that is still only candidate evidence.

The packet keeps these flags false:

- `true_zero_copy_authorized`
- `public_speedup_wording_authorized`
- `whole_app_speedup_claim_authorized`
- `stable_public_primitive_authorized`
- `partner_tensor_handoff_authorized`
- `release_action_authorized`

## Pod Efficiency Notes

The pod should not be used until the next task explicitly needs real NVIDIA evidence.

Once started, run the packet immediately after syncing `origin/main`. The runner performs environment capture and evidence packet generation in one command, so it should avoid wasting paid GPU time on setup ambiguity.

## Files

- `scripts/goal1485_v1_5_4_managed_buffer_pod_evidence_packet.py`
- `scripts/goal1485_v1_5_4_managed_buffer_pod_evidence_runner.sh`
- `tests/goal1485_v1_5_4_managed_buffer_pod_evidence_packet_test.py`
- `docs/reports/goal1485_v1_5_4_managed_buffer_pod_evidence_packet_2026-05-07.md`

