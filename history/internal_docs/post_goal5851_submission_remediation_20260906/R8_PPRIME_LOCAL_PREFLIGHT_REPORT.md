# R8 P-Prime Local Preflight Report

Date: 2026-09-06 America/New_York.

Status: `LOCAL_PPRIME_PREFLIGHT_PASSED__R7_AND_EXTERNAL_ACTIONS_PENDING`.

This report repeats the local checks invalidated by changing old-P PDF and
source bytes. It does not close R8, count as an independent anonymity review,
or represent an upload or submission.

## Exact candidate

- P-prime commit: `818c2ed284cde8acae9a09b531b8bfed3bf925ee`.
- P-prime tree: `59e6eaacadac711f8b0d93980b1bfbbd3d772dc7`.
- PDF: 140,343 bytes, SHA-256
  `9bce71368ff0398efbc0d24685a80939fc691288663074ebf72ec9b20619013b`.
- Artifact: 180,308 bytes, unchanged SHA-256
  `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8`.
- Source bundle: 20,699 bytes, SHA-256
  `1d76d60b1f72487a414ef2fe649415938bc12a3ea6baedd65396b9378b4d90ed`.

## PDF checks

- Eight pages, US Letter, anonymous `acmart` `sigplan,screen,review,anonymous`.
- Main text ends on page 7; references occupy page 8.
- Page numbers and review line numbers are visible.
- All eight exact pages were rendered and visually inspected with no clipping,
  overlap, missing glyph, unreadable table, or color-dependent content.
- Build log: zero overfull boxes, zero unresolved citations/references, zero
  BibTeX warnings, and zero ACM-class warnings.
- All 12 listed fonts are embedded and have Unicode mappings.
- Metadata and extracted text contain no tested private identity, local path,
  pod/SSH endpoint, internal Goal identifier, private commit, or author
  repository identity.
- The PDF is not tagged. No PDF/UA or complete assistive-technology
  certification is claimed.

The same-day official-rule check recorded by the old-P R8 report remains the
format authority: standard papers allow at most 11 text pages excluding
references and require Letter paper, the ACM SIGPLAN format, anonymity, page
numbers, and review line numbers. P-prime remains within that checked envelope.

## Source bundle

The source bundle contains only:

```text
rtdl-cgo2027-source/paper/cgo2027/main.tex
rtdl-cgo2027-source/paper/cgo2027/references.bib
```

Two separately staged builds used directories mode 0755, files mode 0644,
uid/gid and owner/group normalized to zero/empty, and mtime 2000-01-01. The
resulting archives were byte-identical. Extraction under a foreign path
containing spaces preserved both source hashes. Tectonic returned exit 0 and
produced an eight-page Letter PDF. Time-dependent generated PDF bytes are not
substituted for the exact candidate PDF.

## Evidence artifact and tests

The artifact remains byte-identical to F2 and old P. Two fresh extraction
roots each passed isolated normal and `-O` replay. All four output files were
byte-identical at SHA-256
`c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8`.
The frozen submission-evidence suite passed 14/14 normally and 14/14 under
`-O`. No GPU execution or project import occurred in these recounts.

## Open R8 gates

- P-prime has zero of two required independent R7 final-byte approvals and
  zero independent P-prime anonymity scans.
- Authenticated author, topic, conflict, and form fields have not been checked.
- No upload has occurred; no downloaded-upload hash comparison exists.
- No submission receipt exists.
- Every public/manuscript claim authorization remains false.

Accordingly, local preflight passes but R8 remains open and the work is not
submitted.
