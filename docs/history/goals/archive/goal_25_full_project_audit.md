# Goal 25: Full Project Audit

Goal 25 performs a full-project audit of the current RTDL repository.

Scope:
- source code
- tests
- examples
- key top-level docs
- project framing and current claims
- experiment/reporting artifacts to the extent they affect correctness or honesty

Required collaboration model:
- Claude performs the main external audit
- Codex reviews Claude's findings, revises the repo, and writes responses
- Gemini monitors each major stage and verifies whether the process remains honest and technically consistent
- the round closes only after consensus

Audit expectations:
- be strict about overclaiming
- prioritize correctness, consistency, performance claims, and research-paper honesty
- treat unresolved uncertainty as a finding when it could mislead a reader or user
- distinguish between current local Embree reality and future multi-backend / NVIDIA plans

Closure condition:
- Claude accepts the revised repo state or reports no remaining blockers
- Gemini accepts the monitored process and final state
- Codex records the final consensus note
