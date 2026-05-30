# Goal2733: Public Claim Boundary Guard After Primitive-First Correction

Date: 2026-05-30
Status: accepted as documentation guardrail

## Purpose

Goal2726 contains useful but asymmetric diagnostic ratios comparing an older whole-call native path against a prepared v2.5 path. Claude's Goal2729 review correctly warned that those ratios must not leak into public or learner-facing performance wording.

Goal2733 adds a mechanical guard:

- learner-facing docs may describe the primitive-first design rule;
- learner-facing docs must not quote the Goal2726 diagnostic ratios (`64.018x`, `342.722x`, or nearby exact table values);
- detailed diagnostic ratios remain in `docs/reports/`, where their asymmetry is documented.

## Scope

The guard scans:

- root `docs/*.md` learner-facing files;
- `docs/tutorials/**/*.md`;
- `docs/learn/**/*.md`;
- `docs/rtdl/**/*.md`;
- `docs/features/**/*.md`.

It intentionally excludes `docs/reports/`, `docs/reviews/`, `docs/handoff/`, and `docs/history/`, where audit evidence and historical details belong.

## Boundary

This does not authorize any public performance claim. It only prevents the most dangerous diagnostic numbers from appearing in the wrong documentation surfaces.

