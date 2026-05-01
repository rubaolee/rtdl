# Goal1004 RTX A5000 Artifact Consensus

Date: 2026-04-26

## Verdict

Status: `ACCEPT`.

The saved RTX A5000 pod artifacts are sufficient to record the narrow fact that all 17 current RTX app gates executed successfully on real RTX A5000 hardware at commit `914122ecd2f2c73f6a51ec2d5b04ca3d575d5681`.

This consensus does not authorize public speedup claims. Speedup claims still require same-semantics baselines, phase-separation review, and release-level wording review.

## Evidence

- Pod run summary: `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_pod_run_summary_2026-04-26.md`
- Final artifact report: `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_final_artifact_report_2026-04-26.md`
- Final merged summary: `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_final_merged_summary_2026-04-26.json`
- Final artifact bundle: `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_artifacts_with_report_2026-04-26-v2.tgz`
- Local audit: `docs/reports/cloud_2026_04_26/goal1004_rtx_a5000_artifact_audit_2026-04-26.md`

## Review Trail

- Codex local audit: `ACCEPT`; `scripts/goal1004_rtx_a5000_artifact_audit.py` reports `status: ok`.
- Claude external review: `ACCEPT`; report saved at `docs/reports/goal1004_claude_external_review_2026-04-26.md`.
- Gemini external review: `ACCEPT`; report saved at `docs/reports/goal1004_gemini_external_review_2026-04-26.md`.

Gemini's review is treated as a limited secondary signal because it primarily confirmed artifact presence and explicitly did not perform deep semantic analysis. Claude's review is the substantive external review for the hard evidence and honesty boundary.

## Remediation From Review

Claude recommended two non-blocking audit improvements:

- Add a machine check that the merged run was not a dry run.
- Cross-check RTX A5000 hardware identity from the merged JSON `nvidia_smi` field, not only from the human-authored run summary.

Both were implemented in `scripts/goal1004_rtx_a5000_artifact_audit.py` and covered by `tests/goal1004_rtx_a5000_artifact_audit_test.py`.

## Incident Handling

The first graph group run failed because the pod image lacked GEOS development files, so the native oracle could not link `-lgeos_c` for graph BFS and triangle-count validation. This was remediated by installing `libgeos-dev` and `pkg-config` on the pod and rerunning only Group F. The final v2 bundle contains the passing graph artifact.

The incident is not release-blocking because the cause was a missing system dependency, not a source-code change; the failed first bundle is preserved; and the final merged summary reports 17 entries, zero failures, and `status: ok`.

## Boundary

The accepted claim is only:

> RTDL built the OptiX backend and executed all 17 current grouped RTX app gates on an RTX A5000 pod at commit `914122ecd2f2c73f6a51ec2d5b04ca3d575d5681`.

The accepted claim is not:

- a public speedup claim,
- a whole-app acceleration claim,
- a DBMS or SQL-engine claim,
- a full KNN/ANN/DBSCAN/Barnes-Hut/polygon-GIS replacement claim,
- or release authorization for v1.0.
