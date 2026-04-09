# Goal 185: Orbit Support-Star Stability Candidate

## Why

The moving-star orbit concept is still the most intuitive visual story in the `v0.3` demo line:

- fixed camera
- a bright star flies over the Earth
- visible lighting change follows the star's motion

Its main weakness is the left-bottom temporal blinking. This goal tests a more cinematic repair that keeps the moving-star concept alive:

- one hero moving star remains the main visible subject
- one smaller support star briefly lights the left-bottom danger zone early in the shot
- the support star fades out after the hero star takes over

## Scope

- package the current moving-star support-star composition as an explicit candidate
- keep the orbit-camera framing fixed
- generate a Windows Embree HD movie candidate
- keep the Linux OptiX and Vulkan versions runnable for bounded backend validation
- preserve the RTDL/Python honesty boundary:
  - RTDL owns the geometric-query core
  - Python owns animation, light choreography, shading, blending, and media output

## Success Criteria

- the support-star orbit composition is documented explicitly
- the Windows HD render completes and is copied back for review
- the candidate can be compared directly against the smooth-camera movie set
- Linux `optix` and `vulkan` paths remain runnable for this composition

## Out of Scope

- claiming the blinking problem is fully solved before visual review
- replacing the smooth-camera line by assumption
- changing RTDL backend semantics
