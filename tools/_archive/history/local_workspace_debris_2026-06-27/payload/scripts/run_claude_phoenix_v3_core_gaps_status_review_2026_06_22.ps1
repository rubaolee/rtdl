$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review"
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $RepoRoot "docs\reviews\claude_phoenix_v3_core_gaps_status_and_next_work_after_claude_review_2026-06-22.raw.md"
$Err = Join-Path $RepoRoot "docs\reviews\claude_phoenix_v3_core_gaps_status_and_next_work_after_claude_review_2026-06-22.stderr.txt"

Set-Location $RepoRoot

$Prompt = @'
You are Claude acting as an independent external reviewer for Phoenix V3.

Read these files from the current repository:

1. docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md
2. docs/reviews/call_for_review_phoenix_v3_core_gaps_status_and_next_work_after_claude_2026-06-22.md
3. docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md
4. docs/reports/phoenix_v3_grouped_stream_runner_route_pod_ab_2026-06-22.md
5. docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md

Task:
Return a protocol-shaped external review. You must include exactly one verdict
label from:

- release_ready
- approve_blocked_not_release
- block_p1
- block_p0

Please answer these specific questions:

1. Does the current Phoenix V3 status still map to approve_blocked_not_release,
   or has new evidence moved it to block_p1 or block_p0?
2. Is the AABB M2.1 focused result valid Set-A productized-path evidence, or
   should it be demoted because of slower prepare, harness shape, or some other
   issue?
3. Should the Set A / Set B release bar become the working bar, be amended, or
   be rejected?
4. Which second Set-A runner-backed route should be prioritized next?
5. Are the four gaps stated correctly, with Gap 1 as the parent blocker?
6. Is any current action drifting into benchmark-app development instead of
   language/runtime work?
7. What exact focused evidence is sufficient before another all-app pod run?
8. Are any docs or generated packets still likely to mislead users into
   thinking V3 is release-ready?

Requirements:
- Findings first, highest severity first.
- Include a non-authorization block that explicitly says whether V3 release,
  public speedup wording, broad V3-over-V2 wording, true-zero-copy wording, and
  all-app rerun authorization are allowed.
- State whether AABB M2.1 may proceed toward M7 review.
- State whether a Codex consensus report should accept, amend, or reject your
  verdict.
- Do not write files. Return the review text only.
'@

$Prompt | & $Claude --print --dangerously-skip-permissions > $Out 2> $Err
