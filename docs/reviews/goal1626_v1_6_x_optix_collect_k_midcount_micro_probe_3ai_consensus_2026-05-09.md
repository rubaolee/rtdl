# Goal1626 v1.6.x OptiX Collect-K Midcount Micro-Probe 3-AI Consensus

## Verdict

`accepted_as_internal_micro_probe_evidence_only`

Codex, Claude, and Gemini agree that the Goal1626 interpretation is supported by
the A4500 micro-probe artifacts and that its claim boundary is appropriately
conservative.

## Consensus Points

- The controlled wrapper run completed successfully on `NVIDIA RTX A4500`,
  driver `550.127.05`, at commit `d659bf0e80725128715e5758bb0ec1a3c8fc66ce`.
- Baseline and gated modes preserved parity for counts `65537`, `98305`, and
  `131072`.
- Count `65537` is the only tested row with a clear topology-backed win:
  carry payload copies dropped from `5` to `0`.
- Counts `98305` and `131072` do not provide accepted speedup evidence because
  their gated topology does not reduce carry payload copies relative to
  baseline.
- The next performance direction should target merge launch/sync behavior, not
  broader threshold-4 sweeps.

## Review Notes

- Claude accepted the interpretation and recommended two clarifications:
  explicitly state the single-sample limitation and distinguish carry payload
  removal from structural carry-copy topology. Both clarifications were added to
  the interpretation note.
- Claude also observed that the generated summary artifact retains the Goal1625
  runner label. The raw artifact was not rewritten; the interpretation note now
  documents that the Goal1626 note reused the existing Goal1625 runner.
- Gemini approved the interpretation and found no substantive concerns.

## Claim Boundary

This consensus accepts the evidence only as internal v1.6.x performance
diagnostic material. It does not authorize public speedup wording, true
zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording,
whole-application speedup claims, release tags, or release action.
