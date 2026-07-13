# Goal4846 Dataset Inventory - RayJoin Section 5.2 LSI

Date: 2026-07-01

POD:

```text
ssh root@157.157.221.29 -p 23132 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Environment gates:

| Item | Status |
|---|---|
| AuthorPatch `query_exec` | present |
| RTDL source tree | present |
| RTDL OptiX library | present |

## CDB Inventory

| # | Pair | Left exists | Left bytes | Right exists | Right bytes | Status |
|---:|---|---|---:|---|---:|---|
| 1 | County x Zipcode | yes | 904,529,353 | yes | 2,603,929,396 | completed by Goal4845 on current same-source CDB path |
| 2 | Block x Water | yes | 3,146,767,020 | yes | 2,402,941,772 | ready for Goal4846 on current same-source/regenerated CDB path |
| 3 | LKAF x PKAF | no | - | no | - | missing exact input |
| 4 | LKAS x PKAS | no | - | no | - | missing exact input |
| 5 | LKAU x PKAU | no | - | no | - | missing exact input |
| 6 | LKEU x PKEU | no | - | no | - | missing exact input |
| 7 | LKNA x PKNA | no | - | no | - | missing exact input |
| 8 | LKSA x PKSA | no | - | no | - | missing exact input |

## Immediate Consequence

Current POD can support a serious Section 5.2 LSI reproduction on **2/8 currently available CDB pairs**:

1. County x Zipcode - already completed for LSI correctness.
2. Block x Water - next.

The other six cannot be run as exact paper-input reproduction from the current POD state. They must remain `missing_exact_input` unless exact CDBs are found elsewhere.

Important correction: the old Goal4380 path `/workspace/rayjoin_section57_data/cdb_topology` is not present on the current POD. The available County/Zipcode and Block/Water paths are current same-source/regenerated artifact paths, not the old Goal4380 exact-root path. Do not call regenerated data exact paper input.

An all-`/workspace` search for the six lakes/parks CDB filenames returned no matches on 2026-07-01.

## Next Action

Run Block x Water:

- AuthorPatch `query_exec -query=lsi -mode=rt`;
- RTDL OptiX LSI count under the same direction and parameters;
- compare counts before interpreting timing.
