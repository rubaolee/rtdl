# Goal 1582: OptiX Collect-K 49153 Noise Isolation

## Verdict

The previous negative targeted `49153` alias point appears to be session/process measurement noise, not a correctness, topology, or candidate-preset problem. A direct `49153`-only 9-repeat run on the same committed pod state showed alias and candidate preset both faster than baseline while preserving parity and expected topology.

## Run Scope

- Pod checkout: `/root/rtdl_goal1545_pod`
- Commit: `63272caeb52ce0210b990878486bbaad824a55db`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Candidate count: `49153`
- Repeats: `9`
- Probe: `scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py`
- Baseline artifact: `/tmp/goal1582_49153_baseline.json`
- Alias artifact: `/tmp/goal1582_49153_alias.json`
- Candidate preset artifact: `/tmp/goal1582_49153_candidate.json`

## Results

| Mode | Accepted | Parity | Topology | Python median ms | Stage total ms | Merge launch ms | Merge sync ms | Carry copy ms | Payload copies |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| Baseline flags | True | True | True | 0.250374 | 0.220958 | 0.072767 | 0.049432 | 0.022302 | 3 |
| Alias flags | True | True | True | 0.242740 | 0.213694 | 0.071658 | 0.049303 | 0.015119 | 1 |
| Candidate preset | True | True | True | 0.239473 | 0.211771 | 0.070734 | 0.050335 | 0.014797 | 1 |

## Interpretation

The isolated direct run supports the derived carry alias mechanism:

- The alias and candidate preset paths both reduce `49153` carry payload copies from `3` to `1`.
- The alias and candidate preset paths both preserve candidate rows, overflow flags, valid counts, native path, and expected topology.
- The candidate preset behaves like the intended alias bundle and does not require the rejected pointer-carry diagnostics.

The broader Goal1581 targeted rerun still remains part of the evidence record because it exposed timing instability. The current conclusion should be narrow: the `49153` slowdown was reproduced as noise in one process/session, then contradicted by a cleaner isolated 9-repeat run. Promotion should still require a final accepted package and external review.

## Claim Boundary

This report does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
