# Double-blind gate

Status: **SUPERSEDED PRELIMINARY SNAPSHOT; DOES NOT CERTIFY CURRENT BYTES.**
This file binds an earlier seven-page PDF and seven-member artifact. The current
eight-page PDF and eight-member artifact require a new independent final-byte
gate after content freeze. Historical observation below is retained rather
than silently rewritten.

Historical status: manuscript/PDF gate passed; compact anonymous scientific artifact
constructed, verified, and scanned. Assignment of an anonymous artifact URL
and a final packaged rerun source review remain required before submission.

## Required source properties

- [x] `acmart` `sigplan,screen,review,anonymous` submission mode
- [x] anonymous author and institution only
- [x] no owner name or username
- [x] no local Windows/Linux path
- [x] no POD endpoint, private IP, or host nickname
- [x] no internal Goal identifiers or evidence filenames in `main.tex`
- [x] no acknowledgement or funding text
- [x] no self-identifying repository URL
- [x] system name used as a research artifact name, not linked to identity
- [ ] anonymous artifact URL assigned
- [x] PDF metadata inspected: anonymous title only; no author, owner, host or path
- [x] generated `.aux`, `.bbl` and `.out` scanned; the local-only `.log` contains
  MiKTeX installation paths and is explicitly excluded from any review package
- [x] all seven rendered PDF pages visually inspected for clipping, overlap,
  malformed tables, accidental identifiers and anonymous running heads
- [x] artifact filenames and file contents scanned for identity, internal Goal
  ids, local paths, host/IP/port data, and reviewer/owner names
- [ ] final diff reviewed for deanonymizing self-citations

## Current PDF observation

The anonymous review PDF is seven letter-size pages after the formalism,
worked example, claim-map, related-work table, and artifact section rebuild. It
has no PDF Author field,
contains no internal Goal id, local path, host/IP/port, reviewer name, owner
name, acknowledgement, funding statement or self-identifying URL, and uses the
CGO 2027 conference/date/location metadata. The visible `Anonymous Author(s)`
string is intentional. Build logs are not submission artifacts.

The current three-arm PDF SHA-256 is
`d850580ab3d4c9d38c6983c6bb4227a9017087e683cd288d9f9ae73282e6e37e`.
All seven pages were re-rendered after the three-arm integration and visually
inspected; the 18-value performance table is legible and not clipped.

## Compact artifact observation

The anonymous artifact contains only scientific projections and a
standard-library verifier. Its manifest covers seven payload files. The
verifier passes the 19-leaf, five-residual, SQL-reuse, and three-arm performance
recounts, including 324 workers, 7,128 registered timings, and all 18
same-target comparison rows. The compact
artifact is explicitly an evidence/recount package, not a full GPU rerun or
production SDK.

## Forbidden artifact material

The reviewer-facing artifact must not copy the identifying internal archive.
Exclude internal goal numbering, external-review names, owner directives, local
user paths, host/IP/port data, credentials, private keys, Git remotes carrying
identity, and immutable logs that reveal those fields. Scientific arrays,
program bytes, anonymous manifests, validators, aggregate results, and bounded
reproduction scripts must be exported into a separately constructed anonymous
artifact.
