# Gemini CLI Notes

## Purpose

This document records the observed behavior of Gemini CLI during the RTDL
review-and-revision workflow on this Mac.

The goal is operational clarity, not criticism of the model itself. The main
problems observed so far are about CLI/session behavior, not about Gemini's
ability to reason about the project.

## Confirmed Environment Notes

- Gemini CLI is installed locally and can authenticate successfully.
- The CLI repeatedly prints this warning:

```text
Keychain initialization encountered an error: Cannot find module '../build/Release/keytar.node'
Using FileKeychain fallback for secure storage.
Loaded cached credentials.
```

This warning is **not** the main blocker.

What it means:

- the native `keytar` module is unavailable,
- Gemini falls back to file-based credential storage,
- authentication still succeeds afterward.

So the `keytar` warning is noisy, but not fatal.

## Actual Failure Modes Observed

### 1. Progress narration before the answer

Gemini often prints lines such as:

- `I will read the specified files...`
- `I will now verify the presence and content...`

before the actual review content begins.

This matters because:

- redirected output files may contain mixed progress text plus final report text,
- and some runs terminate before the final report is fully written.

### 2. Long hangs without clean process completion

For larger review prompts, Gemini CLI sometimes appears to continue running
without closing stdout in a predictable amount of time.

Symptoms:

- output file stays empty for a long time,
- or the process prints only setup/progress text and then stalls,
- or a timeout is needed to recover control.

### 3. Incomplete redirected artifacts

Some `gemini -p ... > file` runs produced:

- empty files,
- truncated files,
- or files containing only the opening progress narration.

This makes non-interactive artifact capture unreliable for long reviews.

### 4. Tool/file-access restrictions inside Gemini's environment

At least one implementation review failed because Gemini could not read files
under `build/` due to its own ignore-pattern configuration.

This was not a repository bug. It was a Gemini review-environment limitation.

The practical workaround was:

- copy generated artifacts into the archived review snapshot,
- then ask Gemini to read those snapshot paths instead.

### 5. Better results in shorter or TTY-style runs

Shorter prompts and TTY-style invocations have generally behaved better than
large single-shot redirected prompts.

That does not fully eliminate hangs, but it improves the odds of getting a
usable response.

## Operational Interpretation

The important conclusion is:

> The main issue is Gemini CLI output/session reliability on this machine, not
> Gemini's core reasoning ability.

So when a review artifact is missing or truncated, do **not** immediately assume:

- the review content is invalid,
- the model disagrees,
- or the repository is at fault.

First check whether the CLI session itself failed to produce a stable artifact.

## Recommended Workflow For Future RTDL Review Rounds

### Preferred prompt style

- keep prompts short and tightly scoped,
- avoid asking for too many files at once,
- ask for specific structured sections,
- and separate setup review from implementation review.

### Preferred artifact paths

- avoid asking Gemini to inspect files only under `build/`,
- copy important generated artifacts into the round archive under
  `history/revisions/<round>/project_snapshot/`,
- then review those archived copies.

### Preferred execution style

- prefer shorter TTY-style calls when a direct saved artifact is required,
- or use a controlled timeout wrapper if the CLI is prone to hanging,
- and treat partial/progress-only output as an environment artifact, not a
  final review.

### Preferred review decomposition

Instead of one large prompt, split the review into:

1. scope or pre-implementation review,
2. implementation/code review,
3. artifact/report review,
4. final consensus confirmation.

### Required archival honesty

If a Gemini artifact is partial or truncated:

- save it,
- label it honestly,
- do not treat it as a final consensus artifact,
- and issue a narrower follow-up prompt.

## RTDL-Specific Guidance

For this repository, the safest Gemini review workflow is:

1. review docs/spec first,
2. review code next,
3. copy generated outputs into `history/revisions/.../project_snapshot/`,
4. review the copied outputs,
5. request a short final-decision pass.

This pattern reduces failures from ignored build paths and oversized prompts.

## Status

These notes should be treated as live operational guidance for future Codex ↔
Gemini review rounds in RTDL until the CLI behavior becomes more stable.
