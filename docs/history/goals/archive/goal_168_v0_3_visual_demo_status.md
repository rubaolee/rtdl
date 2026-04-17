# Goal 168: v0.3 Visual Demo Status Package

## Why

After Goal 167 and the smoother `softvis` follow-up artifact, the repository
needs one current-status package that says clearly:

- what the v0.3 visual-demo line has already proven
- which backends are already closed for the underlying 3D RTDL query surface
- which artifact is the current recommended public demo
- what remains a target rather than a finished performance story

Without that package, the repo still reads too much like:

- released v0.2 docs only
- plus scattered visual-demo goal history

## Goal

Write one consistent repo-accurate status package for the current v0.3 visual
demo line and align the main front-door/status docs with it.

## Scope

This goal covers:

- a single current-status summary for the v0.3 visual-demo line
- alignment of top-level status docs with the current demo reality
- explicit statement that the polished public artifact is currently the Windows
  Embree `softvis` MP4
- explicit statement that the underlying bounded 3D RTDL ray/triangle demo path
  is already closed across:
  - `embree`
  - `optix`
  - `vulkan`
  on Linux

This goal does not claim:

- that the polished public movie already runs equally well on all three
  backends
- that RTDL is now a general rendering engine
- that the Python-side visual path is fully optimized

## Acceptance

- the repo has one clear v0.3 visual-demo status file
- top-level status docs reflect the same current story
- focused demo tests still pass
- Claude review is saved
- Gemini review is saved
- Codex consensus is saved
