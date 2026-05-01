# Goal1087 Robot Chunked Runner Resume Update

Date: 2026-04-29

## Status

Implemented.

## Change

Updated the Goal1085 robot chunked Embree baseline runner generator so the
heavy 180-chunk baseline can be executed incrementally on Linux/Windows without
restarting completed chunks.

The regenerated runner supports:

- `RTDL_GOAL1085_START_CHUNK`, default `0`
- `RTDL_GOAL1085_END_CHUNK`, default `179`
- `RTDL_GOAL1085_SKIP_EXISTING`, default `1`

The generated shell runner validates the chunk range, skips existing non-empty
chunk files when requested, and still writes artifacts under
`docs/reports/goal1085_robot_chunked_embree_baseline/chunk_${chunk_index}.json`.

## Reason

The 36M-pose same-total-work Embree baseline may take a long time and should be
safe to run in multiple sessions or across a subset of chunks. This update
reduces operational risk before running it on a strong non-cloud host.

## Boundary

Goal1087 changes execution ergonomics only. It does not run the heavy baseline,
does not authorize release, does not change public wording, and does not
authorize public RTX speedup claims.
