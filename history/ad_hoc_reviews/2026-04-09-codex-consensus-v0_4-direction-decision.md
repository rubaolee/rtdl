# Codex Consensus: v0.4 Direction Decision

Status: closed after Claude and Gemini review

## Codex position

- `v0.4` should not be demo-first
- `v0.4` should not be backend-only
- the strongest next milestone is a workload-language-first release that turns
  bounded 3D proof work into explicit non-graphical public workload surface

## What Gemini changed

Gemini did not overturn the recommendation, but it made the required scope much
sharper:

- `v0.4` cannot stop at generic 3D ray visibility language
- `v0.4` needs at least one real 3D spatial-data workload, not just promoted
  demo mechanics
- the hidden-star demo must become background evidence, not the center of the
  milestone
- backend maturity debt must stay visible; broadening 3D surface without honest
  backend boundaries would weaken RTDL's credibility

## Updated Codex conclusion

The right `v0.4` direction is:

- **bounded 3D geometric-query release**

But the concrete acceptance target should be tightened to:

- one first-class 3D spatial-data workload with a credible non-graphical user
  story
- one non-demo example chain that teaches that workload directly
- explicit backend acceptance boundaries and performance/non-performance claims

## What Claude changed

Claude agreed with the direction but identified the remaining non-actionable
gap:

- the package still had not chosen the concrete first target

Claude's strongest useful corrections were:

- formalize `ray_tri_hitcount_3d` first as a public substrate feature
- do not pretend that this alone is enough to define `v0.4`
- choose one real non-graphical workload for release identity
- remove Hausdorff-adjacent work from `v0.4` headline scope
- treat the non-demo 3D example as a release-entry requirement

## Final Codex conclusion

The settled `v0.4` package is:

- first substrate feature to formalize:
  - `ray_tri_hitcount_3d`
- headline release workload:
  - `point_in_volume`

This preserves the original recommendation while making it actionable and
honest.

The wrong `v0.4` directions remain:

- prettier or more numerous public demos
- backend refactoring without new public semantics
- vague 3D support claims without a concrete non-graphical workload anchor
