# Goal1626 v1.6.x OptiX Collect-K Midcount Micro-Probe Interpretation

## Verdict

`midcount_micro_probe_recorded_no_public_claim`

The controlled A4500 micro-probe confirms that the prior broad rerun was too
large as a measurement package, not evidence of a broken OptiX environment. A
small wrapper run covering counts `65537`, `98305`, and `131072` completed in
8 seconds with parity preserved for baseline and gated modes.

## Evidence

- Repository commit: `d659bf0e80725128715e5758bb0ec1a3c8fc66ce`.
- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Runner: `scripts/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe.py`.
- Scope: `rounds=1`, `repeats=1`, counts `65537 98305 131072`.
- Statistical caveat: this is a single-round, single-repeat micro-probe, so it
  provides topology and direction evidence only; it does not provide a variance
  estimate or public speedup claim.
- Summary artifact: `docs/reports/goal1626_v1_6_x_optix_collect_k_midcount_micro_probe_2026-05-09.json`.
- Round artifacts:
  - `docs/reports/goal1626_v1_6_x_optix_collect_k_midcount_micro_probe_baseline_round1.json`
  - `docs/reports/goal1626_v1_6_x_optix_collect_k_midcount_micro_probe_gated_round1.json`
- Artifact identity note: the summary artifact was produced by the existing
  Goal1625 runner, so its internal `goal` and generated claim-boundary strings
  retain the runner's `Goal1625` label. This interpretation note is the Goal1626
  wrapper around that controlled reuse, and the raw generated artifact was not
  edited after collection.

## Results

| Count | Baseline total ms | Gated total ms | Delta ms | Payload copies baseline/gated | Parity |
|---:|---:|---:|---:|---:|---|
| 65537 | 0.382622 | 0.350152 | -0.032470 | 5/0 | true |
| 98305 | 0.358881 | 0.358191 | -0.000690 | 4/4 | true |
| 131072 | 0.367112 | 0.363302 | -0.003810 | 0/0 | true |

## Interpretation

The threshold-4 gate is still useful when it actually removes carry payload
copies, as shown by count `65537`. The same gate does not create meaningful
copy-reduction at `98305`, where both baseline and gated modes still report
four payload copies, or at `131072`, where neither mode reports payload copies.
Those two rows should be treated as near-zero or noise-level timing deltas, not
as accepted speedup evidence.

At count `65537`, the gate removes carry payload movement, not the structural
carry-copy topology itself: `carry_copies` remains present while
`carry_payload_copies` drops from `5` to `0`.

The strongest remaining optimization target is still the merge path. Prior
Goal1625 stage profiles showed that the largest remaining native-side time is
merge launch/sync work after carry payload copies are reduced. This micro-probe
adds a guardrail: do not spend pod time scaling the same broad threshold-4
package unless the next experiment either changes the merge/sync mechanism or
changes the gate so it removes payload copies for a newly targeted topology.

## Next Work

1. Keep `COLLECT_K_BOUNDED` experimental.
2. Do not promote threshold-4 as a stable public performance feature from this
   micro-probe.
3. Replace broad reruns with narrow probes: one hypothesis, one or a few
   topology-sensitive counts, hard external timeout, and small `rounds/repeats`
   first.
4. Prefer the next implementation attempt in the merge/sync area rather than
   another larger threshold-4 sweep.

## Claim Boundary

This note is internal v1.6.x performance evidence only. It does not authorize
public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED`
promotion, broad RTX/GPU wording, whole-application speedup claims, release
tags, or release action.
