# V4 Universe Audit Snapshot

Date: 2026-06-27

Status: `pass`

## Counts

- tracked files: `28343`
- untracked files: `0`
- public current files scanned: `31`

## Tracked Buckets

- `audit_provenance`: `1839`
- `current_code_or_gate`: `4356`
- `history_archive`: `22046`
- `other_tracked`: `71`
- `public_current`: `31`

## Tracked Documentation Buckets

- `audit_provenance`: `1201`
- `current_code_or_gate`: `4`
- `history_archive`: `14343`
- `other_tracked`: `7`
- `public_current`: `19`

## Tracked Code Buckets

- `audit_provenance`: `13`
- `current_code_or_gate`: `4333`
- `history_archive`: `328`
- `other_tracked`: `62`
- `public_current`: `12`

## Public Surface Findings

- none

## Untracked Buckets


## Untracked Samples


## Interpretation

Public V4 current surface must be clean. history/ is archival. future/ is audit provenance. Known untracked raw evidence, review working records, and local debris are not public V4 files. Use --strict-release before a final tag/package gate to require a debris-free local tree.
