# Goal 409: Repo-Wide File Status Audit

## Objective

Perform a total repository file audit for the released `v0.6.1` line.

This audit must examine every tracked file in the repository, regardless of
category, including:

- source code
- tests
- examples
- tutorials
- reports
- handoffs
- release docs
- historical docs
- scripts
- schemas
- generated-supporting files that are intentionally tracked

## Required audit questions for each file

For every audited file, record at least:

1. file path
2. file category
3. current role
4. status
   - live
   - historical
   - transitional
   - unclear
5. correctness status
   - correct
   - needs review
   - incorrect
6. content freshness
   - current
   - stale
   - obsolete
7. dead / unused / misleading content assessment
8. action recommendation
   - keep
   - revise
   - archive
   - delete candidate
   - investigate further

## Required outputs

1. one master report describing:
   - audit method
   - repo-wide findings
   - major risk clusters
   - cleanup recommendations
2. one per-file record dataset or ledger covering every tracked file
3. one AI checker review
4. one AI verifier review
5. one final independent AI proof/review over the whole audit package
6. one Codex consensus closure

## AI role split

- AI 1: checker
  - performs the primary repo-wide audit pass
- AI 2: verifier
  - checks the checker's work for omissions, bad classifications, and weak logic
- AI 3: final proof
  - reviews the whole package and states whether the audit is credible enough to rely on

## Acceptance rule

This goal is not closed until:

- every tracked file has a recorded entry
- the master report exists
- the checker review exists
- the verifier review exists
- the final proof review exists
- Codex has written the final closure note
