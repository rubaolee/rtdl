# Goal 449: v0.7 Packaging Manifest Validation Gate

Date: 2026-04-16

## Purpose

Add a non-destructive validation gate for the Goal 448 packaging manifest.

The gate checks that the important package paths exist and that invalid review
attempts are not counted as valid consensus. It does not stage, commit, tag,
merge, or push.

## Acceptance Criteria

- A script checks the core runtime, test, script, release-doc, evidence, and
  consensus paths named by the packaging manifest.
- The script writes JSON evidence.
- The JSON evidence reports zero missing required files.
- The JSON evidence explicitly distinguishes invalid preserved review artifacts
  from valid consensus artifacts.
- Codex and one external AI review accept the gate before closure.
