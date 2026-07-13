# Goal5492 LibRTS Exact Archive Operation Inventory

## Status

```text
verified_archive_operation_inventory_complete__review_pending
```

The verified official `PPoPPAE-v2.tar.gz` archive was scanned without full
extraction. The audit classified operation query members and paired them with
same-basename geometry members. It did not treat scripts, logs, or paper PDFs
as executable input evidence.

## Inventory result

```text
regular file members: 1370
geometry members: 10
query members: 70
exact point-contains pairs: 14
exact range-contains pairs: 14
exact range-intersects pairs: 42
exact PIP pairs: 0
exact mutation pairs: 0
```

The archive therefore supports further exact range gates. It does not provide
an exact PIP or mutation input pair suitable for this line. The PIP keyword
hits are source/scripts/logs, not geometry/query pairs, and are not promoted.

## Decision

Proceed with one exact range-contains gate first. Keep range-intersects as a
separate next operation. Fail-close PIP and mutation paper-app claims on this
archive rather than inventing or substituting inputs.

## Claim boundary

This inventory does not reproduce a figure, establish author performance, or
claim full paper reproduction. Embree remains excluded.

## Evidence

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5492_exact_archive_operation_inventory.json
```
