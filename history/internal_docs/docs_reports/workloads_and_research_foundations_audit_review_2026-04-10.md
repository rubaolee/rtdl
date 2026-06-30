# Workloads And Research Foundations Audit Review

Date: 2026-04-10

Scope:

- `/Users/rl2025/rtdl_python_only/docs/workloads_and_research_foundations.md`

Consensus basis:

- Codex consensus:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-10-codex-consensus-workloads-and-research-foundations-audit.md`
- Claude review:
  - `/Users/rl2025/rtdl_python_only/docs/reports/claude_workloads_and_research_foundations_audit_review_2026-04-10.md`
- Gemini review:
  - `/Users/rl2025/rtdl_python_only/docs/reports/gemini_workloads_and_research_foundations_audit_review_2026-04-10.md`

Resolved in this slice:

- corrected the RTNN citation from the previously wrong SIGMOD-style entry to
  the verified PPoPP '22 entry
- reduced redundant RayJoin section repetition by collapsing the repeated paper
  mapping into one `RayJoin-centered spatial workloads` section
- standardized remaining ACM-linked DOI entries in this page to `doi.org`
- added an explicit note explaining why `ray_tri_hitcount` appears in the page
  without being framed as a named paper-reproduction target
- strengthened the Jaccard/overlap wording so it looks grounded rather than
  defensive
- clarified the X-HD DOI placeholder wording

External review result:

- Claude: pass with minor notes
- Gemini: pass
- no blocking findings remain

Residual risks:

- this page is now clean, but it is still a curated workload/paper map rather
  than a full bibliography of every archived RTDL research direction
- the X-HD DOI line will need a future update once the public DOI is available
- when `v0.4` is formally released, the `Active v0.4 preview workload surface`
  heading will need the expected status update

Closure judgment:

- the page is factually sound for current public use
- the prior RTNN citation error is fixed
- the page now closes under Codex + Claude + Gemini review
