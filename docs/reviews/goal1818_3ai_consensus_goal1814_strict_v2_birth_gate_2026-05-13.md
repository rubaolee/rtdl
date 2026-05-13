# Goal1818: 3-AI Consensus for Goal1814 Strict v2.0 Birth Gate

Date: 2026-05-13

Verdict: `accept-with-boundary`

## Scope

This consensus evaluates the stricter v2.0 birth gate introduced by Goal1814.
It supersedes the earlier Goal1810/Goal1813 release-ready conclusion and keeps
the current Python+partner path in preview status.

This consensus does not tag, publish, or move a release. It blocks v2.0
publication until the stricter blockers are solved or explicitly removed from
the v2.0 public scope by a later 3-AI consensus.

## Inputs

Codex authored Goal1814 after the user rejected the earlier
`release-ready-with-boundary` interpretation as too weak for v2.0.

External reviews:

- Gemini first response:
  `docs/reviews/goal1815_gemini_review_goal1814_strict_v2_birth_gate_2026-05-13.md`
- Claude:
  `docs/reviews/goal1816_claude_review_goal1814_strict_v2_birth_gate_2026-05-13.md`
- Gemini follow-up:
  `docs/reviews/goal1817_gemini_followup_review_goal1814_strict_v2_birth_gate_2026-05-13.md`

Goal1815 is recorded but not counted as a substantive accepting technical
review because it declined to evaluate the gate. Goal1816 and Goal1817 are the
substantive external reviews. Claude and Gemini are distinct from Codex and
from each other; Codex+Codex is invalid and is not counted.

## Consensus Findings

The strict birth gate is accepted:

- Goal1814 cleanly supersedes Goal1810/Goal1813 without deleting or devaluing
  the existing preview evidence.
- README, docs index, partner tutorial, and roadmap gate now describe the
  current Python+partner path as preview, not released v2.0.
- The six blockers are first-class release blockers:
  - true zero-copy;
  - direct device-pointer handoff;
  - broad RT-core speedup evidence;
  - whole-application acceleration evidence;
  - arbitrary PyTorch/CuPy acceleration boundaries;
  - package-install/source-tree release scope.
- v2.0 remains `needs-more-evidence`.

## Boundaries Incorporated

Claude's `accept-with-boundary` review raised two useful refinements, now
incorporated into Goal1814:

- the arbitrary PyTorch/CuPy blocker requires a positive rule for what RTDL does
  accelerate, not only a list of blocked claims;
- the package-install/source-tree blocker can be resolved by a source-tree-only
  release statement only if that statement is ratified by 3-AI consensus.

## Final Decision

`accept-with-boundary`: Goal1814 is now the governing v2.0 release gate.

The current Python+partner path is real preview evidence. It is not a v2.0
release. v2.0 is born only after the six blockers are solved or explicitly
removed by a new 3-AI consensus based on reviewed evidence.
