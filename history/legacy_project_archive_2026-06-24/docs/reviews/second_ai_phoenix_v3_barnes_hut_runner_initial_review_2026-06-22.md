# Second-AI Review: Phoenix V3 Barnes-Hut Runner Initial Implementation

Date: 2026-06-22
Reviewer: Aquinas (Codex multi-agent second AI)
Packet under review: Phoenix V3 Barnes-Hut prepared-execution runner wrapping before fixed POD evidence

## Verdict

`blocked_needs_fix`

## Findings

1. `--skip-historical-optix` could still produce `step1_replacement_candidate=True` and `runtime_sourced_material_gain=True`. The reviewer said this violated the required dual comparison for a pod packet. The skip path may remain only as local smoke, or it must force candidate/material fields false.

2. The pod A/B script had no correctness-equivalence gate. It always ran the large rows with skipped CPU validation and collected checksums, but did not compare runner versus existing fused-control outputs.

3. The prepared-execution helper could overstate trunk execution from weak output metadata. It treated missing output contract as matching and did not require returned partner or source/target/tree counts to match the request before setting `runtime_trunk_executes_end_to_end=True`.

## Boundary Review

The reviewer found the helper app-agnostic: generic name, generic primitive, no Barnes-Hut naming in the runtime helper, and app-shaped primitive terms remain forbidden in the prepared-session key layer. The reviewer also found release/public speedup/RT-core/true-zero-copy/all-app flags mostly closed.

## Required Fixes Applied After This Review

- `scripts/v3_phoenix_barnes_hut_runner_parity_pod_ab.py`: `--skip-historical-optix` is smoke-only and cannot produce Step-1 candidate/material status.
- `scripts/v3_phoenix_barnes_hut_runner_parity_pod_ab.py`: added `runner_control_equivalence_rows` and `runner_control_output_equivalence_all_sizes` gate over contribution count plus checksum X/Y parity.
- `src/rtdsl/prepared_execution.py`: `runtime_trunk_executes_end_to_end` for aggregate-tree fused vector sum now requires exact output contract, partner, and source/target/tree count agreement.

## Non-Authorization

This review authorized no release, no broad V3-over-V2 wording, no public speedup wording, no true-zero-copy wording, and no all-app pod run.
