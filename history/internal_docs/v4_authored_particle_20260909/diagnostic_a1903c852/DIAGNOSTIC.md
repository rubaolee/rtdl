# Authored Particle diagnostic at `a1903c852`

Status: retained adverse exploratory diagnostic. This is not a preregistered
transaction and authorizes no public performance claim.

## Identity and task

- Source commit: `a1903c85212f5c6cc58e8d3cb90eb82ccb519818`
- Source tree: `0645b931218a9d98c7196bc71fa3285693fd7126`
- GPU: NVIDIA RTX 4000 Ada Generation, CC 8.9
- GPU UUID: `GPU-2a00572b-6cef-b9e6-db0a-c127783a5d46`
- Driver: 550.127.05
- Input identity: `c6678099ecff9581726781a765213d5b0890f20ada70561b09dd6dd94a4009af`
- Task: 5,000 real Particle queries over 3,392,530 triangles
- Required output: complete `5000 x 3` little-endian U32 rows

The RTDL arm used the public source-to-GPU lifecycle and its public prepared
query-batch API. The PyOptiX arm used the public handwritten precompiled-PTX
owner's complete SoA API. Both timers included execute, synchronization,
device-status checks, complete output return, and exact NumPy oracle comparison.
Detailed evidence-object expansion occurred after the final timed sample.

## Result

| Arm | Samples | Median (ns) | Min (ns) | Max (ns) |
| --- | ---: | ---: | ---: | ---: |
| Public authored RTDL | 20 | 421,489 | 407,874 | 442,825 |
| Public PyOptiX complete SoA | 20 | 342,036 | 331,351 | 369,173 |

The ratio of arm medians was `1.2322942614x`, above the engineering target of
`1.20x`. Both arms returned output SHA-256
`452ec9df2d8ee3c3a274dcbe4e175df305380f25793472e05da448e9556ed73b`.
RTDL also reported `optix_traversal_observed` and role counters
`[0, 5000, 0, 0, 5000, 0, 5000]`.

## Follow-up profiling

An unpreregistered same-process decomposition was run after this comparison.
It is retained only to select engineering work; its aggregate values are in
`PROFILE_SUMMARY.json`. It localized about 41.5 microseconds to the public
facade's duplicate output digest and negligible time to compact-receipt
rebinding. More importantly, the competent PyOptiX implementation already has
a stronger public prevalidated exact-core endpoint. That endpoint measured
about 218 microseconds in the diagnostic, versus about 343 microseconds for the
RTDL internal prepared owner. Therefore the next comparison must use the
stronger baseline; removing facade hashing alone would not close the real gap.

The native RTDL owner currently deinterleaves every admitted query batch into
seven fresh host vectors and performs seven execute-time query uploads. A
generic owner-bound device-resident prepared query batch is the next bounded
repair. It must not contain Particle semantics, weaken status-before-output,
or change the full-output contract.

## File hashes

| File | SHA-256 |
| --- | --- |
| `RTDL_DIAGNOSTIC.json` | `688913d9eb15f6157ca9c0421a0b50ad9ca0b0bcf9669270f22394192775476d` |
| `PYOPTIX_DIAGNOSTIC.json` | `f571ca9692081c08e2f3b0f09a5479de5f16ac766e6641583f975491de47e3c0` |
