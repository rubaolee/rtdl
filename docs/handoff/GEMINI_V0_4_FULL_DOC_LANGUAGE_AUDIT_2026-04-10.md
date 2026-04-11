# Gemini Task: Full v0.4 Doc Language Audit

Please audit the RTDL documentation for terminology quality and consistency, with
special attention to the post-restart `v0.4` nearest-neighbor line.

Work in this repo:

- `/Users/rl2025/rtdl_python_only`

Write your response to this required file:

- `/Users/rl2025/rtdl_python_only/docs/reports/gemini_v0_4_full_doc_language_audit_review_2026-04-10.md`

## Scope

Audit the live docs for:

- wrong expressions
- unexplained abbreviations
- inconsistent naming
- stale status wording
- dead or misleading content
- terminology that should be expanded on first use

## Priority examples

Check cases like:

- `lsi`
- `pip`
- `pkau`
- `lkau`
- `frn`
- other workload or benchmark shorthand that appears without a clean first-use
  expansion

If an abbreviation is valid, say where it is first explained clearly. If it is
not explained well enough, call that out.

## Priority pages

At minimum, inspect:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/v0_4_application_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/workloads_and_research_foundations.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/llm_authoring_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_4/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_4/release_statement.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_4/support_matrix.md`

You may inspect more files if needed.

## Output format

Use exactly these sections:

1. `Verdict`
2. `Findings`
3. `Dead Links Or Dead Content`
4. `Abbreviation And Naming Issues`
5. `Recommended Fix Order`

## Review standard

- Be precise, not broad
- Quote exact file paths
- Identify exact wording that is wrong, stale, inconsistent, or unclear
- Separate real issues from acceptable bounded wording
- Do not speculate about code; this is a documentation-language audit
