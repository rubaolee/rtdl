# Goal 175: Two-Star 4K Variant

## Objective

Build the next bounded `v0.3` 4K movie variant by extending the accepted
Windows Embree orbiting-star scene from one main yellow star to two stars:

- the current yellow star remains the primary diagonal sweep
- a brighter red star is added as a delayed secondary accent
- the red star moves horizontally from left to right

## Accepted Scope

- implement the two-light scene in the Python demo layer
- keep RTDL as the geometric-query core
- add focused tests for:
  - delayed secondary-light activation
  - left-to-right secondary-light motion
  - two-light summary metadata
- generate a bounded preview before the Windows 4K run
- obtain external AI review before calling the goal closed

## Out of Scope

- changing RTDL backend semantics
- claiming the new movie is fully polished before it exists
- replacing the accepted Goal 173 artifact yet

## Success Criteria

- the new two-light logic is implemented and tested
- a preview run confirms the delayed red star becomes active later in the clip
- external review is saved
- then the Windows 4K run can proceed as the goal’s artifact step
