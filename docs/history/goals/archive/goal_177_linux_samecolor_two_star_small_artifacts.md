# Goal 177: Linux Same-Color Two-Star Small Artifacts

## Objective

Produce small, compare-clean Linux GIF artifacts for the synchronized two-star
variant of the orbiting-star 3D demo, with both stars using the same warm
yellow family and a fully symmetric equator flight path.

## Accepted Scope

- keep the Linux host as the execution platform:
  - `lestat@192.168.1.20`
- keep both stars synchronized in time
- keep both stars in the same warm yellow family
- make both stars fly horizontally on the equator
- keep them mirrored left/right across the clip
- save small copied-back artifacts for:
  - `optix`
  - `vulkan`
- require frame `0` compare parity against `cpu_python_reference`

## Out of Scope

- restarting or replacing the Windows 4K movie path
- large Linux GPU movies
- strong Linux GPU performance claims
- changing the RTDL/Python honesty boundary

## Success Criteria

- the synchronized same-color scene is implemented and locally verified
- the symmetric equator pass is implemented and locally verified
- Linux OptiX small GIF artifact is copied back with compare-clean frame `0`
- Linux Vulkan small GIF artifact is copied back with compare-clean frame `0`
- the goal package records the change honestly as a small supporting-artifact
  follow-up, not a new flagship movie
