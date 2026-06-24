# Goal1197 Claude Review Request: OptiX Slower-App Investigation

Please review the Goal1197 investigation manifest before any new pod run.

Read:

- `docs/reports/goal1197_optix_slower_app_investigation_manifest_2026-04-30.md`
- `docs/reports/goal1197_optix_slower_app_investigation_manifest_2026-04-30.json`
- `docs/reports/goal1196_two_ai_consensus_2026-04-30.md`
- `docs/reports/goal1194_goal1192_public_wording_evidence_batch_final_intake_2026-04-30.md`

Questions:

1. Does the manifest correctly target only the four app paths where OptiX was
   slower than Embree in the accepted Goal1195 evidence?
2. Are the hypotheses and scale sweeps sufficient to distinguish real Embree
   advantage from GPU launch/setup/interface overhead?
3. Is the Jaccard stability rule strict enough after the observed
   chunk-sensitive or nondeterministic parity behavior?
4. Is it correct to include road_hazard_screening and hausdorff_distance only as
   positive controls, not as the main slower-app investigation targets?
5. Does the manifest preserve the no-public-wording/no-release boundary?

Expected output:

- Verdict: `ACCEPT` or `BLOCK`
- Reasons
- Required fixes, if any

If accepted, save as:

`docs/reports/goal1197_claude_optix_slower_app_investigation_review_2026-04-30.md`
