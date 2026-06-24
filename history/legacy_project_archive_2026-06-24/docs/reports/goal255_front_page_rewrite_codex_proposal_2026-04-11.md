# Goal 255 Codex Proposal: Front Page Rewrite (2026-04-11)

## Diagnosis

The current front page is not wrong, but it is overloaded.

Main problems:

- too much version-layer explanation too early
- too much historical/research framing before the first practical action
- the strongest beginner path exists, but it is buried under release-layer prose
- the visual demo is honest, but the page spends too long defending that boundary
  instead of simply showing what RTDL is and how to start

## Proposed Direction

The front page should have six short sections, in this order:

1. **One-screen identity**
   - one-sentence definition
   - one-sentence honesty boundary
   - one compact list of what RTDL is good for

2. **Start in 2 Minutes**
   - clone
   - install
   - first hello-world run
   - one released workload run

3. **Choose Your Path**
   - quick tutorial
   - released workloads
   - nearest-neighbor line
   - visual demo/video

4. **What RTDL Contains**
   - language core
   - built-in workload primitives
   - backend runtimes
   - RTDL-plus-Python application layer

5. **Current Release State**
   - `v0.4.0` release anchor
   - `v0.2.0` stable released workload family
   - `v0.3.0` demo/application proof layer
   - `v0.4.0` nearest-neighbor expansion

6. **Research Context**
   - short RayJoin note
   - link out to docs, not full narrative on the front page

## Style Proposal

- remove table-based layout from the hero area
- keep the video thumbnail, but move it under a clean “See It” section
- shorten bullets
- use fewer nested concepts
- keep the first screen optimized for:
  - what RTDL is
  - how to run it
  - where to go next

## Guardrails

- do not call RTDL a renderer
- do not hide the release structure, but compress it
- do not make backend promises on the front page beyond the release docs
- do not push users into archive/history material from the front door
