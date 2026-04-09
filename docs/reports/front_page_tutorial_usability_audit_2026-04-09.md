# Front Page And Tutorial Usability Audit

Date: 2026-04-09

## Goal

Check the live front-page and tutorial surfaces against three practical
questions:

1. do they clearly state what RTDL can be used for?
2. do they give users easy instructions to use RTDL?
3. do they present RTDL in a useful and attractive way rather than as a dry
   archive dump?

## Files Audited

- `README.md`
- `docs/quick_tutorial.md`
- `docs/v0_2_user_guide.md`

## Main Weaknesses Found Before Editing

- the front page was honest, but it did not answer "what can I use this for?"
  fast enough
- the front page linked to deeper materials, but did not give a short
  first-run path near the top
- the quick tutorial explained RTDL well once already inside the docs, but it
  did not open with the fastest first successful command
- the user guide had practical content, but the first-run path was still too
  buried
- some stale absolute-path links remained in the docs

## Edits Applied

### Front Page

- added an early "RTDL is useful when..." section with concrete use cases
- added an early public front door block:
  - public video
  - quick tutorial
  - user guide
  - release-facing examples
- added a "Start Fast" section with repository-root commands
- kept the v0.2.0 workload surface and v0.3 demo line clearly separated

### Quick Tutorial

- added a "Fastest First Run" section before the deeper explanation
- made the first successful command explicit
- added a short "If You Only Remember Three Things" close
- replaced stale absolute links with repo-relative links

### User Guide

- added a short easiest-path quick-start preface
- made the first two commands explicit near the top of the quick-start area
- replaced remaining stale absolute links with repo-relative links

## Resulting Answers

### 1. Does the front page clearly state what RTDL can be used for?

Yes, materially better than before.

The front page now names both:

- released workload uses:
  - segment/polygon hitcount
  - segment/polygon any-hit rows
  - bounded polygon-set similarity
- application-style use:
  - Python applications that need a geometric-query core

### 2. Does the tutorial give users easy instructions?

Yes, materially better than before.

The shortest first-run path now appears immediately:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world.py
```

Then it gives two concrete next commands and points readers to the
release-facing examples and feature homes.

### 3. Is the front page more attractive and useful?

Yes, within the constraints of a Markdown repo front page.

The page now behaves more like:

- a concise problem/fit statement
- a front door with a public demo
- a quick-start surface
- then a deeper architecture/release archive

It is still a technical README, not a marketing landing page, but it is now
more inviting and easier to navigate.

## Boundaries

- this edit round improves clarity and approachability
- it does not redesign the entire docs tree
- it does not replace the broader release and archive materials
- it does not change the underlying RTDL scope claims

## Closure Standard

This round should only be called done if:

- Claude review agrees the three questions are materially addressed
- Gemini review agrees the three questions are materially addressed
- Codex review agrees the three questions are materially addressed
