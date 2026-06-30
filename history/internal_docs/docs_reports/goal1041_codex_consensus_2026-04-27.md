# Goal1041 Codex Consensus

Date: 2026-04-27

## Scope

Goal1041 compares corrected local macOS CPU/Embree/SciPy timings against remote RTX A5000 OptiX phase timings for the four Goal1038 apps.

Reviewed:

- `docs/reports/goal1041_internal_rtx_vs_local_baseline_comparison_2026-04-27.md`
- Goal1036 corrected local baseline artifacts
- Goal1038 RTX pod artifacts
- Goal1040 comparison-readiness review

## Consensus Verdict

Status: `accepted_internal_engineering_comparison_only`.

The report is accepted as internal engineering evidence. It correctly preserves the important boundaries:

- local baselines and RTX timings are from different machines;
- RTX values are phase timings, not whole-app timings;
- Group B used `skip_validation=true`;
- cloud group summaries still lack git source commit traceability;
- no public speedup, release, or NVIDIA superiority claim is authorized.

## Engineering Direction

The next useful work is not another pod run. The next useful work is local implementation and measurement work to reduce overhead before paying for more cloud time:

- source-commit injection for future pod artifacts;
- `skip_validation=false` mode for claim-grade Group B reruns;
- same-machine Linux baseline harness;
- native reduction / lower-copy paths for the four prepared summary apps.

## Boundary

This consensus does not authorize public speedup wording or release. It closes only the internal comparison/reporting step.
