$ErrorActionPreference = "Stop"

$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Repo

$env:PYTHONPATH = "src;."

py -3 scripts\v3_phoenix_m70_m71_claude_backfill_intake.py `
    --json-out docs\rebuild\v3\phoenix_v3_m70_m71_claude_backfill_intake_after_claude_2026-06-24.json `
    --md-out docs\reports\phoenix_v3_m70_m71_claude_backfill_intake_after_claude_2026-06-24.md

py -3 scripts\v3_phoenix_m70_m71_goal_completion_audit.py `
    --json-out docs\rebuild\v3\phoenix_v3_m70_m71_goal_completion_audit_after_claude_2026-06-24.json `
    --md-out docs\reports\phoenix_v3_m70_m71_goal_completion_audit_after_claude_2026-06-24.md

py -3 scripts\v3_phoenix_m70_m71_final_3ai_consensus.py `
    --json-out docs\rebuild\v3\phoenix_v3_m70_m71_final_3ai_consensus_after_claude_2026-06-24.json `
    --md-out docs\reports\phoenix_v3_m70_m71_final_3ai_consensus_after_claude_2026-06-24.md

py -3 -m unittest `
    tests.v3_phoenix_m70_m71_final_3ai_consensus_test `
    tests.v3_phoenix_m70_m71_goal_completion_audit_test `
    tests.v3_phoenix_m70_m71_claude_backfill_intake_test `
    tests.v3_phoenix_m70_m71_claude_backfill_packet_gate_test `
    tests.v3_release_wording_gate_test

py -3 scripts\run_test_matrix.py `
    --group v3_rebuild `
    --json-out docs\reports\phoenix_v3_m70_m71_after_claude_v3_rebuild_2026-06-24.json
