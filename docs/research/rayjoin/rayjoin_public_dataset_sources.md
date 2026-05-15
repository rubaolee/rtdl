# RayJoin Public Dataset Sources

This file summarizes the current public-source picture for the RayJoin-style
dataset families used in RTDL.

## Main Families

U.S. families:

- `County`
- `Zipcode`
- `BlockGroup`
- `WaterBodies`

Lakes / parks families:

- `LKAU`
- `PKAU`

## Source Strategy

Current source strategy is:

- use public-source acquisition where possible
- stage raw source data
- convert into RTDL-ready logical inputs
- keep bounded exact-source slices explicit when whole-family execution is not
  yet the accepted path

## Current Position

The repo now has real executed evidence for multiple exact-source families.
That means this file should be read as a current acquisition summary, not as a
speculative future-source list.

## Boundary

This file is the short public-source summary.

Use reports and accepted goal artifacts for:

- exact staging commands
- host-specific execution details
- accepted experiment outputs
