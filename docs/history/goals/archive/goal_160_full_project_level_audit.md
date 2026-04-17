# Goal 160: Full Project-Level Audit

## Why

Before starting `v0.3`, the repository needs one explicit project-level audit
package that accounts for:

- every tracked doc file
- every tracked goal file
- every tracked code file in the current source/test/example/script surface

The package must also make the audit method explicit:

- per-item local correctness/coverage checks
- per-item AI review coverage through audited matrices
- final three-AI consensus

## Required Output

The final audit package must include:

1. **Docs matrix**
   - every tracked markdown doc file
   - one local correctness check
   - one AI-review approval reference

2. **Goals matrix**
   - every tracked `docs/goal_*.md` file
   - one local flow-correctness check
   - one AI flow-check reference
   - one AI approval reference

3. **Code matrix**
   - every tracked source/test/example/script code file
   - one local correctness check
   - one test-evidence entry if needed
   - one AI check reference
   - one AI approval reference

4. **Final report**
   - summary counts
   - any explicit exemptions or historically exempt planning artifacts
   - any remaining informational caveats

5. **Final consensus**
   - Claude review
   - Gemini review
   - Codex consensus

## Acceptance

- every tracked doc file is listed in the docs matrix
- every tracked goal file is listed in the goals matrix
- every tracked code file is listed in the code matrix
- the final report links those matrices directly
- Claude review saved
- Gemini review saved
- Codex consensus saved
